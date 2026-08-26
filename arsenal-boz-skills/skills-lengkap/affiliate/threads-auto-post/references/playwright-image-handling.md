# Playwright Image Handling for Threads

## 1. Direct File Input (Upload)
Do not attempt to click dynamic "Add Media" buttons (`aria-label` matching) in Threads Web via Playwright. The DOM structure changes and clicks often fail silently or hit the wrong element.
**Pattern:** Directly target the hidden file input.
```python
file_input = page.locator('input[type="file"][accept*="image"]')
if file_input.count() > 0:
    file_input.first.set_input_files(image_path)
else:
    # Fallback
    page.locator('input[type="file"]').first.set_input_files(image_path)
```

## 2. Affiliate Image Sourcing (Scraping vs AI)
When posting affiliate products (e.g., Shopee), **DO NOT use AI Image Generation (Flux/Gemini) to create product photos.** AI hallucinates packaging and breaks trust.
**Pattern:** Scrape the real product image directly from the affiliate link using Playwright.
```python
# Wait for DOM, extract image from susercontent.com or shopee.co.id/file/
img_srcs = page.evaluate("() => Array.from(document.querySelectorAll('img')).map(i => i.src).filter(s => s.includes('susercontent.com'))")
# Clean up thumbnail suffixes (e.g., remove _tn or _cover) to get high-res
base_url = re.sub(r'_[a-zA-Z0-9]+$', '', img_srcs[0].split('?')[0])
if base_url.endswith('_cover'):
    base_url = base_url[:-6]
```