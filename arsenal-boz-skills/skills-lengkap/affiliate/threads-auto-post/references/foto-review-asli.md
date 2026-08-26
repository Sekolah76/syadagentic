# Foto Review Asli — Sourcing Strategy (v12)

## Golden Rule
BOZ wants FOTO ASLI REVIEW — hands holding product, swatches on skin, candid desk/nightstand shots. NEVER product catalog, studio lighting, white background, 3D render, or AI-generated.

## Pinterest (PRIMARY — No ISP Censorship)

Pinterest is NOT affected by Indonesian ISP DNS hijacking (SafeSearch strict on Bing). It returns real user photos reliably.

### Query Strategy
```
"{produk} swatches bibir"
"{produk} di tangan review"  
"{produk} pemakaian"
"{produk} review asli"
```

### Selection Logic
- First 4 images on Pinterest = usually catalog/product-only shots
- **SKIP index 0-3** → pick from index 4-8
- `pick_idx = min(4 + hash(product) % 4, len(links) - 1)`
- Resolusi: replace `236x` → `736x` in URL for HQ version

### Extraction (Playwright)
```javascript
Array.from(document.querySelectorAll('img'))
  .map(img => img.src)
  .filter(src => src.startsWith('https://i.pinimg.com/') && !src.includes('svg'))
```

## Bing (LAST RESORT — Heavily Censored)

Indonesian ISPs (Telkom/Telkomsel) DNS-hijack Bing to enforce SafeSearch Strict. Some keywords trigger false-positive porn filters → results become irrelevant (landscapes, academic papers, random objects).

### Mitigation (limited effectiveness)
- Set `SRCHHPGUSR=ADLT=OFF` cookie
- Use `&cc=US&setlang=en` params
- Still unreliable — prefer Pinterest

## Shopee DOM (BLOCKED)
Akamai + Cloudflare WAF blocks 100% of automated access:
- Playwright headless → 403 / verify/captcha redirect
- curl_cffi impersonate → 403 error 90309999
- browser_cookie3 + cookies → still 403
- **DO NOT attempt — waste of time**

## What to REJECT
- ❌ Background putih polos / isolated
- ❌ Studio lighting sempurna
- ❌ AI-generated / 3D render / mockup
- ❌ Official marketing poster / infografis
- ❌ No human interaction element

## What to ACCEPT
- ✅ Tangan memegang produk
- ✅ Swatches di kulit (bibir, tangan)
- ✅ Produk di meja/kasur berantakan
- ✅ Pencahayaan natural (jendela, lampu kamar)
- ✅ Ada objek sekitar (boneka, gelas, kabel, charger)