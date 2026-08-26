# Credential Registry — Sumber Kebenaran Semua Akses

## Overview
File: `~/.hermes/hermes-agent/platform_access.json`

**NOTE:** This is the single source of truth for all platform configs, accounts, cron jobs, golden hours, and affiliate link tracking. Updated 2026-05-25 to consolidate all credential info.

## Platform Status (2026-05-25)
| Platform | Handle | Status | Access Method |
|----------|--------|--------|---------------|
| Twitter | @MyBiniGua | ✅ | browser_cookie3 from Chrome Profile 16 |
| Threads | @jagonya_shopee | ✅ | browser_cookie3 + uv (auto-refresh 6h) |
| Google | <MASKED_EMAIL> | ✅ | OAuth 2.0 auto-renew |
| Discord | @d4nnboz | ✅ | Token file API v10 |

## Cron Jobs
| ID | Name | Schedule |
|----|------|----------|
| 67a687f2978a | Threads Reply v3 | every 30m |
| 23199a7b2d5b | Threads Post v4 | 30 7,11,19 * * * |
| f1902736896e | Cookie Refresh | 0 */6 * * * |

## Files
- Discord token: `~/.hermes/discord_token.json`
- Google token: `~/.hermes/google_token.json`
- Instagram cookies: `/Users/user/instagram_cookies.json`
- Cookie extraction: `~/.hermes/scripts/extract_threads_cookies.py`
- OWL wallet: `~/.hermes/hermes-agent/owl-wallet.json`

## ⚠️ Twitter Login Notes (SOLVED 2026-05-25)
- **Same method as Threads** — user logs in manually in Chrome Profile 16, then extract via browser_cookie3
- Cookies extracted → saves to `/Users/user/twitter_cookies.json`
- **Bot detection:** Twitter blocks headless browser login. User MUST login manually in real Chrome Profile 16.
- Cookies file contains: `auth_token`, `ct0`, `twid` (all valid)

## Pitfalls
- Chrome CDP port 9222 does NOT bind on macOS → use browser_cookie3
- System Python 3.9 broken → use `uv run` for all cookie operations
- **Twitter blocks headless browser login** → user must login manually in Chrome Profile 16
- **"Postingan" = POST BARU (not reply)** — use this skill for original posts, `threads-auto-reply` for comments

## Bot Management (Operational)
When killing background bots:
1. Find PID: `ps aux | grep -i "bot_name" | grep -v grep`
2. Kill: `kill <PID>`
3. Disable launchd (if exists): `launchctl unload ~/Library/LaunchAgents/<plist>` then rename to `.disabled`
4. Verify: `ps aux | grep -i "bot_name"` should return empty
