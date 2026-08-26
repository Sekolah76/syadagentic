# Threads Auth Scope + Follow-List Scraping (2026-07-13)

Hard-won gotchas for any Threads scraping/automation beyond posting. @jagonya_shopee
(ds_user_id `3310347890`).

## Cookie scope: IG-app session ≠ Threads web session
- `~/threads_cookies.json` (keys: datr, ig_did, mid, wd, csrftoken, dpr, ds_user_id,
  sessionid) is an **Instagram-app-scoped** session.
- It **works** for IG mobile private API:
  `GET https://i.instagram.com/api/v1/users/{uid}/info/`
  headers `User-Agent: Instagram <ver> Android`, `X-IG-App-ID: 238260118697367`,
  `Cookie: <k=v joined>` → returns username/full_name/counts.
- It **does NOT** authenticate `threads.com` / `threads.net` web via Playwright
  `ctx.add_cookies(...)`. Injecting these cookies (any domain: .threads.com,
  .threads.net, .instagram.com) still lands on the **login modal** + redirects to
  feed `/` — no logged-in profile. `Sunting profil` / logged-in nav never appears.
- Threads friendship endpoints all reject this cookie:
  - `i.instagram.com/api/v1/friendships/{uid}/following|followers/` → **401**
  - `threads.net/api/graphql` profile/follow queries → **302 loop** or **401**
    (needs valid rotating `lsd` token + correct `doc_id`, both scraped from an
    authenticated page — not available while logged out).
  - Threads Barcelona App-ID `3419628305025917` on users/info → **403**.

**→ Proven web-session path = Chrome Profile 16 clone** (same auth the auto-post
engine uses: `threads_post_p16_playwright.py`). For follow-list scrape/unfollow,
port to the P16 clone user-data-dir, NOT cookie injection.

## Follower COUNT: IG count ≠ Threads count
- `users/{uid}/info/` `follower_count` returns the **Instagram** number
  (e.g. 120), which is unrelated to the Threads follower count.
- **Threads follower count** must be read from the live profile page.
  Logged-out `web_extract`/browser on `https://www.threads.com/@{user}` exposes it:
  - body text: `"766 pengikut"` (Indonesian) / `"N followers"`
  - `<meta name="description">`: `"756 Pengikut • 213 Utas • ..."`
  - counts fluctuate slightly between body vs meta (cache lag) — treat as approximate.
- Following count is NOT shown on the logged-out profile page — needs auth session.

## Auto-unfollow tool (built this session)
- `~/.hermes/scripts/threads_unfollow.py` — diff engine:
  `non_followback = following − followers − whitelist`, `--skip-recent N` grace,
  `--dry-run` default / `--execute`, DAILY_LIMIT 40, delay 30–90s, sleep window
  01–07 WIB, whitelist `threads_unfollow_whitelist.json`, state
  `~/.hermes/state/threads_unfollow_state.json`, log `/tmp/threads_unfollow.jsonl`.
- **Blocker**: scraper currently uses cookie injection → login modal (see above).
  Needs re-port to Chrome Profile 16 clone to open Following/Followers dialogs.

## Threads unfollow UI flow (for the P16 port)
- Open profile `/@user` → click `N pengikut` link → dialog `[role=dialog]`.
- Tab switch to `Mengikuti` (Following) inside the dialog.
- Rows are `a[href^="/@"]`; scroll the dialog element (`el.scrollBy(0, scrollHeight)`)
  until username count stabilizes (~4 stable rounds).
- Unfollow: go to `/@target` → click `Mengikuti` button → confirm `Berhenti Mengikuti`.
