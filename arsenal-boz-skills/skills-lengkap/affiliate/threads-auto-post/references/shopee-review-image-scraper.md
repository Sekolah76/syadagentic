# Shopee Buyer Review Image Scraper (product-only, 5★, HD)

Updated: 2026-07-13 · Script: `~/.hermes/scripts/shopee_scraper.py`

## Goal
Ambil **foto review pembeli asli** untuk Threads affiliate post — bukan gallery katalog, bukan avatar, bukan toko.

## Hard rules (BOZ)
1. **Link produk only** — never shop/store page.
2. **Bintang 5 only** — click `5 Bintang` chip before extract.
3. **Dengan Media** — then click media filter.
4. **HD** — original CDN file, not Shopee thumbnail resize.
5. **cron_post wire** — `get_real_review_photo()` MUST call `shopee_scraper.scrape_review_image()` (no inline legacy scraper).

## Resolve URL
Affiliate shortlink pattern:
```
https://s.shopee.co.id/XXXX
  → redirect → https://shopee.co.id/{user|opaanlp}/{shop_id}/{item_id}
  → canonical → https://shopee.co.id/product/{shop_id}/{item_id}
```
Regex IDs:
- `/product/(\d+)/(\d+)`
- `shopee.co.id/(?:[^/]+)/(\d+)/(\d+)`

**REJECT** if:
- `shopee.co.id/shop/{id}`
- `shopee.co.id/{shopname}` (no item id)

CLI resolve self-check:
```bash
python3 ~/.hermes/scripts/shopee_scraper.py   # no args → prints resolve samples
```

## Scrape flow (camoufox + Profile 16)
```text
1. camoufox open chrome_local_102130715962900495 PRODUCT_URL --headed
2. sleep ~6s
3. scroll down ~18 × 1100px (lazy-mount rating overview)
4. click chip text starts with "5 bintang" / "5 star"
5. click chip "dengan media" / "with media"
6. extract .rating-media-list img (buyer review only)
7. download + pick max(w*h)
8. session close
```

Filter chip classes (live 2026-07-13):
- `.product-rating-overview__filter`
- Texts: `5 Bintang (N)`, `Dengan Media (N)`

## HD image trap (critical)
Shopee review `<img>` often has:
| field | example | size |
|---|---|---|
| `src` | `.../file/id-...` | **HD original** (e.g. 960×1280, 150–220KB) |
| `currentSrc` | `.../file/id-...@resize_w144_nl.webp` | **thumb** (~5KB, 144px) |

**Always prefer `i.getAttribute('src')` / `i.src`.**  
Never prefer `currentSrc` first.

Strip before download:
```
@resize_w\d+(_h\d+)?(_nl)?
.webp
_tn / _sm
```

Original CDN form that works:
```
https://down-id.img.susercontent.com/file/{file_id}
```

## Selectors (buyer only)
Include:
- `.rating-media-list img`
- `img.rating-media-list__image-wrapper--image`
- fallback: `.shopee-product-comment-list img` inside ratings

Exclude:
- `.shopee-avatar`, `[class*="avatar"]`
- `[class*="product-gallery"]`, product-carousel, image-carousel
- avatar / icon / logo / banner / spay / voucher paths

## Quality gate
- min ~250×250 px
- pick highest pixel score `w*h`
- convert RGB JPEG quality ~92
- output default: `/tmp/threads_post_image.jpg`

## CLI
```bash
python3 ~/.hermes/scripts/shopee_scraper.py 'https://s.shopee.co.id/XXXX' /tmp/out.jpg
```

## Wire-in
- `cron_post.py`: `_resolve_shopee_shortlink()` → `shopee_scraper.resolve_product_url`
- `cron_post.py`: `get_real_review_photo()` → **only** `from shopee_scraper import scrape_review_image`
- Threads publish: `threads_post_http.py` consumes `image_path`

## Pitfalls
| Symptom | Cause | Fix |
|---|---|---|
| Found 0 images | Stopped scroll too early on title "Penilaian" count | Force ~18 scrolls; require real filter chips, not mere "penilaian" text |
| Found N but all ~5KB | Used `currentSrc` thumbs | Use `src` + strip `@resize_w144_nl.webp` |
| Shop homepage / no ratings | Passed store URL | Hard reject non-product resolve |
| BOZlery product photo | Wrong selector | Stay inside `.rating-media-list` only |
| API `get_ratings` 403 | Pure HTTP blocked without anti-bot | Stick to camoufox DOM path |
| Inline scraper drift | `cron_post` kept old camoufox block | Always delegate to `shopee_scraper.py` |

## Live probe (2026-07-13)
| Product | Result |
|---|---|
| BROMEN Brightening Simpel Booster (`8fPRqgStF6`) | 11 candidates → **960×1280 / 216KB** |
| Pond's Hair Loss Prevention Shampoo (`9KfEwLfptW`) | 25 candidates → **1080×1920 / 173KB** → cron post SUCCESS |
