# Shopee Anti-Scraping Verified Report (2026-06-26 v2)

curl_cffi + Playwright + Chrome CDP battle-tested against Shopee Akamai WAF (Indonesia region).

## What Works

| Method | Target | Result |
|--------|--------|--------|
| curl_cffi chrome131 | Product page HTML | ✅ 200 OK (1.1MB) |
| curl_cffi chrome131 | Product info extraction | ✅ name/price/variants |
| Chrome CDP (real Chrome) | Login page / product page | ✅ loads in existing session |

**curl_cffi usage:**
```python
from curl_cffi import requests
s = requests.Session(impersonate="chrome131")
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept-Language": "id-ID,id;q=0.9",
})
r = s.get(f"https://shopee.co.id/product/{shop_id}/{item_id}", timeout=30)
```

## What FAILS (all bypass methods tested — 2026-06-26)

| Method | Endpoint | Error |
|--------|----------|-------|
| curl_cffi chrome131 | /api/v4/item/get_ratings | 403 (90309999) |
| curl_cffi chrome131 | /api/v2/item/get_ratings | 403 (90309999) |
| curl_cffi chrome131 | /api/v4/item/get | 403 (90309999) |
| curl_cffi + Profile 16 cookies | Ratings API | 403 (is_login:true) |
| Playwright headless | Any page | Redirect to /verify/traffic/error |
| Playwright headful (non-headless) | Any page | Redirect to /verify/traffic/error |
| Playwright headful + stealth init_script | Any page | Redirect to /verify/traffic/error |
| Chrome CDP (remote-debugging-port) | Ratings API extraction | N/A — reviews client-side only |
| Mobile API endpoint (X-Api-Source: rn) | Ratings | 403 (90309999) |

## Root Cause

Shopee Akamai WAF has **three-layer protection**:

1. **TLS fingerprint** — curl_cffi chrome131 bypasses this (product page loads)
2. **JS challenge** — Playwright Chromium fork detected at JS level (WebDriver, plugins, rendering behavior fingerprint). Even headful mode with stealth scripts fails.
3. **API auth layer** — Ratings API has additional authorization beyond product page access. Even valid Profile 16 cookies don't grant API access via curl_cffi.

## Tested Stealth Bypasses (ALL FAILED)

- `--disable-blink-features=AutomationControlled`
- `Object.defineProperty(navigator, 'webdriver', {get: () => undefined})`
- `window.chrome = {runtime: {}, ...}`
- Plugin enumeration override
- Language/locale spoofing
- notifications permission mock
- hardwareConcurrency / deviceMemory override
- Chrome CDP via `open -a "Google Chrome" --args --remote-debugging-port=9223`

## Bottom Line

**Pinterest is the ONLY reliable source** for real product review images in Indonesia. Shopee review images are 100% locked behind Akamai WAF (as of 2026-06-26). Fall through to Pinterest immediately — do not waste attempts on Shopee.

**Bing is compromised** by ISP DNS hijacking in Indonesia — not a reliable fallback either.
