# Affiliate Product Image Handling & Threads Upload (v3.0)

## The "Real Review Photo" Rule (Updated July 2026)
**NEVER use AI-generated images** (Flux/Midjourney/Gemini) for affiliate product posts. 
**PREFER real user review photos over studio mockups** — hands holding products, swatches on skin, 
candid desk photos have higher trust signals and conversion rates.

## Image Sourcing Pipeline (Priority Order)

### 1. Pinterest Search (PRIMARY — Proven Best Source)
Pinterest is the **#1 source for real user review photos** in Indonesia. It is:
- **Not censored** by ISP DNS hijacking (unlike Bing/Google)
- **Rich in UGC** — real users posting swatches, hand-held product shots, desk flatlays
- **Free to scrape** without authentication

**Implementation:**
```python
search_url = f"https://www.pinterest.com/search/pins/?q={urllib.parse.quote(query)}"
# Extract pinimg.com images from DOM
img_links = page.evaluate("""() => {
    return Array.from(document.querySelectorAll('img'))
        .map(img => img.src)
        .filter(src => src.startsWith('https://i.pinimg.com/') && !src.includes('svg') && !src.includes('webapp'));
}""")
# Convert thumbnail to HQ: /236x/ → /736x/
pin_url = img_links[0].replace('/236x/', '/736x/')
```

**Queries to try (in order):**
1. `{product} swatches` (best for makeup/skincare)
2. `{product} review`
3. `{product} di tangan` (hands holding product)
4. `{product} swatch`

### 2. Shopee DOM Scraping (Rarely Works)
Shopee's product pages are protected by **Akamai + Cloudflare WAF**. 
Headless browsers and curl_cffi sessions both return 403 or captcha redirects.
Only attempt as a fast-path; expect failure.

### 3. Bing Image Search (LAST RESORT — Heavily Censored)
Bing Image Search in Indonesia is **subject to ISP DNS hijacking** (Internet Positif).
- `safeSearch` is force-locked to `Strict` by Telkom/Indihome DNS
- Many cosmetic brand queries return 0 results or unrelated images
- `safeSearch=off` parameter is ignored at network level
- Even `cc=US` locale override does not bypass local DNS enforcement

**Workaround:** Set cookies `SRCHHPGUSR=ADLT=OFF&SRCHLANG=en` and `_EDGE_S=mkt=en-us&F=1`
on `.bing.com` domain. Still unreliable.

## Stealth Browser Config
To reduce WebDriver detection by anti-bot systems:
```python
browser = p.chromium.launch(headless=True, args=[
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox"
])
```

## Robust Threads Image Upload Pattern
Do not rely on `page.evaluate()` to click dynamic "Add Media" or "BOZlery" SVG buttons. 
They change classes frequently and can break headless scripts.

Instead, directly target the hidden file input element:
```python
file_input = page.locator('input[type="file"][accept*="image"]')
if file_input.count() > 0:
    file_input.first.set_input_files(image_path)
```

## Platform Access Notes (Indonesia)
| Platform | Headless Access | Image Quality | Notes |
|----------|----------------|---------------|-------|
| Pinterest | ✅ Full access | ⭐⭐⭐ Real UGC | Best source. No auth needed. |
| Shopee DOM | ❌ 403/CAPTCHA | ⭐ Official product | Akamai WAF blocks headless. |
| Bing Images | ⚠️ Censored | ⭐⭐ Mixed | ISP DNS hijacking to Strict. |
| Google Images | ❌ CAPTCHA | — | Immediate reCAPTCHA on headless. |
| Soco (Sociolla) | ⚠️ Limited | ⭐⭐ Studio/Editorial | Mostly professional shots, not UGC. |
| Female Daily | ⚠️ Limited | ⭐⭐ Studio/Editorial | Similar to Soco. |
