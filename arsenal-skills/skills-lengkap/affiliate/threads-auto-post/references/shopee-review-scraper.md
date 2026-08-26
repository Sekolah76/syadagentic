# Shopee Review Image Scraper (Product-Only, Bintang 5, HD)

## Tujuan
Ambil **foto review buyer asli** dari halaman **produk** Shopee untuk Threads post.
Bukan gallery katalog, bukan avatar, bukan foto toko.

## Script
- `~/.hermes/scripts/shopee_scraper.py`
- Entry: `scrape_review_image(link, output_path="/tmp/threads_post_image.jpg", product_name="product")`
- Resolve: `resolve_product_url(link)` → canonical `/product/{shop_id}/{item_id}` atau `""` (reject)

## Hard Rules
1. **Link produk only**
   - OK: `s.shopee.co.id/xxx` → resolve → `/product/{shop}/{item}`
   - OK: `shopee.co.id/{user}/{shop_id}/{item_id}` → canonical product
   - REJECT: `/shop/{id}`, nama toko, URL tanpa `item_id`
2. **Filter UI**
   - Klik chip `5 Bintang` dulu (`.product-rating-overview__filter`)
   - Lalu klik `Dengan Media`
3. **Sumber image**
   - Hanya `.rating-media-list img` / `img.rating-media-list__image-wrapper--image`
   - Skip avatar / product-gallery / product-carousel
4. **HD, bukan thumb**
   - Pakai `i.getAttribute('src')` / original path
   - **JANGAN** prefer `currentSrc` — Shopee sering inject `@resize_w144_nl.webp` (≈5KB thumb)
   - Strip: `@resize_w*_nl`, `_tn`, `_sm`, querystring
5. **Pilih winner**
   - Download kandidat, score = `width * height`
   - Min ~250×250; prefer max pixel score
   - Output JPEG RGB ke path target

## Wire ke Cron Post
```text
run_threads_post.sh  (no_agent=true)
  → cron_post.py
    → get_real_review_photo(link, product)
      → shopee_scraper.scrape_review_image(...)
```
`cron_post.get_real_review_photo` **wajib** delegate ke modul scraper (jangan re-inline camoufox lawas).

## Flow Scrape (stabil)
1. Resolve shortlink → product IDs; abort jika non-product
2. `camoufox` open Chrome Profile local + product URL
3. Sleep load, lalu scroll step-by-step (~18× amount 1100) agar rating-overview mount
4. Click **5 Bintang** → wait → click **Dengan Media** → wait
5. Eval JS extract rating-media-list `src` (full)
6. Clean URL → download → pick largest → `/tmp/threads_post_image.jpg`

## Pitfalls
| Gejala | Root cause | Fix |
|---|---|---|
| `Found 0` images | Stop scroll terlalu awal karena text "Penilaian" di header produk | Jangan stop di text header; scroll force + deteksi filter chips / rating-media-list |
| Images ~5KB | Pakai `currentSrc` (`@resize_w144_nl.webp`) | Pakai `src` original + strip resize suffix |
| BOZlery/katalog ikut | Open shop URL / selector longgar | Hard-reject non-product; batasi ke rating-media-list |
| API `get_ratings` 403 | Pure HTTP Shopee block tanpa anti-bot token | Gunakan camoufox session Profile 16, bukan pure API |
| Cookie `~/shopee_cookies.json` empty | Session expired | Bukan blocker untuk review scrape via camoufox login profile |

## Verify
```bash
python3 ~/.hermes/scripts/shopee_scraper.py 'https://s.shopee.co.id/XXXX' /tmp/threads_review_test.jpg
# expect: Found N buyer-review images + ✅ review photo + size >= ~100KB, dim HD
```

## Live proven (2026-07-13)
- BROMEN Booster: 11 imgs → winner 960×1280 / 216KB
- Pond's Shampoo (cron run): 25 imgs → winner 1080×1920 / 173KB → Threads post SUCCESS
