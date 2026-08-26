# Chrome Cookie Access — Multi-Platform Verification (Updated 2026-05-25)

## Overview
browser_cookie3 extracts cookies from Chrome Profile 16 for Google, Threads/Instagram.
Twitter/X requires manual login in browser tool (bot detection blocks headless login).
Discord uses a saved token file instead.

## Prerequisites
```bash
# Install via uv (NOT system Python 3.9 — has broken lz4)
uv pip install browser_cookie3 pycryptodome lz4
```

## Quick Access Check Script
```python
import browser_cookie3
import urllib.parse
import json
import requests

def check_all_access():
    """Check logged-in status across all platforms."""
    results = {}
    
    # Google
    cj = browser_cookie3.chrome(domain_name='.google.com')
    cookies = {c.name: c.value for c in cj}
    results['google'] = {
        'logged_in': 'SID' in cookies,
        'cookie_count': len(cookies),
        'email': '<MASKED_EMAIL>'
    }
    
    # Threads (uses Instagram cookies)
    cj = browser_cookie3.chrome(domain_name='.instagram.com')
    cookies = {c.name: c.value for c in cj}
    results['threads'] = {
        'logged_in': 'sessionid' in cookies and 'ds_user_id' in cookies,
        'cookie_count': len(cookies),
        'handle': '@jagonya_shopee',
        'user_id': cookies.get('ds_user_id', '')
    }
    
    # Twitter/X — check via cookies (login status)
    cj = browser_cookie3.chrome(domain_name='.x.com')
    cookies = {c.name: c.value for c in cj}
    twid = cookies.get('twid', '')
    results['twitter'] = {
        'logged_in': 'auth_token' in cookies and 'twid' in cookies,
        'cookie_count': len(cookies),
        'handle': '@MyBiniGua',
        'user_id': urllib.parse.unquote(twid).replace('u=', '') if twid else None,
        'note': 'Cookies extractable but can't be injected. Manual login in browser tool required for posting.'
    }
    
    # Discord (via saved token file)
    try:
        with open('/Users/user/.hermes/discord_token.json') as f:
            token = json.load(f)['token']
        resp = requests.get('https://discord.com/api/v10/users/@me', 
                          headers={'Authorization': token, 'User-Agent': 'Mozilla/5.0'},
                          timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            results['discord'] = {
                'logged_in': True,
                'handle': f"@{data['username']}",
                'user_id': data['id']
            }
        else:
            results['discord'] = {'logged_in': False, 'error': resp.status_code}
    except Exception as e:
        results['discord'] = {'logged_in': False, 'error': str(e)}
    
    return results
```

## Platform-Specific Notes

### Google ✅
- Cookies: `SID`, `SSID`, `HSID` indicate logged-in
- Domain: `.google.com`
- Email: <MASKED_EMAIL>
- OAuth: Auto-renew via refresh token

### Twitter/X ✅ (SOLVED 2026-05-25)
- Cookies: `auth_token`, `twid`, `ct0` indicate logged-in
- Domain: `.x.com`
- Handle: @MyBiniGua (ID: 2034537386840031232)
- **Cookie extraction:** browser_cookie3 → saves to `/Users/user/twitter_cookies.json`
- **Login method:** Same as Threads — user logs in manually in Chrome Profile 16, then extract via browser_cookie3
- **Bot detection:** Twitter blocks headless browser logins (browser_navigate/agent-browser). User MUST login manually in real Chrome Profile 16.
- **Credentials:** Username `MyBiniGua`, password in credential-registry

### Threads/Instagram ✅
- Cookies: `sessionid`, `ds_user_id`, `csrftoken` indicate logged-in
- Domain: `.instagram.com`
- Handle: @jagonya_shopee (ID: 3310347890)
- Cookie extraction: browser_cookie3 via uv run
- Auto-refresh: Every 6 hours (cron f1902736896e)

### Discord ✅ (via token file)
- **NOT extractable via browser_cookie3** — Discord uses localStorage for auth
- **Solution:** Use saved token file: `~/.hermes/discord_token.json`
- Token format: `{"token": "NjM0Nz...R8A8"}`
- Access: `requests.get('https://discord.com/api/v10/users/@me', headers={'Authorization': token, 'User-Agent': 'Mozilla/5.0'})`
- Handle: @d4nnboz (ID: 634730261086470187)
- Email: <MASKED_EMAIL>
- Has MFA: Yes

## Master Credential Registry

All social media credentials are documented in `~/.hermes/hermes-agent/credential-registry.json`:
- Twitter, Threads, Google, Discord access methods
- Wallet addresses (OWL, BOZ)
- Cron job IDs and schedules
- Affiliate database stats

## ⚠️ Twitter Login via Browser Tool — WORKAROUND

Twitter blocks headless browser login (bot detection). To post on Twitter:

1. Open browser tool login page: `https://x.com/i/flow/login`
2. Have user manually provide username + password
3. Browser tool types credentials and attempts login
4. If blocked, user must login manually in their own Chrome, then browser tool can access

**Alternative (future):** Use Chrome Profile 16 with manual login → extract cookies → save for API use.

## Pitfalls
- System Python 3.9 broken → use `uv run`
- Discord uses localStorage, NOT cookies → use saved token file
- Instagram cookies expire faster; auto-refresh every 6h
- **CDP port 9222 does NOT bind on macOS Chrome 148** — do NOT waste time trying
- **Twitter blocks headless browser login** — user must provide credentials or login manually