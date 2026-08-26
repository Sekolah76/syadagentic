# Instagram/Threads Session Management

## Cookie Files
- **Instagram:** `/Users/user/instagram_cookies.json` (8 cookies: datr, ig_did, ig_nrcb, mid, wd, csrftoken, dpr, ds_user_id, rur, sessionid)
- **Threads:** `/Users/user/threads_cookies.json` (7 cookies: ig_did, ps_l, ps_n, mid, sessionid, csrftoken, ds_user_id)
- **Merged (for Playwright):** `/tmp/threads_merged_cookies.json` — created at runtime, IG base + Threads override
- **Used by:** `threads-auto-reply`, `threads-auto-post`, `threads_bot.py`
- **Auto-refresh:** Cron job `f1902736896e` runs every 6 hours

## Merged Cookies Pattern (RECOMMENDED for Playwright)

Threads cookies alone often fail login in headless Playwright. Merge with IG cookies:
```python
import json
ig = json.load(open('/Users/user/instagram_cookies.json'))
threads = json.load(open('/Users/user/threads_cookies.json'))
merged = {}
merged.update(ig)      # Base auth tokens (datr, rur, ig_nrcb)
merged.update(threads)  # Threads-specific overrides
json.dump(merged, open('/tmp/threads_merged_cookies.json', 'w'))
```

Inject for BOTH domains:
```python
pw_cookies = []
for name, value in merged.items():
    for domain in [".threads.com", ".instagram.com"]:
        pw_cookies.append({
            "name": name, "value": value,
            "domain": domain, "path": "/",
            "httpOnly": name in ['sessionid', 'ig_did', 'datr', 'mid', 'rur', 'ig_nrcb'],
            "secure": True, "sameSite": "Lax"
        })
context.add_cookies(pw_cookies)
```

## Cookie Extraction (PRIMARY METHOD)

### `browser_cookie3` via uv (verified 2026-05-25)
```bash
# Install deps (once)
uv pip install browser_cookie3 pycryptodome lz4

# Extract cookies
uv run python3 ~/.hermes/scripts/extract_threads_cookies.py
```

**Why `uv run` is required:** System Python 3.9 has broken `lz4` module (`ModuleNotFoundError: lz4._version`). The `uv run` environment has properly linked native extensions.

**Script location:** `~/.hermes/scripts/extract_threads_cookies.py`

**Auto-refresh cron:** Job `f1902736896e`, schedule `0 */6 * * *`, delivers to local only.

### Why NOT CDP port 9222
Chrome 148 on macOS does NOT bind port 9222. The `--remote-debugging-port=9222` flag is ignored due to macOS sandbox. `curl localhost:9222` always returns connection refused. `lsof -i :9222` always empty.

## Session Validation (run before any CDP automation)

**⚠️ Cookie file may contain control characters** that cause `requests.exceptions.InvalidHeader`. The raw JSON export from Chrome has binary values. Always clean before use.

```python
import requests, json, re

def check_session_valid() -> tuple[bool, dict]:
    """Check if Instagram session is still valid. Returns (is_valid, details)."""
    raw = json.load(open('/Users/user/instagram_cookies.json'))
    # Clean control characters from cookie values
    cookies = {k: re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(v)) for k, v in raw.items()}
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    
    resp = requests.get(
        'https://i.instagram.com/api/v1/accounts/current_user/?edit=true',
        headers={
            'User-Agent': 'Instagram 275.0.0.27.98 Android (33/13; 420dpi; 1080x2168; samsung; SM-G991B; o1s; exynos2100; en_US; 458229258)',
            'Cookie': cookie_str,
            'X-CSRFToken': cookies.get('csrftoken', ''),
            'X-IG-App-ID': '936619743392459',
        },
        timeout=10
    )
    
    if resp.status_code == 200:
        data = resp.json()
        user = data.get('user', {})
        return True, {
            'username': user.get('username'),
            'full_name': user.get('full_name'),
            'user_id': user.get('pk'),
        }
    else:
        data = resp.json()
        return False, {
            'message': data.get('message'),
            'logout_reason': data.get('logout_reason'),
            'error_title': data.get('error_title'),
        }
```

## Logout Reasons
| Code | Meaning |
|------|---------|
| 8 | Fully invalidated — requires fresh 2FA login |
| 4 | Account disabled/terminated |
| (other) | Session expired without invalidation (may refresh via si/fetch_headers/) |

## Refresh Options

### Option 1: Auto-refresh (preferred)
Cron job `f1902736896e` runs every 6 hours — no user action needed.

### Option 2: Manual extract
```bash
uv run python3 ~/.hermes/scripts/extract_threads_cookies.py
```

### Option 3: Manual re-login (if session fully invalidated)
1. Open Chrome Profile 16
2. Login to Instagram with 2FA
3. Login to Threads
4. Run: `uv run python3 ~/.hermes/scripts/extract_threads_cookies.py`
5. Verify: `SESSION VALID: @jagonya_shopee`

## Symptom Matrix
| Scenario | API Status | Search Works? | Balas Click Works? | Kirim Works? |
|----------|------------|---------------|---------------------|--------------|
| Valid session | 200 | ✅ | ✅ | ✅ |
| Expired (logout_reason=8) | 403 | ⚠️ partial | ❌ silent fail | ❌ |
| Cookie-injected but restricted | 403 | ✅ | ❌ silent fail | ❌ |
| Account flagged (integrity review) | 200 | ✅ | ✅ | ⚠️ posts invisible |

**Key insight:** Cookie injection via CDP `Network.setCookie` may enable page navigation and search, but CDP clicks on interactive elements (Balas, Kirim) silently fail without full session. This is Threads' anti-bot behavior — check API status, not just page rendering.

**Account flagged diagnosis:** When API returns 200 and dialog closes but comment never appears, check `integrity_review_decision` in the response from `POST /api/v1/media/configure_text_only_post/`. If `"pending"` on every attempt (including plain text), the account is flagged. See `references/api-endpoints.md` for response structure.

## Login Detection (Bilingual UI)

Threads may render in English or Indonesian. Check BOTH:
```python
is_logged_in = any(x in body for x in [
    'Beranda', 'Lainnya',  # Indonesian
    'For you', 'Home', 'Search', 'Profile', 'Activity'  # English
])
```
If only Indonesian labels are checked, login appears to fail when Threads shows English UI.

## Browser Tool Limitation

**Browserbase browser has NO session cookies.** browser_navigate connects to a remote browser without auth. Login dialog always appears. Do NOT use browser tool for Threads — use Playwright with cookie injection instead.

## Chrome Profile 16 Location
```
~/Library/Application Support/Google/Chrome/Profile 16
```
