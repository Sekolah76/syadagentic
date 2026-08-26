# Pinterest Image Scraping for Real User Review Photos

**Version: v1.0 (2026-06-26)**
**Status: PROVEN IN PRODUCTION — Pinterest is the ONLY reliable source in Indonesia**

---

## Why Pinterest?

| Source | Status | Notes |
|--------|--------|-------|
| Pinterest | ✅ PRIMARY | No anti-bot, no ISP censorship, no SafeSearch |
| Shopee DOM | ❌ BLOCKED | Akamai WAF → 403 + CAPTCHA redirect (99% failure) |
| Bing Images | ❌ CENSORED | ISP DNS hijacking → SafeSearch Strict forced ON |
| Google Images | ❌ BLOCKED | ISP DNS hijacking (Telkomsel/Indihome) |

---

## Query Patterns (PROVEN — use in this order)

```python
queries = [
    f"{product} swatches bibir",       # lip/cheek swatches on real skin
    f"{product} di tangan review",     # hands holding product
    f"{product} pemakaian",            # in-use / application shots
    f"{product} review asli",          # genuine customer review photos
]
```

### Query Design Rules:
- **NEVER use generic `"{product}"` or `"{product} review"`** — returns catalog/official studio photos
- **Add context words:** `swatches`, `di tangan`, `pemakaian`, `bibirm` → pushes real user content to top
- **Try multiple queries** — stop when ≥6 results found
- **Avoid words that trigger Bing's false-positive porn filter** (some cosmetic terms hit this on Bing — not an issue on Pinterest)

---

## Image Extraction (Playwright)

```python
search_url = f"https://www.pinterest.com/search/pins/?q={urllib.parse.quote(query)}"
page.goto(search_url, timeout=15000)
page.wait_for_timeout(4000)

img_links = page.evaluate("""() => {
    return Array.from(document.querySelectorAll('img'))
        .map(img => img.src)
        .filter(src => src.startsWith('https://i.pinimg.com/') 
                    && !src.includes('svg') 
                    && !src.includes('webapp'));
}""")
```

---

## CRITICAL: Skip First 4 Images (Catalog Filter)

**Pinterest ranks catalog/official product shots FIRST (index 0-3).**

```python
# DO NOT: img_links[0]  ← Almost always studio product shot

# DO: Skip index 0-3, pick from 4-8
pick_idx = min(4 + hash(product) % 4, len(img_links) - 1)
pin_url = img_links[pick_idx].replace('/236x/', '/736x/')
```

### Why `hash(product) % 4`?
- Deterministic per product (same product → same offset)
- Adds variety across different products
- Still safely within index 4-7 range

---

## Resolution Upgrade

```python
# Pinterest serves 236x thumbnails by default
# Replace with 736x for HD quality (no re-auth needed)
pin_url = img_links[pick_idx].replace('/236x/', '/736x/')
```

---

## Image Quality Checklist

### ✅ ACCEPT (real user photo):
- Hands holding product
- Swatches on skin (arm, lips, cheek)
- Product on messy desk/nightstand (coffee mug, cables, books visible)
- Natural lighting (not studio)
- Bathroom shelf with other products

### ❌ REJECT (catalog/studio):
- White/plain background (isolated product)
- Perfect studio lighting
- 3D render / mockup look
- Only text/infographic
- No human interaction

---

## Fallback: Bing (Last Resort — Indonesia ISP Censored)

Only use if Pinterest returns 0 results:

```python
query = f"{product} review"
search_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}"

links = page.evaluate("""() => {
    return Array.from(document.querySelectorAll('a.iusc'))
        .map(el => JSON.parse(el.getAttribute('m')).murl)
        .filter(url => {
            const u = url.toLowerCase();
            return u.includes('pinimg.com') || u.includes('soco.id') 
                || u.includes('blogspot') || u.includes('wordpress')
                || u.includes('femaledaily');
        });
}""")
```

### Bing Limitations in Indonesia:
- ISP DNS hijacking → many images return wrong/nature wallpapers
- Some cosmetic keywords trigger false-positive porn filter → 0 results
- `SRCHHPGUSR=ADLT=OFF` cookie sometimes bypasses but unreliable
- **TL;DR: Don't rely on Bing. Pinterest is the answer.**
