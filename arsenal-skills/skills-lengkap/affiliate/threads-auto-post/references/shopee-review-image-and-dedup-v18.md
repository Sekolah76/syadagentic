# Shopee Review Image + Affiliate Dedup (v18.3, 2026-07-16)

## Product-only review images
- Input must resolve to product page: `/product/{shop_id}/{item_id}`
- Affiliate shortlink `s.shopee.co.id/xxx` → curl `-sI -L` → parse → canonical product URL
- Reject shop/store pages (`/shop/{id}`, bare shop slug)

## Filter order (DOM) + hardened extract (2026-07-16)
1. Scroll until rating filters mount
2. Click **5 Bintang**
3. Click **Dengan Media** (broad match: media/dengan media)
4. **Re-scroll 6× after filters** so lazy media mounts (critical — without this: Found 0)
5. Extract from broad selectors: `.rating-media-list`, `[class*=rating|comment|review] img`, srcset, background-image
6. Prefer `i.getAttribute('src')` / original `src` — **not** `currentSrc` (often `@resize_w144` thumb)
7. Strip: `@resize_w\d+(_h\d+)?(_nl)?`, `.webp`, `_tn`, `_sm`

## Image path contract (HARD — text-only root cause 2026-07-16)
- `cron_post.get_real_review_photo(link, product)`:
  1. **PRIMARY** `shopee_scraper.scrape_review_image` → `/tmp/threads_post_image.jpg`
  2. If empty / file <5KB → **MUST call** `download_pinterest_review_photo` (was defined but unwired → all posts text-only)
  3. Else return `""` (HTTP engine continues text-only)
- `threads_post_http.py`: if `image_path` exists → rupload + `configure_text_post_app_feed`; else text-only
- History field: `has_image` false on last N posts = image pipeline broken, not HTTP engine

## Content Viewbait & Ragebait (v18.3, 2026-07-16)
- **Rules (Post 1 / Hook)**:
  - Baris pertama wajib **KAPITAL SEMUA** (ALL CAPS)
  - Panjang post_1 wajib **minimal 210 karakter**
  - Gunakan tone **ragebait, sarkas, validasi emosi ekstrem, atau kubu-kubuan** (Gen-Z style)
  - Auto-pad dengan fragmen edukasi/tips per kategori jika total template kurang dari 210 char
- **CTA (Post 3)**: Mancing debat / kubu-kubuan di baris komentar untuk mendongkrak algoritma views.

## Scripts
- `~/.hermes/scripts/shopee_scraper.py` — product resolve + scrape
- `~/.hermes/scripts/cron_post.py` — `get_real_review_photo()` (Shopee → Pinterest fallback)
- `~/.hermes/scripts/threads_post_http.py` — upload + configure image post
- `~/.hermes/scripts/threads_content_engine.py` — content generator (all-caps hook + 210 char constraint)

## 1 post = 1 affiliate link forever
- Permanent set: `~/.hermes/scripts/threads_post_used_links.json` (+ legacy `threads_used_links.json`)
- On success: mark DB `✅ USED` **and** append permanent set
- **No USED→UNUSED recycle**
- Heal: any `❌ UNUSED` already in history/permanent set → mark `✅ USED`

## Cron
- Auto-Post · `run_threads_post.sh` · `no_agent: true` · silent success
- Logs: `/tmp/threads_post_cron_run.log`

## Pitfalls
- Shopee ratings API public → 403; use camoufox DOM scrape
- Cookie IG mobile valid for some APIs but **not** threads.com web login for follow-list (unrelated unfollow work)
- IG `users/{uid}/info` follower_count = **IG**, not Threads — scrape `threads.com/@user` DOM for real Threads followers
