# Shopee Cookie Refresh — Profile 16 SQLite (2026-07-21)

**Cron:** `1140bbcb4773` · `Shopee — Cookie Refresh via SQLite` · `0 */6 * * *` · `no_agent`  
**Script:** `~/.hermes/scripts/refresh_shopee_cookies.py`  
**Outputs:** `~/shopee_cookies.json` (flat) · `~/shopee_cookies_full.json`  
**Watchdog topic:** COOKIES & SESSION (`t23`)

## Failure that bit production (00:01 WIB 2026-07-21)

| Symptom | Cause |
|---------|--------|
| C1: `script exit != 0` | Old path still **camoufox** CDP |
| stdout: `Extracting Shopee cookies via camoufox...` + `session_name=shp_c_ref_*` | Separate browser session, **not** Chrome Profile 16 |
| Message: session expired / belum login | False negative — P16 still had `SPC_U` + `SPC_ST` |

**Same class as AllScale 2026-07-15:** camoufox `chrome_local_*` ≠ visual Profile 16 login jar.

## Canonical path (MANDATORY)

1. Read **Chrome Profile 16** Cookies SQLite via `browser_cookie3` (Chrome 130+ `v10x`).
2. **Always** `shutil.copy2` DB → tempfile first (Chrome lock / concurrent write).
3. Domains: `shopee.co.id`, `.shopee.co.id`, `mall.*`, `seller.*`, `affiliate.*`.
4. Prefer buyer `.shopee.co.id` over `seller.*` when names collide (`SPC_SI`, `SPC_SEC_SI`).
5. Write flat + full JSON **before** any API verify gate.
6. **Auth gate (exit 0):** `SPC_U` non-empty and not `0`/`-` **and** `SPC_ST` len ≥ 15.
7. API verify is **best-effort only** — soft-saved exit 0 if auth markers present.

## Soft-success rule (anti C1 spam)

| Condition | Exit | Cron status |
|-----------|------|-------------|
| Auth markers OK + API profile 200 | 0 | ok · Online |
| Auth markers OK + API `error 19` / bot wall / 403 | 0 | ok · Soft-saved |
| No `SPC_U`/`SPC_ST` / empty jar | 1 | error · Expired |
| Cookies DB missing / decrypt fail | 1 | error |

Live probe 2026-07-21:
- `SPC_U=10133050829`, `SPC_ST` len 261, 22 cookies
- `get_account_info` / `get_profile` → HTTP 200 body `error: 19 Failed to authenticate` (bot wall)
- **Not** expired — soft-saved exit 0 after fix

## Auth vs noise

| Keep as auth | Noise (never sole success) |
|--------------|----------------------------|
| `SPC_U`, `SPC_ST`, `SPC_SI`, `SPC_F`, `SPC_CLIENTID`, `SPC_T_*`, `SPC_R_T_*` | `_ga*`, `_fbp`, `_gcl_au`, `language`, `ssr-tz` |
| Prefer buyer domain values | Seller-only `SPC_SEC_SI` lower score |

Missing `csrftoken` is common in P16 jar — do not fail solely on that.

## Anti-patterns

- ❌ camoufox / CDP `chrome_local_*` for Shopee cookie refresh
- ❌ exit 1 when API returns error 19 but `SPC_ST` long
- ❌ reading Cookies DB without tempfile copy under live Chrome
- ❌ treating homepage 403 / bot wall as “login dead”

## Manual verify

```bash
/usr/bin/env python3 ~/.hermes/scripts/refresh_shopee_cookies.py; echo EXIT:$?
# expect EXIT:0 and Soft-saved or Online
python3 -c "import json;d=json.load(open('/Users/user/shopee_cookies.json'));print(d.get('SPC_U'), len(str(d.get('SPC_ST')or'')))"
```

## Cross-refs

- AllScale twin pattern: `allscale-automation` · `refresh_allscale_cookies.py` (browser_cookie3, not camoufox)
- Threads/IG verify endpoints: `references/cookie-refresh-verify-endpoints.md`
- Cron C1: `script exit != 0` → fix script soft-exit, not pause job blindly
