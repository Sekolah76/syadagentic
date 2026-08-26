# Threads Browserless HTTP Engine (2026-07-13 → image LIVE)

## Why browserless
Browser engines (AppleScript / Playwright) frequently fail with:
- Kirim UI no-op (Create mutation = 0)
- Composer not found / Lexical state miss
- ChromeLock / P16 guest / AppleEvents disabled after restart
- High RAM + slow cron

Pure HTTP via Threads private media API is 0 UI RAM and seconds per beat.

## Canonical scripts
| Role | Path |
|---|---|
| Executor | `~/.hermes/scripts/threads_post_http.py` |
| Content | `~/.hermes/scripts/threads_content_engine.py` |
| Cron | `~/.hermes/scripts/cron_post.py` |
| Cookie extract | `~/.hermes/scripts/extract_threads_cookies.py` |

Wire order in `cron_post.py`:
1. **HTTP** (`threads_post_http.py`) — PRIMARY
2. AppleScript P16
3. Playwright P16 clone
4. Cookie Playwright (`threads_post_v6.py`)

Env: `THREADS_FORCE_PLAYWRIGHT=1` skips HTTP + AS (debug only).

## Auth / cookies
Priority:
1. **Live Chrome Profile 16 Cookies DB** via `browser_cookie3` (copy DB first)
2. `~/threads_cookies.json`
3. `~/instagram_cookies.json`

Merge `.instagram.com` + `.threads.com` cookies.
Accept identity:
- IG `ds_user_id=3310347890`
- Threads-native `ds_user_id=38122991886` (`@jagonya_shopee`)

**Pitfall:** file cookies often enough for text-only, but image `configure_text_post_app_feed` can HTTP 500 unless live P16 session cookies are used.

## Text post
```
POST https://www.threads.com/api/v1/media/configure_text_only_post/
```
Headers: `X-IG-App-ID=238260118697367`, cookie, `X-CSRFToken`.

| Field | Root | Reply / add-to-thread |
|---|---|---|
| `publish_mode` | `text_post` | `text_post` |
| `caption` | text | text |
| `text_post_app_info` | `{"reply_control":0}` | `{"reply_control":0,"reply_id":"<parent_pk>","is_reply":true,"reply_to_author":"<uid>"}` |
| `replied_to_media_id` | omit | parent **pk** |

### Critical chain rule
`replied_to_media_id` alone is **not enough** → becomes separate root (`is_reply=false`).
Must also set `text_post_app_info.reply_id`.

Hard success: `status=ok` + `media.pk` + `media.code`.

## Image post (LIVE proven)
### 1) Rupload
```
POST https://www.threads.com/rupload_igphoto/fb_uploader_{upload_id}
```
Headers:
- `X-Instagram-Rupload-Params`: `{"is_sidecar":"0","is_threads":"1","media_type":1,"upload_id":"...","upload_media_height":H,"upload_media_width":W}`
- `Content-Type: image/jpeg`
- `X-Entity-Name`, `X-Entity-Length`, `Offset:0`
- body = raw image bytes

### 2) Configure image root
```
POST https://www.threads.com/api/v1/media/configure_text_post_app_feed/
```
Payload keys from live browser capture:
- `upload_id`, `caption`
- `is_threads=true`
- `is_upload_type_override_allowed=1`
- `should_include_permalink=true`
- `text_post_app_info` JSON with `entry_point=top_of_feed`, `reply_control=0`, `self_thread_context_id=<uuid>`, `text_with_entities`
- `web_session_id`, `jazoest`, empty optional fields ok
- headers: `X-ASBD-ID=359341`, `X-Bloks-Version-Id` present in browser capture

Hard success image:
- `status=ok` AND (`media_type==1` OR `image_versions2.candidates` non-empty)

Do **not** use `configure_text_only_post` with `upload_id` for images — returns `media_type=19` and ignores image.

## Content decision (SYADAGENTIC correction)
Before writing copy: decide **cerita** vs **tips** first.
- `cerita`: narrative/relatable (regret, transformasi, pain_point, storytelling, social_proof, validasi_mental)
- `tips`: value/howto (myth_buster, checklist, expert_tip, how_to, comparison, mistake)

3-beat length (do not ship ultra-short 1-liners):
- P1 long hook (1–2 sentences), no URL; cerita P1 no product dump
- P2 2–3 sentences with timeframe/texture/result + soft product bridge
- P3 soft CTA + save + affiliate link + engagement question

Engine: `threads_content_engine.py` (`content_mode` = `cerita_v3` / `tips_v3`).

## Pitfalls
1. Wrong App-ID → use Threads `238260118697367`
2. Missing `reply_id` → fake chain of independent roots
3. Parent must be numeric `pk`, not shortcode
4. Image 500 → refresh live P16 cookies + exact rupload params (`is_threads=1`)
5. Never mark USED without configure `status=ok` + pk/code all beats
6. Guest HTML 404 on profile GET ≠ API dead if session cookie valid
7. Short hooks rejected by SYADAGENTIC as "kurang" — always generate long P1/P2

## Manual test
```bash
python3 ~/.hermes/scripts/threads_content_engine.py
python3 ~/.hermes/scripts/threads_post_http.py /tmp/threads_post_content.json
```
Result: `/tmp/threads_post_result.json`

Cron Auto-Post `23199a7b2d5b` remains paused until SYADAGENTIC unpause after content approval.
