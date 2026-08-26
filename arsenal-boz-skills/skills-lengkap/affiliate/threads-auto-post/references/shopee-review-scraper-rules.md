# Shopee Review Image Scraper Rules (Strict Product Link)

## 📌 Rules & Constraints
1. **Input URL**: Wajib berupa link produk valid (`/product/{shop_id}/{item_id}` atau shortlink `s.shopee.co.id/xxx` yang diresolve ke format canonical tersebut).
2. **Shop URL Reject**: JANGAN PERNAH scrape jika link yang ter-resolve adalah link toko (`/shop/` atau `shopee.co.id/{username}` tanpa ID produk). Tolak (reject) URL toko untuk mencegah bias gallery/katalog dan kegagalan element detection.
3. **Selector Target**: Target `.rating-media-list` (buyer reviews). Lakukan scroll secara progresif dan klik filter "dengan media" (with media).
4. **Script**: Gunakan `~/.hermes/scripts/shopee_scraper.py` (Product-Only Hard Reject) atau `get_real_review_photo()` di `cron_post.py`.

## 🛠️ Scraper Script (`shopee_scraper.py`)
```python
# Parse product IDs from resolved URL
def parse_product_ids(url: str) -> tuple[str, str] | None:
    if not url: return None
    clean = url.split("?")[0].split("#")[0]
    if re.search(r"shopee\.co\.id/shop/\d+/?$", clean): return None
    if re.search(r"shopee\.co\.id/[A-Za-z][^/]*/?$", clean): return None
    m = PRODUCT_RE.search(clean)
    if m: return m.group(1), m.group(2)
    m = PATH_IDS_RE.search(clean)
    if m: return m.group(1), m.group(2)
    return None
```
