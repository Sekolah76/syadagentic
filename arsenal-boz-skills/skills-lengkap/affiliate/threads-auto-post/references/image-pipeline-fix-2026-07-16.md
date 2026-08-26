# Threads image pipeline fix (2026-07-16)

## Symptom
Cron posts SUCCESS as **text-only**. History: `has_image: false`, engine `http_v2`.
Log pattern:
```
Found 0 buyer-review images
⚠️ no review images on product page
Publish engine: Browserless HTTP (v1 API)
✅ Post SUCCESS
```

## Root causes
1. `shopee_scraper.scrape_review_image` — filter/scroll/selectors too narrow → 0 URLs.
2. `cron_post.get_real_review_photo()` called Shopee only; **Pinterest fallback existed but was never called**.
3. `threads_post_http.py` correctly text-only when `image_path` empty/missing (not a publish bug).

## Fix (shipped)
### `shopee_scraper.py`
- After `5 Bintang` + `dengan media`: re-scroll 6× amount ~900.
- Broader selectors: rating/comment/review imgs + srcset + background-image.
- Prefer `i.getAttribute('src')` / data-src over `currentSrc` thumbs; strip `@resize_w*`, `_tn`, webp.
- Verified recovery: Dove product went **0 → 16** review images, HD ~300KB.

### `cron_post.py` `get_real_review_photo`
```
Shopee scrape (primary)
  → empty or file <5KB
Pinterest download_pinterest_review_photo (fallback)
  → empty
return ""  # only then text-only
```

### HTTP engine (already OK)
- Image root: rupload → `configure_text_post_app_feed`
- Text: `configure_text_only_post`
- Hard-fail if upload_id accepted but media_type not image when image intended.

## Verify
```bash
python3 -c "
from cron_post import get_real_review_photo
from pathlib import Path
p=get_real_review_photo('https://s.shopee.co.id/<short>','Product Name')
print(p, Path(p).stat().st_size if p else 0)
"
```
Expect non-empty path + size >> 5KB.

## Gotcha
- Shopee public ratings API often **403** — DOM camoufox path is primary.
- Never treat product gallery/carousel as review media.
