# Threads Account Identity + Follow Management

## Active account (verified 2026-07-13)
- Username: **@jagonya_shopee** (JAGONYA SHOPEE)
- user_id / `ds_user_id`: `3310347890`
- Session cookies: `/Users/user/threads_cookies.json`

## Cookie file format (IMPORTANT)
`~/threads_cookies.json` is a **flat dict** `{name: value}`, NOT a list of cookie objects.
Keys present: `datr, ig_did, mid, wd, csrftoken, dpr, ds_user_id, sessionid`.

```python
import json
c = json.load(open('/Users/user/threads_cookies.json'))
uid = c['ds_user_id']
cookie_header = '; '.join(f'{k}={v}' for k, v in c.items())
```

## Identity probe — confirm which account the session belongs to
Threads runs on Instagram infra, so the IG private API works with the same cookies.

```python
import json, urllib.request
c = json.load(open('/Users/user/threads_cookies.json'))
uid = c['ds_user_id']
cookie = '; '.join(f'{k}={v}' for k, v in c.items())
req = urllib.request.Request(
    f'https://i.instagram.com/api/v1/users/{uid}/info/',
    headers={
        'User-Agent': 'Instagram 309.0.0.40.113 Android',
        'Cookie': cookie,
        'X-IG-App-ID': '238260118697367',
    })
d = json.load(urllib.request.urlopen(req, timeout=15))['user']
# d['username'], d['full_name'], d['follower_count'], d['following_count']
```
`X-IG-App-ID: 238260118697367` is the web IG app id — required or the endpoint 403s.

## Follow-diff / auto-unfollow pattern (non-followback cleanup)
1. Fetch full following + followers lists via paginated GraphQL/private API:
   - `https://i.instagram.com/api/v1/friendships/{uid}/following/?count=200&max_id=<cursor>`
   - `https://i.instagram.com/api/v1/friendships/{uid}/followers/?count=200&max_id=<cursor>`
   - Loop on `next_max_id` until exhausted.
2. `non_followback = set(following_ids) - set(follower_ids)`.
3. Filter: whitelist file (`threads_whitelist.json`), grace period (skip accounts followed < 3 days).
4. Unfollow: `POST https://i.instagram.com/api/v1/friendships/destroy/{target_id}/`
   with `X-CSRFToken` header from `csrftoken` cookie.

### Rate-limit / action-block safety (MANDATORY)
- Meta blocks mass unfollow hard. Cap **~40 unfollow/day**.
- Log-normal delay 30–90s between actions; reuse `scripts/threads_human_behavior.py`.
- Always **dry-run first** (list who would be unfollowed) before real destroy calls.
- Log actions to `/tmp/threads_unfollow.jsonl`.
- @jagonya_shopee at build time: following 1307 vs followers 120 → ~1187 non-followback → ~30 days to clear at 40/day.
