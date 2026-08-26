# Affiliate Product Imagery: Scrape vs Generate

When creating posts for specific affiliate products (e.g., Shopee), **DO NOT use AI Image Generation (like Flux or Gemini) to visualize the product.** AI models will hallucinate the packaging/bottle shape, leading to inaccurate product representations that confuse buyers and hurt conversion.

**Correct Workflow (Discovered June 2026):**
Scrape the real product image directly from the affiliate URL using Playwright.
1. Navigate to the Shopee link using Playwright.
2. Wait for the DOM to load.
3. Extract `img.src` looking for `susercontent.com` or `cf.shopee.co.id/file/`.
4. Clean the URL (remove thumbnail suffixes like `_tn` or `_cover` to get the high-res version).
5. Download the image locally to upload it to the platform.

## Playwright File Upload Bypass (Threads/Meta)
When uploading images to complex SPAs like Threads, clicking the "Add Media" UI button often fails due to dynamic DOM classes, overlapping layers, or multiple editors in a thread chain.

**Solution:** Bypass the UI button entirely. Directly target the hidden file input to inject the file:

```python
# Instead of page.evaluate("...click UI button...")
file_input = page.locator('input[type="file"][accept*="image"]')
if file_input.count() > 0:
    file_input.first.set_input_files(image_path)
```
This is significantly more stable than relying on visual clicks.