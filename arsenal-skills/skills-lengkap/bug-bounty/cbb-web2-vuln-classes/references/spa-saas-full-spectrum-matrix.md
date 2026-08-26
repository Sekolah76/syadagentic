# SPA/SaaS full-spectrum test matrix (post-auth)

Add-on to `spa-saas-api-recon.md`. Lessons from CoreSR full-spectrum 2026-07-18.
Full case: `coresr-saas-audit-2026-07-18.md`.

## Always run after authed session

| Surface | Probe | Pass (hardened) | Fail (finding) |
|---------|-------|-----------------|----------------|
| Email verify | register ×N | `emailVerifiedAt` null / gated | non-null + approved + usable |
| Change-email | with/without password | password required | no password works |
| Mass-assign | register/profile `role:admin` | ignored | role flips |
| Workspace IDOR | foreign UUID/int/garbage | uniform 403 body | 200 data or 403≠404 enum |
| Project IDOR | 2nd account | 403/404 | 200 |
| Upload session | epoch/guess + cross-user | 403 cross-user | 200 other user data |
| Seat race | parallel invites free | all 403, members=1 | >cap members |
| Project race | parallel create | count stays at limit | over-cap |
| Proxy SSRF | `http://127.0.0.1/{url}` | 400 reject private | accepts + server fetch |
| Proxy public | `https://x/{url}` | client-only | server hits URL |
| Fetcher status | GET screening/fetcher/status | no internal IP | Tailscale/RFC1918 URL |
| Billing checkout | priceKey team_monthly | live Stripe OK | free unlock without pay |
| Webhook | POST no signature | 400 sig fail | 200 grants tier |
| OAuth callback | forged code/state | error redirect | session issued |
| Admin path `../` | normalize | 403 | 200 admin data |
| Schema in JS | schema-*.js | n/a (LOW recon) | live secrets in bundle |
| AI/orchestrator | chat/runs | 404/TIER_REQUIRED | free prompt inject |

## Retract rules

1. First 200 can lie — retest with correct fields.
2. Uniform 403 ≠ IDOR.
3. Client proxy template ≠ SSRF without server fetch proof.
4. Scoreboard: Confirmed | Retracted | Hardened.
5. `Severity: X — because [live data]`.

## Pointers

- Pipeline: `spa-saas-api-recon.md`
- Case: `coresr-saas-audit-2026-07-18.md`
- Honest report: `honest-bug-bounty-reporting`