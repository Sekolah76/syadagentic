# Threads Auto-Post: Shopee Image Scraping & Playwright Upload

## 1. Scrape Real Images, Don't Generate (June 2026)
Using AI (e.g., Flux) to generate images for specific affiliate products results in hallucinations that do not match the actual packaging. 
**Solution:** Navigate to the Shopee affiliate link via Playwright, extract `img.src` matching `susercontent.com` or `shopee.co.id/file/`, strip the `_tn` (thumbnail) or `_cover` suffix to get high-res, and download it locally.

## 2. Playwright Image Upload on Threads
Clicking the "Add media" UI button via `aria-label` often fails due to DOM translation or overlapping elements.
**Solution:** Bypass the UI button entirely. Target the hidden file input directly:
```python
file_input = page.locator('input[type="file"][accept*="image"]')
if file_input.count() > 0:
    file_input.first.set_input_files(image_path)
```
