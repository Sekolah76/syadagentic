# Threads Auto-Post: Image Scraping & Upload Patterns

## 1. Scraping Authentic Product Images from Shopee
AI text-to-image models (like Flux) hallucinate product packaging. For affiliate posts, always scrape the authentic image from the Shopee URL instead of generating a fake one.

**Playwright Pattern:**
```python
# Navigate to shopee link, wait for DOM
page.goto(link, wait_until="domcontentloaded", timeout=15000)
page.wait_for_timeout(3000)

# Extract high-res image
img_srcs = page.evaluate("""() => {
    const imgs = document.querySelectorAll('img');
    return Array.from(imgs).map(i => i.src).filter(src => src.includes('susercontent.com') || src.includes('shopee.co.id/file/'));
}""")

# Clean thumbnail suffix (_tn or _cover)
if img_srcs:
    base_url = re.sub(r'_[a-zA-Z0-9]+$', '', img_srcs[0].split('?')[0])
    if base_url.endswith('_cover'):
        base_url = base_url[:-6]
    urllib.request.urlretrieve(base_url, "/tmp/threads_post_image.jpg")
```

## 2. Uploading Images to Threads via Playwright
Do NOT attempt to click the "Add media" UI button using `aria-label` or generic selectors. Threads translates these labels and frequently changes the DOM.

**Direct Input Targeting:**
Find the hidden file input that accepts images and set the file directly:
```python
# Target the first file input directly
file_input = page.locator('input[type="file"][accept*="image"]')
if file_input.count() > 0:
    file_input.first.set_input_files(image_path)
else:
    # Fallback to any file input
    page.locator('input[type="file"]').first.set_input_files(image_path)
```
