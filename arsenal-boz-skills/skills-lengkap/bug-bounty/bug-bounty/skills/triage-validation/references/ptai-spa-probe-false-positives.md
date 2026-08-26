---
name: ptai-spa-probe-false-positives
description: When ptai reports 100+ open redirects from spa_probe, they are usually Next.js / Cloudflare internal routing chains — not real cross-domain redirects. Pattern + how to triage in <2 min.
---

# ptai `spa_probe` and Scanner False Positive Patterns

## Pattern 1: `spa_probe` Open Redirect Noise

When ptai engagement ends with **~120 findings, all categorized as `redirect`, all titled "Open Redirect via parameter [X]" with 12 different param names × 10 different endpoints** — this is almost always noise, not real open redirects.

Confirmed across multiple 2026-07 sessions:
- Cloudbet → 120 findings, all noise (Cloudflare internal routing chain)
- K2 Cloud → 120 findings, all noise (Next.js internal routing chain)

The pattern is consistent enough to use as a heuristic: **if ptai gives 100+ `redirect` findings from `spa_probe`, do NOT triage each one individually. Pick 2-3 samples and verify the cluster.**

### Why It Happens (spa_probe)
`spa_probe` brute-forces common redirect parameter names (`to`, `url`, `next`, `return`, `redirect`, etc.) against common redirect endpoint names. Many frameworks echo the param value inside a Location header that points to an internal path, e.g.:

```http
GET /redirect?to=https://evil.com HTTP/1.1

HTTP/2 301
Location: https://www.example.com/redirect?to=https://evil.com
```

The probe sees `evil.com` in the Location header → flags as open redirect. But the URL stays on `example.com`.

## Pattern 2: Next.js / Vercel Locale 307 Redirects (SQLi / SSTI False Positives)

When scanning a Next.js application hosted on Vercel (or similar frameworks with auto-locale resolution), ptai may report **Critical SQLi or SSTI** findings that are actually just harmless routing redirects.

**The Signal:**
- Finding claims SQLi or SSTI (e.g. "SQLi login bypass on /sessions", "SSTI on /rest/track-order")
- The PoC/reproduction shows a `307 Temporary Redirect` (or 308) to a locale-prefixed path (e.g., `/sessions` → `/en/sessions` or `/de/sessions`).
- Following the redirect leads to a `404 Not Found` or a normal page.

**Why It Happens (Locale 307s)**
The scanner sends a payload like `/sessions?id=1' OR 1=1--`. The Next.js router intervenes BEFORE any backend logic runs, noticing the user lacks a locale prefix. It issues a `307 Redirect` to `/en/sessions?id=1' OR 1=1--`. 

If the scanner's heuristic sees the payload reflected in the `Location` header or misinterprets the 307/404 timing/length difference as a successful boolean/time-based injection, it flags a Critical bug. But the payload never touched a database or template engine.

### How to Triage in <2 Minutes

Pick 3 representative findings (different endpoint, different param). For each:

```bash
# Test 1: External URL in param — does it actually leave the domain?
curl -sIL "https://TARGET/redirect?to=https://evil.com" 2>&1 | grep -iE 'location|http/'

# Test 2: javascript: scheme — does it execute?
curl -sIL "https://TARGET/redirect?to=javascript:alert(1)" 2>&1 | grep -iE 'location|http/'

# Test 3: Next.js Locale Check (for SQLi/SSTI false positives)
curl -sIL "https://TARGET/endpoint?payload=1" 2>&1 | head -15
# If you see HTTP/x 307/308 and Location: /en/endpoint?payload=1 → it's a router false positive.
```

**PASS conditions for a REAL open redirect:**
- `location:` header points to `https://evil.com/...` (not back to TARGET domain)
- Browser actually leaves TARGET domain
- javascript: and // schemes are not URL-encoded (still dangerous)

**FAIL conditions (ptai false positive):**
- `location:` points back to `https://www.TARGET/<same_path>?to=...`
- The canary URL stays URL-encoded inside an internal query string
- Following the redirect lands on TARGET or a 403/404, NOT on the canary host

If 2-3 samples all FAIL → kill the entire 120-finding batch as noise. Don't triage the other 117 individually.

## Why This Matters

- **Triaging 120 false positives one-by-one wastes 60-90 minutes** for $0 return
- Auto-verifier receipt contains `successes: 2, attempts: 2` — that is the probe's replay count, NOT independent verification. Don't mistake it for human review
- Per `triage-validation` skill: "Open redirect alone (no ATO or OAuth theft chain) → KILL IT"
- Most programs explicitly exclude open redirect with no security impact

## When NOT to Apply This Shortcut

Kill the shortcut if ANY of these are true:
- The probe found an OAuth `redirect_uri` param specifically (`redirect_uri=`, `oauth_callback=`, `state=`, `client_id=` + `redirect_uri`)
- The Location header actually points to an external domain (not just URL-encoded in the query string)
- The probe found a `<meta http-equiv="refresh" content="0;url=...">` tag reflection with attacker-controlled URL
- The program explicitly pays for open redirects (rare — almost never true)

In those cases, do individual triage on the few that look different.

## Related

- `triage-validation` SKILL.md → NEVER SUBMIT LIST: "Open redirect alone (no ATO or OAuth theft chain)"
- `triage-validation` SKILL.md → 7-Question Gate, Q6 impact proof
- `references/external-verification-pattern.md` → for high-stakes findings, run an LLM verifier
