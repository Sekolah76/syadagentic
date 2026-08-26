# SPA / SaaS API Recon Playbook (class-level)

Condensed from live CoreSR (`coresr.ai`, 2026-07-18) and prior SPA hunts. Pure Web2 SaaS — no Web3 pivot required.

## When to use

- Target is React/Vue/Vite SPA (all paths same HTML size)
- Auth + multi-tenant workspaces/projects
- Admin surface only visible in JS chunks
- Goal: map API, auth gates, IDOR, info disclosure, session/CSRF

## Pipeline (order matters)

### 1. Fingerprint + SPA fallback gate

```bash
curl -sk -I "https://target/"
# identical size across paths → SPA fallback; stop path fuzz as “exists”
for p in / /admin /api /login /dashboard /.env /robots.txt; do
  curl -sk -o /tmp/b -w "$p %{http_code} %{size_download}\n" "https://target$p"
done
```

If sizes identical → **do not** treat 200 as real route. Pivot to JS/API.

### 2. Asset harvest (curl, not python urllib)

Many SaaS block bare Python UA (`403`). Prefer:

```bash
mkdir -p /tmp/spa_assets
curl -sk "https://target/" | grep -oE '/assets/[^" ]+\.js' | sort -u > /tmp/spa_js.txt
while read a; do curl -sk "https://target$a" -o "/tmp/spa_assets/$(basename "$a")"; done < /tmp/spa_js.txt
# pull lazy chunks from index mapDeps
grep -oE 'assets/[A-Za-z0-9_.-]+\.js' /tmp/spa_assets/index-*.js | sort -u
```

Priority chunks: `Auth*`, `Admin*`, `SuperAdmin*`, `api-*`, `Share*`, `Account*`, `schema*`.

### 3. Endpoint extraction

```python
import re, os
js = "".join(open(f"/tmp/spa_assets/{f}", errors="ignore").read()
             for f in os.listdir("/tmp/spa_assets") if f.endswith(".js"))
apis = sorted(set(re.findall(r"/api/[A-Za-z0-9_./${}-]{1,120}", js)))
print("\n".join(apis))
```

Also hunt: `superadmin`, `isSuperAdmin`, `csrf`, `siteToken`, `credentials:\`include\``, share/join tokens.

### 4. Unauth matrix

| Probe | Why |
|-------|-----|
| `GET /api/status` `/health` `/ready` | Info disclosure (build, commits, node, uptime) |
| `GET /api/user/me` | Expect 401 |
| Admin/superadmin list from JS | Expect 401/403, not 200 |
| `OPTIONS` + CORS | Credentialed cross-origin? |
| Security headers | HSTS, CSP, `X-Frame-Options`, cookie flags |

**CoreSR F1 pattern:** public `/api/status` leaked `nodeVersion`, deploy hashes, **10 commit subjects**, internal GH actor — severity **LOW** unless secrets/PII.

### 5. Session + CSRF harness

```bash
CJ=/tmp/spa_cj
curl -sk -c $CJ -b $CJ -o /dev/null "https://target/api/health"
# csrf_token cookie; SPA also sends X-CSRF-Token on POST/PUT/PATCH/DELETE
```

Rules observed (CoreSR):

| Check | Pass signal | Fail/hard signal |
|-------|-------------|------------------|
| Missing CSRF on state change | — | `403 CSRF_INVALID` |
| Cookie `SameSite=Strict` + Secure | Cross-site CSRF hard | — |
| CSRF token absent on first jar | Some apps set on any GET | Prime `/api/health` or `/` first |

### 6. Auth surface checklist

```text
POST /api/user/register   {email, password}
POST /api/user/login
GET  /api/user/me
POST /api/user/forgot-password | reset-password
POST /api/user/change-email | change-password
POST /api/user/mfa/*
GET  /api/auth/google     → OAuth client_id (public by design)
```

**Broken auth signals (verify with live response):**

| Signal | Evidence needed | Severity gate |
|--------|-----------------|---------------|
| Email auto-verified at register | `emailVerifiedAt` non-null + `accountStatus: approved` without inbox | MEDIUM if gates features; else LOW |
| Register creates usable session immediately | workspace/project create works | depends on product |
| Change-email without password / step-up | `200` + pending verify + logout | LOW–MEDIUM (needs stolen session) |
| Rate-limit spillover | login 429 also blocks register | informational / DoS self |
| Mass-assign role on profile | role flips to admin | HIGH if works; often 404 |

### 7. Multi-tenant IDOR protocol

1. Create **own** workspace/project → capture UUID.
2. Probe foreign IDs: own UUID, random UUID, sequential ints, garbage.
3. Compare **status + body**, not status alone.

| Pattern | Meaning | Report? |
|---------|---------|---------|
| Own `200` + foreign `404` | Good existence hide | No |
| Own `200` + foreign `403` **same body for all foreign** | Authz OK; **no enum** | No (discard as IDOR) |
| Foreign `403` vs `404` **differs by existence** | ID/workspace enumeration | LOW–MEDIUM |
| Foreign `200` with other-tenant data | Classic IDOR | HIGH |
| Foreign `403` but body leaks name/email/role | Partial disclosure | MEDIUM |

**CoreSR:** `/api/workspaces/{any}` → uniform `{"error":"Not a member of this workspace"}` including invalid IDs → **not IDOR**, discard. Pending-invites returned role-flavored 403 for **all** IDs including garbage → still no existence oracle if uniform.

### 8. Privilege map (JS → live)

From SuperAdmin/Admin chunks, probe:

```text
/api/admin/users | metrics | activity | ai-services
/api/superadmin/check | dashboard | users | online-users
/api/superadmin/runpod-failover | glass-console/* | security-assessment
```

Expect: unauth `401`, user `403` + `{"isSuperAdmin":false}` on check.  
**Finding only if** user gets `200` admin data or can PATCH privilege.

### 9. Follow-on surfaces (after auth)

| Surface | Risk class |
|---------|------------|
| Invite/join tokens (`/workspaces/join/:t`, project-invitations) | Token guess / leak |
| Project shares role upgrade | Priv-esc |
| `cookies-txt` / institutional proxy URL | SSRF + secret store |
| AI/orchestrator chat + upload | Prompt injection / data exfil |
| Billing portal / checkout | Price / tier manipulation |

## Rate limit note

Aggressive login/register probes can IP-lock **all** auth endpoints (CoreSR: 30m `RATE_LIMITED` spillover). Use fresh cookie jars sparingly; prefer one authed session for IDOR matrix.

## Severity honesty (Web2 SaaS)

| Finding | Default severity | Elevate when |
|---------|------------------|--------------|
| Public status/build/commits | LOW | Secrets, internal URLs, PII, admin tokens |
| Email verify skipped | MEDIUM | Unlocks paid modules, admin approval, or trust of verified badge |
| Change-email no password | LOW–MEDIUM | Combined with XSS/session theft chain |
| Uniform 403 IDOR “feeling” | **None** | Only if body/status differs by existence or returns data |
| Admin route in JS only | Info | Live 200 as non-admin |

## Related skills

- `bug-bounty-methodology` — loop FIND→TEST→VALID
- `honest-bug-bounty-reporting` — no severity inflation
- `bug-bounty-methodology/references/spa-to-web3-recon-pivot.md` — only if contracts appear in JS
- `waf-bypass`, `race-condition-exploitation` — as needed
