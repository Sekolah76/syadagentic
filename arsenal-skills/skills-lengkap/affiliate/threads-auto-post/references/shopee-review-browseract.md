# Shopee Review Photo Extraction via Camoufox (Threads)

Updated: 2026-06-27 (v2 — corrected flow)

## Hard Rule
Threads affiliate post images = **exact-product Shopee review photos ONLY**.
No Pinterest, no AI gen, no product thumbnails, no random fallback.
If Shopee returns no valid review image → skip image entirely.

## ⚠️ CRITICAL FLOW (2026-06-27 v2 fix — `/product/` format)

### 🔴 ROOT CAUSE (SYADAGENTIC angry level: "Tolol tolol kenapa masuk ke toko nya sih anjing")
Resolved shortlink `https://shopee.co.id/opaanlp/1069732465/10799647180`  
→ Format `/{shop_name}/{shop_id}/{item_id}` = **STORE PAGE, bukan product page**  
→ Camoufox renders the store, not the product → No review images → SYADAGENTIC kabur

### 🔵 FIX: Force `/product/{shop_id}/{item_id}` format

**Why this matters:** Shopee has TWO URL formats for the same product:
- **Store format:** `/{shop_name}/{shop_id}/{item_id}` → renders store page with product in a grid
- **Product format:** `/product/{shop_id}/{item_id}` → renders product detail page with review section

The `curl -L` shortlink resolver naturally follows the redirect chain which lands on the **store format**. Must convert to `/product/` format.

### 🔵 FIX: Force `/product/{shop_id}/{item_id}` format

```python
def _resolve_shopee_shortlink(link):
    """Resolve Shopee shortlink to /product/{id}/{id} format."""
    if '/product/' in link:
        return link.split('?')[0]  # already correct

    try:
        r = subprocess.run(['curl', '-sI', '-L', '--max-time', '10', link],
            capture_output=True, text=True, timeout=15)
        output = r.stdout + r.stderr
        urls = re.findall(r'https://shopee\.co\.id/[^\s?>\"\']+', output)
        for url in urls:
            clean = url.split('?')[0]
            m = re.match(r'https://shopee\.co\.id/(?:[^/]+)/(\d+)/(\d+)', clean)
            if m:
                # CONVERT to /product/{shop_id}/{item_id}
                return f'https://shopee.co.id/product/{m.group(1)}/{m.group(2)}'
        return link
    except:
        return link
```

**Key:** Use group capture `(?:[^/]+)/(\d+)/(\d+)` — extract shop_id & item_id, rebuild as `/product/{id}/{id}`.  
This works for BOTH shop-name formats (`opaanlp/1069732465/10799647180`) and any other format.

### ⚠️ __mobile__=1 is SECONDARY
Even after stripping `__mobile__=1`, the `/opaanlp/` (shop name) format still loads the store page.  
The `/product/` format is the PRIMARY fix. `__mobile__=1` stripping is secondary safety.

### Verified test (2026-06-27)
```
Input:  https://s.shopee.co.id/9Kf8dWRnV1
Output: https://shopee.co.id/product/1069732465/10799647180  ✅ clean product URL
```

### Scroll Logic: NOT to bottom, TO "Penilaian Produk"
Scroll detection checks for text "penilaian" in document body:

```python
found = False
for attempt in range(30):
    r = subprocess.run(['camoufox', '--session', session_name, 'eval',
        'document.body.innerText.toLowerCase().includes("penilaian") || (document.querySelector("[class*=star]") !== null)'],
        capture_output=True, text=True, timeout=5)
    if 'true' in r.stdout.lower():
        found = True
        print(f"   Penilaian Produk ditemukan scroll ke-{attempt+1}")
        break
    subprocess.run(f'camoufox --session {session_name} scroll down --amount 1500', shell=True, capture_output=True, timeout=4)
    time.sleep(0.3)
```
Usually found in 1-3 scrolls (not 30). Fallback: scroll to bottom using `scrollY + innerHeight >= scrollHeight` if "penilaian" not found.

### Image Extraction: ALL img with susercontent (NO container filter)
Shopee desktop uses randomized class names — `[class*=review]` returns 0 matches.
Fix: capture ALL `img` tags and filter by URL pattern:

```javascript
(() => {
    const urls = new Set();
    document.querySelectorAll('img').forEach(i => {
        let src = i.src || i.getAttribute('data-src') || '';
        if (!src || !src.includes('susercontent')) return;
        if (/icon|logo|banner|shopee|spay|voucher|chat|shopeemart|flash.sale|deal|brand/i.test(src)) return;
        let clean = src.replace(/_(tn|sm|watermark|cover|thumb)($|[.?_])/, '$2');
        urls.add(clean);
    });
    return JSON.stringify([...urls].filter(u => u.startsWith('http')).slice(0,80));
})()
```
Returns 70-80 URLs in most cases. Download best via `_download_valid_image()`.

### Parse JSON from Camoufox output
```python
raw = r.stdout.strip()
try:
    parsed = json.loads(raw)
    urls = [u for u in parsed if isinstance(u, str) and u.startswith('http') and 'susercontent' in u]
except:
    urls = re.findall(r'https?://[^"\'\\s,\]]+susercontent\.com[^"\'\\s,\]]+', raw)
urls = list(dict.fromkeys(urls))  # dedup
```

### Image Validation
- Download with realistic User-Agent
- File size ≥20KB AND PIL resolution ≥250×250
- Best = highest pixel count (width × height)
- Choose from shuffled candidates (top 15)

## Current Limitation: Product vs Review Photo Discrimination (WIP)

**⚠️ As of 2026-06-27, the JS extraction still cannot reliably distinguish product carousel images from user review images.** Both come from `susercontent.com` CDN with similar URL patterns. Current approach returns 80+ images including product shots.

SYADAGENTIC explicitly criticized: *"Lu punya vision gak? Masa gak bisa bedain mana foto review sama poto produk sih kontol"* — and later *"Hmm masih salah, skip aja lain kali kita build lagi"*.

**Key insight from HTML structure debugging:**
```
FOTO PRODUK:  class="uXN1L5 lazyload GqYslU"   400×400px  container="QN2lPu"
FOTO REVIEW:  class="HcSdrS lazyload rating-media-list__image"  72×128px  container="rating-media-list__image-wrapper--container"
```

**Approaches attempted (all failed or unreliable):**
1. **Class-based targeting** — `querySelectorAll('.rating-media-list__image')` → 0 results because Shopee randomizes class names
2. **Container filter** — `i.closest('[class*="QN2lPu"]')` → unreliable across page loads
3. **Position-based** — find "Penilaian" header Y position → skip images above it → failed because scroll shifts coordinates
4. **Size-based** — filter by naturalWidth <200px (review thumbnails are 72px) → but resolved full-size images can be 400×400px too

**For next build:** Need server-side image classification (vision model) or a deterministic DOM selector that reliably reaches Shopee's rating-media-list section. Current JS-only approach can't distinguish product vs review images with >60% accuracy.

## Proven Results (2026-06-27 test)

| Product | Scrolls | Images Found | Best Image | Size | Notes |
|---------|---------|-------------|------------|------|-------|
| HA PRO Niacinamide (v1 /opaanlp/ store) | 3 | 77 | 1080×1350 | 208KB | STILL store page bug |
| HA PRO Niacinamide (v2 /product/ format) | 1 | 80 | 208KB | Valid | ✅ correct page |
| HA PRO Niacinamide (v3 /product/ + Penilaian scroll) | 1 | 80 | 98KB | 1024×1024 | Still product shot |
| HA PRO Niacinamide (v4 rating-media-list selector) | 1 | 0 | - | - | Selector no match |
| HA PRO Niacinamide (v5 QN2lPu exclusion) | 1 | 80 | 208KB | 1024×1024 | Still mixed |
| HA PRO Niacinamide (v6 position filter) | 1 | 42 | skip | - | Filter too aggressive |
| HA PRO Niacinamide (v7 ALL images, no filter) | 1 | 80 | 136KB | 1024×1024 | Mixed |
| HA PRO Niacinamide (v8 ALL + skip QN2lPu) | 1 | 80 | 208KB | 1024×1024 | Still mixed |

## Pitfalls
- `__mobile__=1` in URL → **ALWAYS strip query params** from resolved shortlink
- Shopee class names are randomized → NEVER rely on `[class*=review]` selector
- Scroll 1500px per step, 0.3s delay — Shopee's lazy load needs brief pauses
- Dismiss overlay/popup before extraction: `document.querySelector('[class*=overlay], [class*=backdrop]')?.remove()`
- Some products genuinely have no review photos → skip gracefully (return "")
- Camoufox session timeout default 60s — 30 scrolls × ~1s each = safe, but keep total under 90s
- Chrome Profile 16 session must NOT have Shopee store page open — affects DOM state
