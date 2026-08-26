# Threads/IG Cookie Refresh — Verify Endpoints (2026-07-14)

Script: `~/.hermes/scripts/extract_threads_cookies.py`  
Cron: `f1902736896e` Threads — Cookie Refresh via SQLite (`0 */6 * * *`, no_agent)

## Failure mode that bit production

- Symptom: watchdog `script exit != 0`, message `Weak | verify user gagal: err:HTTP Error 302 ... infinite loop`
- Root cause: `who()` hit `https://www.instagram.com/api/v1/accounts/edit/web_form_data/`
- Reality: `sessionid` still valid; `web_profile_info` returned 200 + real `jagonya_shopee` data
- Fix: change verify endpoints; do not force re-login on 302 from the old form endpoint

## Working verify order

1. Require `sessionid` in IG cookies from Chrome Profile 16
2. `GET https://i.instagram.com/api/v1/users/{ds_user_id}/info/` with Cookie + `X-IG-App-ID` + CSRF → parse `"username"`
3. Fallback: `GET https://www.instagram.com/api/v1/users/web_profile_info/?username=jagonya_shopee`
4. Success only if username string returned without `err:` prefix → `sys.exit(0)`
5. Always write `~/instagram_cookies.json` + sanitized `~/threads_cookies.json` before exit

## Account sanitize rule

- Expected IG `ds_user_id`: `3310347890` (`@jagonya_shopee`)
- If Threads cookie `ds` ≠ IG `ds` → **DROP_FOREIGN_THREADS_MIRROR_IG** (mirror IG keys onto threads domains). Not a failure.
- Never inject foreign Threads session into production post/reply paths

## Headers minimum

```
User-Agent: Chrome desktop
Cookie: <full ig jar>
X-IG-App-ID: 936619743392459
X-CSRFToken: <csrftoken>
X-Requested-With: XMLHttpRequest
Referer: https://www.instagram.com/
```

## Sister job — Shopee cookie refresh (2026-07-21)

Same class of C1 failure as IG verify-endpoint false negatives:

| Job | Script | Rule |
|-----|--------|------|
| `f1902736896e` Threads | `extract_threads_cookies.py` | this file |
| `1140bbcb4773` Shopee | `refresh_shopee_cookies.py` | `references/shopee-cookie-refresh-sqlite.md` |

Shopee: **never** camoufox; auth gate = `SPC_U`+`SPC_ST`; API `error 19` → soft-exit 0.
