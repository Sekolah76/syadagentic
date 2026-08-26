# Playwright Contenteditable Patterns for Threads

## Key Findings (2026-06-11)

### 1. Editor Detection
Threads uses Lexical editor with multiple possible selectors:
- `[contenteditable="true"]` — most reliable, use first
- `[data-lexical-editor="true"]` — Lexical-specific
- `div[role="textbox"]` — accessibility selector

**Retry pattern:** 7 attempts × 2s = 15s total wait. Take screenshot on failure.

### 2. Line Breaks
`page.keyboard.type("text\nlink")` does NOT create proper line breaks in Lexical.

**Fix:** Split on `\n`, type each line separately, `page.keyboard.press("Enter")` between.

```python
lines = text.split("\n")
for j, line in enumerate(lines):
    page.keyboard.type(line, delay=30)
    if j < len(lines) - 1:
        page.keyboard.press("Enter")
        time.sleep(0.5)
```

### 3. URL Detection (UNRESOLVED)
Threads' URL detection is unreliable with automated input:

| Method | Result |
|--------|--------|
| `page.keyboard.type(url, delay=20)` | Link in editor, but stripped from published post |
| `page.keyboard.type(url, delay=80)` | Same — editor shows link, post has none |
| `execCommand('insertText')` | Inserts text but Threads doesn't detect as URL |
| `ClipboardEvent('paste')` | Paste event dispatched but link not inserted |

**Pre-send verify:** `editors.nth(N).inner_text()` shows link is present, but Threads strips it on publish.

**Status:** UNRESOLVED (2026-06-11). Possible causes:
- Threads bot detection filtering URLs from Playwright sessions
- Lexical editor requires specific event sequence for URL recognition
- Threads server-side URL stripping for automated posts

### 4. Add to Thread Loop
```python
for i in range(1, num_posts):
    editors_before = page.locator('[contenteditable="true"]').count()
    click_add_to_thread(page, i)
    time.sleep(3)
    editors_after = page.locator('[contenteditable="true"]').count()
    
    if editors_after <= editors_before:
        # Retry
        click_add_to_thread(page, i)
        time.sleep(3)
    
    editors.nth(i).click()
    page.keyboard.type(post_text, delay=30)
```

**⚠️ PLATFORM LIMIT:** Threads hard-limits to 3 posts per thread session. "Add to thread" clicks 4+ report success but Threads silently drops extra posts on publish.

### 5. Pre-Send Verification
```python
editors = page.locator('[contenteditable="true"]')
last_text = editors.nth(num_posts - 1).inner_text()
if affiliate_link not in last_text:
    # Re-type link
    editors.nth(num_posts - 1).click()
    page.keyboard.press("End")
    page.keyboard.press("Enter")
    time.sleep(1)
    page.keyboard.type(affiliate_link, delay=100)
```

### 6. Send Button
```python
# Try EN first, then ID
try:
    page.locator('div[role="button"]:has-text("Post")').last.click(force=True)
except:
    page.locator('div[role="button"]:has-text("Kirim")').last.click(force=True)
```
