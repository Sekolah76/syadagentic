# Threads Auto-Post: Image Handling & Upload Pitfalls

## 1. Product Image Hallucination (Scrape, don't Generate)
Never use Text-to-Image AI (like Flux, Midjourney, or Gemini) to generate photos of specific real-world products (e.g., "Skintific Moisturizer" or "Heura Parfum"). The AI will hallucinate the packaging, resulting in mismatched, fake-looking products that reduce conversion.

**Solution:** Use Playwright to visit the Shopee/affiliate link, wait for the DOM to load, and scrape the actual product image (`img` tags containing `susercontent.com` or `cf.shopee.co.id/file/`). Download this image locally and use it for the post.

## 2. Playwright File Uploads on Threads
Do not attempt to click the "Add Image" / "Media" button using DOM selectors or ARIA labels. Threads' dynamic classes and overlapping SVG elements cause clicks to fail, or target the wrong editor in multi-post threads.

**Solution:** Directly target the hidden file input element and use `set_input_files`.
```python
# Attach to the FIRST post's editor seamlessly without UI clicks
file_input = page.locator('input[type="file"][accept*="image"]')
if file_input.count() > 0:
    file_input.first.set_input_files(image_path)
```