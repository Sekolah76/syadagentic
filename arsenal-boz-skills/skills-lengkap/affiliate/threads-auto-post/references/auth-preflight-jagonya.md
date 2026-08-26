# Auth Preflight — @jagonya_shopee (2026-07-12 → 2026-07-13)

Live post fails at **composer**, not story content, when session wrong/expired.

## Target account
- Handle: `@jagonya_shopee`
- IG user id: `3310347890`
- Profile: Chrome **Profile 16**

## Hard rule
`web_profile_info?username=jagonya_shopee` returning 200 ≠ **logged-in as jagonya**.
That endpoint can succeed with **any** valid IG cookie (or weak auth).

**Must verify identity of the active session**, not just "can read public profile".

## Cookie sources (ordered)
1. `~/instagram_cookies.json` — used by Playwright post
2. Chrome P16 cookie DB via `browser_cookie3` (copy DB first; Chrome locks file)
3. `~/threads_cookies.json` — optional native Threads cookies (often empty/stale)

## Multi-account trap
| Source | ds_user_id | Who |
|---|---|---|
| P16 main Cookies | `46398254032` | **olivia.vanesso** (active) |
| Cookie backup / old file | `3310347890` | **jagonya_shopee** (session can be expired) |
| P16 Threads cookies | `38122991886` | foreign Threads session — **DROP** if ≠ IG ds |

If Playwright injects **olivia** or foreign Threads session → onboarding / wrong account / Sign up wall / Kirim no-op.

## Sanitize rule (2026-07-13)
```text
if threads.ds != ig.ds → DROP threads session; mirror IG keys
EXPECTED_DS = 3310347890
```
Implemented in `~/.hermes/scripts/extract_threads_cookies.py`.

## Auth-dead signatures (2026-07-13 live)
| Symptom | Meaning |
|---|---|
| P16 JS cookie only `csrftoken+mid`, `sessionid` missing | Guest / logged out |
| UI "Lanjutkan dengan Instagram" | Not authed on Threads |
| Cookie file has `ds=3310347890` but home = "halaman ini memang hilang" | **Session expired** (ds alone ≠ valid) |
| `eds=0` after Buat click + login prompt | Stop publish path; re-login |

## Preflight checklist (before any live post)
```bash
# 1) cookie identity (NOT just profile fetch)
python3 - <<'PY'
import json,re,urllib.request
from pathlib import Path
c=json.loads(Path.home().joinpath('instagram_cookies.json').read_text())
assert c.get('ds_user_id')=='3310347890', f"WRONG ACCOUNT ds={c.get('ds_user_id')} need 3310347890"
cookie='; '.join(f'{k}={v}' for k,v in c.items())
req=urllib.request.Request(
  'https://www.instagram.com/api/v1/accounts/edit/web_form_data/',
  headers={
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Cookie':cookie,'X-IG-App-ID':'936619743392459','X-CSRFToken':c.get('csrftoken',''),
    'X-Requested-With':'XMLHttpRequest','Referer':'https://www.instagram.com/',
  })
body=urllib.request.urlopen(req,timeout=15).read().decode()
m=re.search(r'"username"\s*:\s*"([^"]+)"', body)
assert m and m.group(1)=='jagonya_shopee', f"session user={m.group(1) if m else None}"
print('OK jagonya session')
PY
```

Also check **live P16 UI**: feed + "Apa yang baru?" / composer — not guest.

Fail modes:
- redirect / login chooser text (`olivia.vanesso`, `Use another profile`) → **expired**
- username ≠ `jagonya_shopee` → **wrong account** → STOP, do not post
- home broken-link page after cookie inject → **session dead** even if ds matches

## Playwright cookie inject (keep simple)
- Inject IG cookies to **`.instagram.com` only** (still correct for SSO path)
- Navigate `instagram.com` → must NOT show password field / multi-account chooser
- Then `threads.com/login` → click `Continue with Instagram` / `Lanjutkan dengan Instagram`
- After SSO, home must NOT show `Sign up to post` / `Katakan lebih banyak dengan Threads`
- Composer: `[contenteditable=true]` within ~15s; else screenshot `/tmp/debug_editor.png`

## Recovery (manual — no auto path)
1. Chrome Profile 16 → login **jagonya_shopee** (switch account if olivia is active)
2. Confirm feed as jagonya (not chooser)
3. Open threads.com once as that account
4. Refresh cookies: `~/.hermes/scripts/extract_threads_cookies.py`
5. Re-run identity assert (`ds_user_id==3310347890` + username jagonya)
6. Only then: `run_threads_post.sh` / `cron_post.py` (engine order in `publish-engine-trusted-p16.md`)

## Failure signatures
| Symptom | Meaning |
|---|---|
| `ERROR: No editor found after 15s` + Sign up modal | not logged into Threads |
| SSO → `/onboarding/` then 404 | incomplete/wrong Threads account |
| IG home account chooser | sessionid dead |
| Content JSON ok, history not updated | publish failed before success (good — no false USED) |

## Do NOT
- Treat `web_profile_info` alone as auth OK
- Trust `ds_user_id` present without live session check
- Keep foreign Threads session when ds ≠ IG
- Mark DB USED / append history on failed publish
- Unpause cron while identity preflight fails
