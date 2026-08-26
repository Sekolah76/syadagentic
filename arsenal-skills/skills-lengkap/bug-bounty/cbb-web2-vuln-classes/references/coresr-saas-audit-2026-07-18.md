# Case study: CoreSR SaaS full-spectrum audit (2026-07-18)

**Target:** `https://coresr.ai`  
**Type:** Systematic-review / GRADE / NMA SaaS (pure Web2, not Web3)  
**Stack:** React+Vite SPA · Node v22 · Caddy · Cloudflare · Stripe live  
**Dev signal:** GH user `InvestmentMDideas` (from public `/api/status` commits)

## Confirmed findings

| ID | Finding | Severity | Because |
|----|---------|----------|---------|
| F1 | `GET /api/status` unauth | **LOW** | nodeVersion, uptime, build.hash, 10 commit subjects, org actor — no secrets |
| F2 | Register auto-verifies email | **MEDIUM** | 4/4 accounts: `emailVerifiedAt` set + `accountStatus:approved` + session; free modules usable |
| F4 | `GET /api/screening/fetcher/status` (auth) | **LOW–MED** | Tailscale CGNAT `100.93.126.104:5051`, `ftf-local-api`, auth=token, sweep metrics |
| F5 | Drizzle schema in client JS (~239KB) | **LOW** | 220 tables incl. password_hash, mfa_secret_enc, token tables |
| F7 | Upload `sessionId` = epoch ms | **INFO** | Predictable; cross-user GET → 403 |

## Retracted / discarded

| Claim | Why discarded |
|-------|----------------|
| F3 change-email no password | Retest: `password` required; empty/missing → 400/401 |
| Workspace IDOR | Uniform 403 body for all foreign IDs including garbage |
| Mass-assign admin on register | `role`/`isSuperAdmin` ignored → still user |
| SSRF via institutionalProxy | http/localhost/169.254 rejected; https public host only; no server-side fetch proof |
| Seat/project race | Parallel invites/projects all 403; counts hold |
| OAuth state forge | callback → `error=google_failed` |
| Unsigned Stripe webhook | `/api/billing/webhook` → 400 signature failed |
| Admin path traversal | `../admin/users` resolves but 403 Admin required |
| Cross-user upload session | A5→A2 sessionId → 403 |

## Hardened controls observed

- CSRF: missing token → `CSRF_INVALID` on mutating methods  
- Cookies: `auth_session` HttpOnly Secure Lax 7d; `site_auth_token` Strict; csrf Strict  
- Proxy validator: https + public hostname + `{url}` placeholder  
- API keys (scopus/wos): stored, readback masked `••••••`  
- Free limits: maxProjects=1, seat cap=1 — race-safe in test  
- Stripe: live checkout `team_monthly|annual`, `researcher_monthly`  
- HTML/SVG upload → 500 (not stored XSS proven)  
- Path fuzz / swagger / metrics → SPA HTML fallback  

## Second-order notes (not proven exploit)

1. Screening reference accepts `url=http://169.254.169.254/` in `rawData` — stored.  
2. `fetch-fulltexts` on free returned total=0 (no PDF stage). Retest when pipeline fetches user URLs.  
3. cookies.txt upload accepted (plain text) — fetcher second-order if used server-side.  
4. AI/GLASS/orchestrator gated (`TIER_REQUIRED` / 404) — retest Team tier.

## Minimal PoC

```bash
# F1
curl -sk https://coresr.ai/api/status | jq '{node:.process.nodeVersion,build:.build,n:(.recentDeploys|length)}'

# F2
# prime jar → CSRF → POST /api/user/register → jq '.user|{emailVerifiedAt,accountStatus,role}'

# F4 (authed jar)
curl -sk -b jar https://coresr.ai/api/screening/fetcher/status | jq .localFetcher
```

## Priority fixes (for disclosure)

1. F2 — set `emailVerifiedAt` only after inbox proof; gate features  
2. F4 — hide Tailscale URL / internal fetcher topology from normal users  
3. F1 — strip commit subjects / org from public status  
4. F5 — do not ship full ORM schema to client  
5. F7 — random UUID sessionId  
6. Defense: reject private IPs in stored reference URLs  

## Playbook used

`web2-bug-bounty-fundamental/references/spa-saas-api-recon.md` (updated with full-spectrum matrix from this audit).
