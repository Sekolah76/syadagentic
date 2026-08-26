# Threads Account Status Verification

## Instagram API Method (Primary — Works Without Threads Cookies)

Threads uses Instagram auth. The Instagram API can verify if the underlying account is active, which correlates to Threads status.

### Quick Status Check

```python
import browser_cookie3
import urllib.request
import json

# Load Instagram cookies from Chrome Profile 16
cookies = browser_cookie3.chrome(
    domain_name='.instagram.com',
    cookie_file='/Users/user/Library/Application Support/Google/Chrome/Profile 16/Cookies'
)
cookie_str = '; '.join([f'{c.name}={c.value}' for c in cookies])

# Check user profile via Instagram API
req = urllib.request.Request(
    'https://www.instagram.com/api/v1/users/web_profile_info/?username=jagonya_shopee',
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Cookie': cookie_str,
        'X-IG-App-ID': '936619743392459',
        'X-Requested-With': 'XMLHttpRequest',
    }
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())

user = data['data']['user']
print(f"Username: {user['username']}")
print(f"Bio: {user['biography']}")
print(f"Follower count: {user['edge_followed_by']['count']}")
```

### Threads-Specific Verification (Browser)

For direct Threads verification, navigate to the profile page:

```python
# Navigate to Threads profile
browser_navigate('https://www.threads.net/@jagonya_shopee')

# Check page content for indicators
# ✅ ACTIVE: Title shows "@username • Threads", profile loads, posts visible
# ⚠️ SUSPENDED: 404 page, "This page isn't available" message
# ⚠️ BANNED: Redirect to login, no profile visible
```

### Status Indicators

| Indicator | Active | Suspended | Banned |
|-----------|--------|-----------|--------|
| HTTP Status | 200 | 404 | 302/403 |
| Page title | "@user • Threads" | "Page not found" | Login redirect |
| Profile loads | ✅ Yes | ❌ No | ❌ No |
| Posts visible | ✅ Yes | ❌ No | ❌ No |
| Instagram API | Works | Works | May fail |

### Important Notes

- **Threads suspension ≠ Instagram suspension** — account can be active on Instagram but suspended on Threads
- **Browser verification is most reliable** — API may return stale data
- **The `ds_user_id` in cookies identifies the account** — consistent across Instagram and Threads

### Cookie Maintenance

- Instagram cookies auto-refresh via cron (every 6 hours)
- Cookie file: `~/instagram_cookies.json`
- Threads uses same Instagram session — no separate cookies needed
- If verification fails with 403 `login_required`, cookies need refresh

### Account: @jagonya_shopee

- **ID:** 3310347890
- **Status:** ✅ ACTIVE (verified 2026-05-31)
- **Followers:** 601
- **Verified:** Blue checkmark
- **Bio:** "JAGONYA SHOPEE, JAGONYA BELANJA! 🧡"
- **Link:** jagonya.my.id
- **Tags:** ShopeeAffiliate, Skin Care Threads, Makeup Threads

### Verification Results Template

```
🟠 THREADS ACCESS CHECK

🔸 Status
▪️ @jagonya_shopee [ACTIVE/SUSPENDED/BANNED]
▪️ [X] followers, [verified/unverified]
▪️ Post terakhir: [time]

🔸 Cookies
▪️ Instagram cookies via Profile 16: [valid/expired]
▪️ Session ID: [active/expired]
▪️ Access: [FULL/READ-ONLY/NONE]
```
