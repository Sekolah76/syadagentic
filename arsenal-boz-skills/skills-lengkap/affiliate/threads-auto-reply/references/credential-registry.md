# Credential Registry — Sumber Kebenaran Semua Akses

## Overview
File: `~/.hermes/hermes-agent/credential-registry.json`

## Platform Status (2026-05-27)
| Platform | Handle | Status | Access Method |
|----------|--------|--------|---------------|
| Threads | @jagonya_shopee | ✅ ACTIVE | browser_cookie3 + uv (auto-refresh 6h) |
| Discord | @d4nnboz | ✅ ACTIVE | Token file API v10 |
| Google | <MASKED_EMAIL> | ✅ ACTIVE | OAuth 2.0 auto-renew (refresh token valid) |
| GitHub | @demoproject-cmd | ✅ ACTIVE | ~/.git-credentials store |
| Twitter | @MyBiniGua | ✅ ACTIVE | CDP session refresh + GraphQL validation |

## Account Verification (2026-05-27)
```python
# How to check all accounts at once:
# 1. Discord: requests.get('https://discord.com/api/v10/users/@me', headers={'Authorization': token})
# 2. Threads: requests.get('https://i.instagram.com/api/v1/accounts/current_user/', headers={...cookies...})
# 3. Google: POST https://oauth2.googleapis.com/token with refresh_token → auto-renew
# 4. GitHub: Check ~/.git-credentials for stored credential
# 5. Twitter: requests.get('https://api.x.com/1.1/account/verify_credentials.json') with OAuth1
```

## Cron Jobs
| ID | Name | Schedule |
|----|------|----------|
| 67a687f2978a | Threads Reply v3 | every 30m |
| 23199a7b2d5b | Threads Post v4 | 30 7,11,19 * * * |
| f1902736896e | Cookie Refresh | 0 */6 * * * |

## Files
- Discord token: `~/.hermes/discord_token.json`
- Google token: `~/.hermes/google_token.json`
- Google credentials: `~/.hermes/google_credentials.json`
- Instagram cookies: `/Users/user/instagram_cookies.json`
- Twitter cookies: `/Users/user/twitter_cookies.json`
- Cookie extraction: `~/.hermes/scripts/extract_threads_cookies.py`
- OWL wallet: `~/.hermes/hermes-agent/owl-wallet.json`
- Platform access: `~/.hermes/hermes-agent/platform_access.json`

## ⚠️ Twitter Status (2026-05-27)
- **STATUS: ❌ EXPIRED** — All OAuth1 tokens and cookies returning 401
- **Symptoms:** `{"errors":[{"code":89,"message":"Invalid or expired token."}]}`
- **Fix:** User must login manually in Chrome Profile 16, then extract cookies
- **Primary method:** `browser_cookie3.chrome(domain_name=".x.com", cookie_file=path)`
- **Bot detection:** Twitter blocks headless browser login
- **Credential files:** `~/.hermes/twitter_credentials.json`, `~/.hermes/hermes-agent/platform_access.json`

## ⚠️ Google OAuth (2026-05-27)
- **STATUS: ✅ ACTIVE** — Access token expires every 3599s but refresh_token auto-renews
- **Refresh method:** POST to `https://oauth2.googleapis.com/token` with client_id + client_secret + refresh_token
- **Credential files:** `~/.hermes/google_credentials.json`, `~/.hermes/google_token.json`
- **Note:** Refresh token is permanent unless revoked

## ⚠️ Discord Token
- **STATUS: ✅ ACTIVE** — User token (not bot), API v10
- **Validation:** GET `https://discord.com/api/v10/users/@me` with Authorization header
- **Note:** Token permanent unless user revokes

## ⚠️ GitHub
- **STATUS: ✅ ACTIVE** — Git credential stored in `~/.git-credentials`
- **Username:** demoproject-cmd
- **Email:** <MASKED_EMAIL>
- **Note:** No gh CLI installed, uses git credential helper

## Pitfalls
- Chrome CDP port 9222 does NOT bind on macOS → use browser_cookie3
- System Python 3.9 broken → use `uv run` for cookie operations
- Twitter blocks headless browser login → user must login manually in Chrome Profile 16
- Twitter OAuth1 tokens expire → need to re-auth via Chrome cookies periodically
- Google access_token expires every ~1h → use refresh_token for auto-renew
- "Postingan" = POST BARU (not reply) — use threads-auto-post skill
