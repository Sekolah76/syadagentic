# Threads Auth Scoping & Follower Counters

Hard-won facts about what the `~/threads_cookies.json` session can and cannot do,
and how Threads counters differ from Instagram. Applies to ALL Threads API work
(auto-post, auto-reply, follow-list / unfollow tooling).

## 1. Cookie session is POST-scoped, NOT read-scoped for friendships

The `sessionid` in `~/threads_cookies.json` (keys: datr, ig_did, mid, wd,
csrftoken, dpr, ds_user_id, sessionid) is valid for **create/reply mutations**
(that's why auto-post + auto-reply work via `threads.net/api/graphql` with
`av=ds_user_id`). It is **NOT** accepted for reading friendship lists.

Endpoints that FAIL with this cookie (all verified 2026-07):

| Endpoint | Result |
|----------|--------|
| `i.instagram.com/api/v1/friendships/{uid}/following/` | 401 Unauthorized |
| `i.instagram.com/api/v1/friendships/{uid}/followers/` | 401 Unauthorized |
| `www.threads.net/api/v1/friendships/{uid}/following/` | 401 `require_login:true` |
| `www.threads.com/api/v1/friendships/{uid}/following/` | 401 `require_login:true` |
| Threads web GraphQL follow-tab doc_ids | 200 but returns HTML login page, not JSON |

**Do not waste cycles probing these with the standard cookie.** Reading
follow-lists needs a fully authenticated *web* session that this cookie does
not provide.

⚠️ Repeated probing triggers a soft-block: `{"message":"Please wait a few
minutes before you try again.","require_login":true}`. Back off ~5 min after
hitting it. Don't hammer.

## 2. Playwright cookie-injection also lands on login modal

Injecting the same cookie into a fresh Playwright context (any of .threads.com
/ .threads.net / .instagram.com domains) → redirects to feed + shows login
modal. Session is app-scoped, not web-scoped.

## 3. Chrome Profile 16 web is NOT logged in as @jagonya_shopee

Cloning Profile 16 (the mechanism auto-post uses) and opening
`threads.com/@jagonya_shopee` shows the **"Ikuti" (Follow)** button, not
**"Sunting profil" (Edit profile)** → confirms the web session is a *visitor*,
not authenticated. Profile 16 works for auto-post because posting is a single
cookie-bearing mutation, but it does NOT give an authenticated web session for
follow-list reads.

**Login-state tell:** `Ikuti`/`Follow` button = logged out; `Sunting
profil`/`Edit profile` button = logged in as owner. Check this before scraping
owner-only surfaces.

## 4. IG counter ≠ Threads counter (separate, shared UID)

`i.instagram.com/api/v1/users/{uid}/info/` returns the **Instagram** follower
count, NOT Threads. Example: same UID `3310347890` showed IG `follower_count:
120` but real Threads was `768 pengikut`. They share one user ID but track
counts independently.

**To get the real Threads follower count:** scrape the profile page DOM.
- Body text contains `N pengikut` (ID locale) / `N followers`.
- `<meta name="description">` also carries e.g. `756 Pengikut • 213 Utas • ...`.
- The profile page renders these publicly (no login needed) via browser_navigate.

## 5. Unblock path for follow-list read / unfollow tooling

To actually read followers/following (needed for auto-unfollow diff), the cookie
must be refreshed from a genuinely logged-in web session:
- Re-run `extract_threads_cookies.py` after logging into Threads **web** fresh, OR
- Manual one-time web login in a non-headless Chrome Profile, then capture that
  session.

Diff logic once lists are available: `non_followback = following - followers`,
minus a whitelist file, minus a grace window (skip N most-recent follows).
Throttle unfollows (~40/day default), honor 01:00–07:00 WIB sleep window,
30–90s log-normal-ish delay between actions, daily-cap state file. Tool built at
`~/.hermes/scripts/threads_unfollow.py`.
