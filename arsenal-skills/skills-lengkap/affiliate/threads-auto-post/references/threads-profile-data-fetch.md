# Fetching Threads Profile Data (followers / following / counts)

## CRITICAL GOTCHA — IG counters ≠ Threads counters
Threads and Instagram share ONE user ID (`ds_user_id`), but their follower/following
counters are SEPARATE. Do NOT trust the IG endpoint for Threads numbers.

- `https://i.instagram.com/api/v1/users/{uid}/info/` (X-IG-App-ID `238260118697367`)
  → returns **Instagram** `follower_count` / `following_count`. For @jagonya_shopee this
  returned 120 followers — that is the IG account, NOT Threads.
- Threads Barcelona app-id `3419628305025917` on the IG host → **403 Forbidden**.
- IG app-id on threads text_feed/profile endpoints → **404/500**.
- Raw `urllib` GET on `threads.net`/`threads.com` profile HTML → **302 redirect loop**
  (needs full browser session + LSD token; not worth fighting).

## SESSION VERIFY — confirm IG cookie is authenticated (2026-07-14 fix)
`extract_threads_cookies.py`'s `who()` used to hit
`https://www.instagram.com/api/v1/accounts/edit/web_form_data/` to resolve the
logged-in username. **That endpoint now 302-loops** (`HTTP Error 302 ... infinite loop`)
and returns `err:` → the whole cookie-refresh cron reported `❌ Weak / verify gagal`
even though the session was perfectly valid. False negative that tripped the watchdog.

Working verify (in priority order), all with header `X-IG-App-ID: 936619743392459`:
1. `https://i.instagram.com/api/v1/users/{ds_user_id}/info/` → regex `"username":"..."`
   (authoritative — maps the ds_user_id in the cookie to its handle).
2. Fallback `https://www.instagram.com/api/v1/users/web_profile_info/?username=jagonya_shopee`
   → `200` + real profile JSON confirms the session is authenticated.

Do NOT resurrect `accounts/edit/web_form_data/`. `accounts/current_user/` also returns a
soft-fail body (`status:"fail"`) even on a good session — not reliable for verify.

## RELIABLE METHOD — browser scrape the live profile
Use the managed browser (already logged in via session cookies) against
`https://www.threads.com/@<username>`, then read the DOM:

```js
(() => {
  const t = document.body.innerText;
  const m = t.match(/([\d.,\sRBrbjuta]+)\s*pengikut/i) || t.match(/([\d.,KMkm]+)\s*followers/i);
  const meta = document.querySelector('meta[name="description"]');
  return { followerMatch: m ? m[0] : null, metaDesc: meta ? meta.content : null };
})()
```

- `meta[name="description"]` reliably carries e.g. `"756 Pengikut • 213 Utas • ..."`.
- Body text carries `"766 pengikut"`. Counts may differ slightly between meta cache and
  live body — prefer the live body number, treat meta as backup.
- Note `www.threads.com` (not `.net`) is the current canonical host.

## Account identity (SYADAGENTIC)
- Threads account = **@jagonya_shopee**, uid `3310347890`, cookies at `~/threads_cookies.json`
  (flat dict: datr, ig_did, mid, wd, csrftoken, dpr, ds_user_id, sessionid).
- This is the affiliate ("JAGONYA SHOPEE, JAGONYA BELANJA") posting account — distinct from
  the X/Twitter buzzer account @MyBiniGua. Don't conflate the two.

## Auto-unfollow (non-followback) design notes
For a following−followers diff you need the FULL lists, not just counters:
- `friendships/{uid}/following/` and `friendships/{uid}/followers/` (paginated via
  `max_id` cursor) — same IG-vs-Threads caveat may apply; validate the list is Threads graph
  before trusting it, or enumerate via browser session on the profile follow tabs.
- Mass unfollow triggers action-block: throttle ~40/day, log-normal 30–90s delay, sleep
  window; reuse `scripts/threads_human_behavior.py`. Always dry-run first, honor a
  `threads_whitelist.json`, and skip accounts followed < 3 days (grace period).
