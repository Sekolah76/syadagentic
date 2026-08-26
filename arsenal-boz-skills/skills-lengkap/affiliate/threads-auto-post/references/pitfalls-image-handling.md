# Threads Image Handling & Playwright Pitfalls

## 1. Avoid AI Image Generation for Affiliate Products
AI Text-to-Image models (e.g., Flux, Gemini) hallucinate product packaging, resulting in images that do not accurately represent the physical affiliate product. 
**Solution:** Do not use AI to generate product photos. Instead, use Playwright to navigate to the Shopee affiliate link, extract the actual product image URL (typically from `susercontent.com` or `cf.shopee.co.id/file/`), download it, and use that real image for the post.

## 2. Playwright Image Uploads on Threads
Attempting to locate and click the "Add Media" or "BOZlery" icon on the Threads UI is highly unreliable. The DOM structure and ARIA labels change frequently, leading to `TimeoutError` or clicking the wrong element.
**Solution:** Bypass the UI button entirely. Target the hidden file input element directly and set the files:
```python
file_input = page.locator('input[type="file"][accept*="image"]')
if file_input.count() > 0:
    file_input.first.set_input_files(image_path)
```