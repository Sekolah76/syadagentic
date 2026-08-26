# Isolated Affiliate Pools (v19) + Shopee Review Image Rules

Session knowledge 2026-07-13. Supersedes shared-DB assumptions in older docs (`db-sync-between-reply-and-post.md` is **obsolete**).

## Isolated pools (MANDATORY)

| Channel | DB path | Permanent used-set |
|---|---|---|
| Threads Post | `~/.hermes/skills/affiliate/threads-auto-post/references/affiliate-link-database.md` | `~/.hermes/scripts/threads_post_used_links.json` |
| Threads Reply | `~/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md` | `~/.hermes/scripts/threads_reply_used_links.json` |
| Pinterest | `~/.hermes/skills/pinterest-auto-post/references/affiliate-link-database.md` | `~/.hermes/scripts/pinterest_used_links.json` |

### Hard rules
1. **No cross-sync.** `cron_post.py` `DB_COPIES` must only contain the **post** DB. Never copy post USED flags into reply/pinterest pools.
2. **1 post/reply/pin = 1 affiliate link forever** per channel. Auto-reset USED→UNUSED is **OFF**.
3. Same product URL may appear in multiple pools with **independent** USED/UNUSED state.
4. Scripts:
   - Post: `cron_post.py` + `threads_post_http.py`
   - Reply: `threads_reply_v11.py` (v12 intent runner)
   - Pinterest: `cron_pinterest.py` / `pinterest_autopost.py` → **pinterest-auto-post** DB only

### Why
Shared single pool was drained by concurrent Post + Reply + Pinterest crons. Isolation keeps ~100 links effective capacity per channel.

---

## Shopee buyer-review image scrape (for Threads Post images)

Script: `~/.hermes/scripts/shopee_scraper.py` (called from `cron_post.get_real_review_photo`).

### Must
- Resolve affiliate shortlink → **product URL only** `/product/{shop_id}/{item_id}`
- Reject shop/store homepage (`/shop/{id}`, bare shop name)
- Scroll until `.product-rating-overview__filter` chips exist (not just title "Penilaian")
- Click **5 Bintang** then **Dengan Media**
- Extract from **rating-media-list** only (never product gallery / avatar)
- Prefer `i.getAttribute('src')` / `i.src` — **NOT** `currentSrc` (often `@resize_w144_nl.webp` ~5KB thumb)
- Strip `@resize_w*_nl` / `_tn` / `.webp` → download original HD
- Pick max pixel score (`w*h`), min ~250×250

### Pitfalls
| Symptom | Cause | Fix |
|---|---|---|
| Found 0 review imgs | Stopped scroll on title "Penilaian" | Require filter chips / overview height |
| Images ~5KB | Used `currentSrc` thumb | Use original `src` + strip resize suffix |
| Catalog photos | Landed on shop page / gallery | Product-ID hard gate |
| Case miss on "Bintang" | `includes('bintang')` case-sensitive | `toLowerCase()` |

### Cookie refresh note
Shopee/AllScale cookie extract via raw Chrome SQLite Profile 16 can be empty while Camoufox live session is logged in. Prefer `camoufox cookies get` after headed open of target domain (`refresh_shopee_cookies.py` pattern).