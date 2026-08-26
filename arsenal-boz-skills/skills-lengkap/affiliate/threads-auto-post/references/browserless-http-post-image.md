# Browserless HTTP Post + Image Upload (2026-07-13)

Proven pure-HTTP path for Threads original posts without Chrome/Playwright/AppleScript.

## Why this exists
Browser engines (AppleScript P16, Playwright cookie inject, P16 clone) fail often on:
- Kirim UI no-op (mutation=0)
- Guest / expired session on P16
- ChromeLock / AppleEvents reset
- High RAM + slow cron

Browserless path: **0 browser UI**, ~seconds per 3-post chain.

## Endpoints
| Step | Method | URL |
|---|---|---|
| Image upload | POST | `https://www.threads.com/rupload_igphoto/fb_uploader_{upload_id}` |
| Image root post | POST | `https://www.threads.com/api/v1/media/configure_text_post_app_feed/` |
| Text / reply chain | POST | `https://www.threads.com/api/v1/media/configure_text_only_post/` |

Also works on `threads.net` host for text-only path; **image configure proven on `threads.com`**.

## Auth / cookies
Priority:
1. **Live Chrome Profile 16 Cookies DB** via `browser_cookie3` (copy DB first)
2. Merge: IG domain cookies + Threads domain cookies (Threads keys override)
3. Fallback files: `~/threads_cookies.json` → `~/instagram_cookies.json`

Hard notes:
- File cookie alone can post **text** (`configure_text_only_post`) but often **500** on image configure.
- Live P16 cookies fixed image configure (media_type=1).
- Account may show Threads-native `ds_user_id=38122991886` while IG `ds=3310347890` — both can be `@jagonya_shopee`.
- Always verify publish username == `jagonya_shopee` from response `media.user.username`.

## Rupload (image)
Headers that matter (from live browser capture):
```text
Content-Type: image/jpeg
X-IG-APP-ID: 238260118697367
X-Entity-Name: fb_uploader_{upload_id}
X-Entity-Length: <bytes>
X-Entity-Type: image/jpeg
Offset: 0
X-Instagram-Rupload-Params: {"is_sidecar":"0","is_threads":"1","media_type":1,"upload_id":"...","upload_media_height":H,"upload_media_width":W}
Cookie + X-CSRFToken
```

Success body:
```json
{"upload_id":"...","status":"ok"}
```

## Configure image root
Endpoint:
```text
POST /api/v1/media/configure_text_post_app_feed/
```

Required payload shape (live capture):
- `is_threads=true`
- `is_upload_type_override_allowed=1`
- `upload_id=<from rupload>`
- `caption=<text>`
- `text_post_app_info` JSON including:
  - `reply_control: 0`
  - `entry_point: "top_of_feed"`
  - `self_thread_context_id: <uuid>`
  - `text_with_entities: {entities:[], text: caption}`
  - `fediverse_composer_enabled: true`
- headers: `X-IG-App-ID`, `X-ASBD-ID=359341`, `X-Bloks-Version-Id`, `X-Instagram-AJAX=0`

Success hard checks:
- `status == "ok"`
- `media.pk` + `media.code` present
- `media.media_type == 1` (photo) **or** `image_versions2.candidates` non-empty
- username == `jagonya_shopee`

If image path requested but media_type stays 19 (text-only) → **hard fail** (no silent text-only).

## Text-only / reply chain
Endpoint:
```text
POST /api/v1/media/configure_text_only_post/
```

Root:
```text
publish_mode=text_post
text_post_app_info={"reply_control":0}
caption=...
client_context=...
```

Reply / add-to-thread (proven):
```text
replied_to_media_id=<parent_pk>
text_post_app_info={
  "reply_control":0,
  "reply_id":"<parent_pk>",
  "is_reply":true,
  "reply_to_author":"<user_id>"
}
```

`is_reply=true` only when `reply_id` is present in `text_post_app_info` (not just `replied_to_media_id` alone).

## Canonical script
`~/.hermes/scripts/threads_post_http.py` (v2)
- image on **post_1 only**
- posts 2–3 text replies
- dedup + history + hard gate
- result: `/tmp/threads_post_result.json`

## Cron wiring
`cron_post.py` engine order:
1. `threads_post_http.py` (primary)
2. AppleScript P16
3. Playwright P16 clone
4. cookie Playwright legacy

Env:
- `THREADS_FORCE_PLAYWRIGHT=1` → skip HTTP primary for debug

## Pitfalls
1. **Image configure 500 with file cookies** → use live P16 cookie merge.
2. **Wrong rupload params** (old image_compression-only) can upload ok but configure ignores image.
3. **GraphQL create with random doc_id** → fail (1357004). Prefer v1 media endpoints.
4. **Do not mark USED** unless root has pk/code and (if image) media_type/image candidates prove attach.
5. **Spam test posts** during reverse-eng — clean later; keep live proof posts documented.

## Live proof (2026-07-13)
- Text 3-chain: `DatkjYTj8P9`
- Image root + 2 replies: `DatmBoaEmBJ` (`media_type=1`, imgs=13)
