# Instagram/Threads Session Management

See full details in `threads-auto-reply` skill § `references/session-management.md`.

## Quick Pre-Flight Check
```python
import requests, json, re

raw = json.load(open('/Users/user/instagram_cookies.json'))
cookies = {k: re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(v)) for k, v in raw.items()}
resp = requests.get('https://i.instagram.com/api/v1/accounts/current_user/?edit=true', headers={
    'User-Agent': 'Instagram 275.0.0.27.98 Android (33/13; 420dpi; 1080x2168; samsung; SM-G991B; o1s; exynos2100; en_US; 458229258)',
    'Cookie': '; '.join(f'{k}={v}' for k, v in cookies.items()),
    'X-CSRFToken': cookies.get('csrftoken', ''),
    'X-IG-App-ID': '936619743392459',
}, timeout=10)

# 200 = valid, 403 login_required = expired (logout_reason: 8 = needs 2FA re-login)
```

## Cookie Refresh
```bash
# Auto-refresh every 6h via cron f1902736896e

# Manual refresh
uv run python3 ~/.hermes/scripts/extract_threads_cookies.py
```
