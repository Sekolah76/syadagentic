# Shopee Affiliate Link Generation

## v2 — Product Offer Page (PRIMARY METHOD ✅)

> 50% faster than v1. No need to visit Shopee first.

```
URL: https://affiliate.shopee.co.id/offer/product_offer
```

### Prerequisites
- Logged in to Shopee Affiliate dashboard (D4NNBOZ account)
- Chrome Profile 16 with valid Shopee cookies

### CDP Flow

```python
# 1. Navigate
cdp("Page.navigate", {"url": "https://affiliate.shopee.co.id/offer/product_offer"})
time.sleep(8)

# 2. Find search input
search_input = cdp_eval("""
    (() => {
        const inp = document.querySelector('input[placeholder*="Cari"]');
        if (inp) {
            const rect = inp.getBoundingClientRect();
            return JSON.stringify({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
        }
        return null;
    })()
""")

# 3. Click input + type
click_at(int(inp['x']), int(inp['y']))
time.sleep(0.5)
cdp("Input.insertText", {"text": "moisturizer"})
time.sleep(1)

# 4. Click "Cari" button — it's a SPAN, NOT a button element!
search_btn = cdp_eval("""
    (() => {
        const els = document.querySelectorAll('span, button, [role="button"]');
        for (let el of els) {
            if (el.textContent.trim() === 'Cari' && el.getBoundingClientRect().y > 80) {
                const rect = el.getBoundingClientRect();
                return JSON.stringify({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
            }
        }
        return null;
    })()
""")
click_at(int(btn['x']), int(btn['y']))
time.sleep(6)

# 5. Click "Buat Link" — MUST use JS dispatchEvent, NOT CDP mouse events!
#    CDP Input.dispatchMouseEvent does NOT trigger this React Ant Design button.
click_result = cdp_eval("""
    (() => {
        const btn = document.querySelector('button.AffiliateItemCard__getlinkBtn');
        if (!btn) return 'no button';
        btn.scrollIntoView({block: 'center'});
        btn.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true, cancelable: true}));
        btn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, cancelable: true}));
        btn.dispatchEvent(new PointerEvent('pointerup', {bubbles: true, cancelable: true}));
        btn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true, cancelable: true}));
        btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
        return 'clicked';
    })()
""")
time.sleep(8)  # Modal appears

# 6. Extract affiliate link — check BOTH input and textarea
affiliate_link = cdp_eval("""
    (() => {
        // Check input fields
        const inputs = document.querySelectorAll('input');
        for (let i of inputs) {
            if (i.value && i.value.includes('s.shopee.co.id')) return i.value;
        }
        // Check textarea fields
        const tas = document.querySelectorAll('textarea');
        for (let ta of tas) {
            if (ta.value && ta.value.includes('s.shopee.co.id')) return ta.value;
        }
        // Fallback: regex body text
        const text = document.body.innerText;
        const m = text.match(/https?:\\/\\/s\\.shopee\\.co\\.id\\/[^\\s\\n]+/);
        return m ? m[0] : null;
    })()
""")

# 7. Verify
assert affiliate_link.startswith("https://s.shopee.co.id/"), "NOT affiliate!"
```

### Alternative: Category Tabs (when search doesn't return relevant results)
- If search returns unrelated products, use category tabs instead
- Click "Perawatan & Kecantikan" for skincare/beauty products
- Category tabs are `div` elements — CDP `click_at()` works fine for these
- Tab position: y≈180

### v2 Pitfalls
1. **"Buat Link" MUST use JS dispatchEvent** — CDP mouse events don't work for this Ant Design button
2. **"Cari" is a SPAN** — not a button. Must find dynamically via querySelector
3. **Enter key doesn't work** — must click the "Cari" button
4. **URL param search is ignored** — `?keyword=...` has no effect
5. **Link can appear in input OR textarea** — check both
6. **Input position shifts** on page reload — always query dynamically

---

## v1 — Custom Link Page (LEGACY FALLBACK)

> Only use if product_offer search fails or doesn't return results.

```
URL: https://affiliate.shopee.co.id/offer/custom_link
```

### CDP Flow

```python
# 1. Navigate + wait
cdp("Page.navigate", {"url": "https://affiliate.shopee.co.id/offer/custom_link"})
time.sleep(5)

# 2. Scroll down (button below fold)
cdp_eval("window.scrollBy(0, 400)")
time.sleep(1)

# 3. Fill textarea — MUST use Input.insertText!
cdp_eval("document.querySelector('textarea').focus()")
time.sleep(0.5)
cdp("Input.insertText", {"text": product_url})
time.sleep(2)

# 4. Click "Buat Link" — CDP click_at() works fine here
# ... (mouseMoved → mousePressed → mouseReleased)
time.sleep(8)

# 5. Extract from SECOND textarea
affiliate_link = cdp_eval("""
    (() => {
        const tas = document.querySelectorAll('textarea');
        for (let ta of tas) {
            if (ta.value && ta.value.includes('s.shopee.co.id')) return ta.value;
        }
        return null;
    })()
""")
```

### URL Format Requirements (v1 only)
```
✅ CORRECT: shopee.co.id/PRODUCT-NAME-i.SHOP_ID.PRODUCT_ID
❌ WRONG:   shopee.co.id/product/SHOP_ID.PRODUCT_ID  → rejected
❌ WRONG:   shopee.co.id/i.SHOP_ID.PRODUCT_ID  → missing slug
```

---

## Common Errors

### "Harap masukkan link yang benar untuk dikonversi"
- **Cause:** Used `ta.value = 'URL'` JS assignment instead of `Input.insertText`
- **Fix:** Focus input → `Input.insertText` — React SPA needs native CPS input

### Generated link not appearing
- Wait 8s minimum — dashboard is slow
- Check all inputs AND textareas for `s.shopee.co.id`
- Modal may overlay the page — check for modal content

### Link is direct, not affiliate
- Result MUST start with `s.shopee.co.id/` (NOT `shopee.co.id/`)
- `s.shopee.co.id/` = affiliate tracking link ✅
- `shopee.co.id/` = direct product link ❌ (NO commission)

---

## ⚠️ API Direct Access: BLOCKED

Shopee's affiliate API (`affiliate.shopee.co.id/api/v2/...`) is protected by aggressive anti-bot detection. Even with valid cookies from Profile 16, API calls return HTML challenge pages instead of JSON.

**What fails:**
- `requests.get()` with browser_cookie3 cookies → 200 but returns HTML (fingerprint check)
- `requests.get()` with `af-ac-enc-dat` header → same result
- Headless Chrome (Browserbase) → traffic error page
- Any non-browser HTTP client → blocked

**What works:**
- CDP on real Chrome with Profile 16 (user must have open session)
- Manual link generation via `affiliate.shopee.co.id/offer/product_offer` dashboard

**Implication:** Cannot bulk-generate affiliate links programmatically. Must use CDP flow above on a REAL Chrome instance (not headless). If CDP port binding fails, user must generate links manually through the dashboard.

---

## Account Info
- Affiliate Account: D4NNBOZ
- Dashboard: https://affiliate.shopee.co.id/dashboard
- Product Offers: https://affiliate.shopee.co.id/offer/product_offer
- Custom Links: https://affiliate.shopee.co.id/offer/custom_link
