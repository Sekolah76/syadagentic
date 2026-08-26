# Browserless Threads Post — GraphQL Direct (2026-07-13)

Goal: post ke Threads **tanpa browser** (no Playwright / AppleScript / CDP UI).
Hanya pure HTTP (`requests` / `curl_cffi`).

## Status
| Item | State |
|------|-------|
| Browser engines (AS / P16 PW / cookie PW) | Production — lihat `publish-engine-trusted-p16.md` |
| Pure HTTP GraphQL post | **Belum di-ship** — blueprint di bawah |
| Cookie IG `jagonya_shopee` | Verified via `web_form_data` (`ds=3310347890`) |
| Cookie → Threads SSO pure HTTP | **Belum auto** — GET threads.com/@user → 404 tanpa session Threads native |

## Why pure cookie inject fails (live probe 2026-07-13)
```text
GET https://www.instagram.com/  + IG cookies     → 200, logged-in
GET https://www.threads.com/@jagonya_shopee      → 404 (cookie IG saja)
GET https://www.threads.net/ (no cookies)        → 200 guest, csrftoken only
```
IG `sessionid` **tidak** otomatis jadi session Threads lewat pure HTTP. Perlu SSO handshake dulu.

## Endpoint
```
POST https://www.threads.net/api/graphql
# atau https://www.threads.com/api/graphql (same stack)
```

## Required tokens
| Token | Source | Notes |
|-------|--------|-------|
| `sessionid` | IG cookie / Threads cookie post-SSO | Auth |
| `csrftoken` | cookie | Header `X-CSRFToken` |
| `ds_user_id` | `3310347890` | Identity assert |
| `lsd` | HTML bootstrap (`"LSD",[],{"token":"..."}`) | GraphQL body |
| `fb_dtsg` | HTML bootstrap (`DTSGInitialData`) | Form token |
| `x-ig-app-id` | `238260118697367` (Threads web) | Bukan IG app `936619743392459` |

## Mutation names (from browser network hooks)
Captured di `threads_post_v6.py` request listener:
- `Create` / `Publish` / `PostMedia` / `TextPost` / `Configure`
- `Barcelona*Create*` (internal friendly name)

Hard success = response mutation name match **Create|Publish|PostMedia|TextPost|Configure|Barcelona.*Create** + status 200 + media id/code.

## Recommended build path: Hybrid → Pure
### Phase B (hybrid capture) — do first
1. Run one headed Playwright post with network dump.
2. Save exact request:
   - URL, headers, form body (`fb_api_req_friendly_name`, `variables`, `doc_id` / `query_id`)
3. Dump post-SSO cookies + `lsd` + `fb_dtsg` to JSON.

### Phase A (pure HTTP) — after schema known
```text
1. Load ~/instagram_cookies.json
2. Auth assert: ds==3310347890 + web_form_data username==jagonya_shopee
3. SSO bootstrap (HTTP only):
   GET threads login → follow IG OAuth redirects → store Threads cookies
4. Extract lsd + fb_dtsg from HTML or subsequent response
5. POST /api/graphql with Create mutation variables
6. Hard gate: media_id/code OR create mutation OK — no soft profile HTML
7. Reuse story engine + history/USED only on hard success
```

## Image (optional later)
1. Upload via rupload endpoint (capture from same network dump).
2. Attach returned `media_id` to create variables.
3. Skip image entirely until text-only post solid.

## Do NOT
- Claim browserless success without mutation response proof
- Mark DB USED / append history on soft HTML match
- Use IG-only cookies against Threads GraphQL without SSO tokens
- Treat guest `csrftoken` as logged-in session
- Unpause cron on pure-HTTP path until hard gate green

## Reuse (already in skill)
| Piece | File |
|-------|------|
| Cookie extract P16 | `scripts/extract_threads_cookies.py` |
| Auth preflight | `references/auth-preflight-jagonya.md` |
| Story 3-beat | `scripts/threads_story_engine.py` |
| Dedup + hard gate patterns | `scripts/threads_post_v6.py`, `references/publish-engine-trusted-p16.md` |
| Engine order (browser) | `references/publish-engine-trusted-p16.md` |

## Target script (when built)
`scripts/threads_post_http.py` — pure requests, no browser deps.
Wire as engine 0 in `cron_post.py` only after hard gate proven live.

## Related
- `references/publish-engine-trusted-p16.md` — browser engines + hard gate
- `references/auth-preflight-jagonya.md` — identity assert
- `references/playwright-post-method.md` — current browser post method
