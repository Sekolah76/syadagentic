# Threads Auto-Post v4 — Working Playwright Script

## Overview
This is the **verified working method** for posting 3-post affiliate threads to Threads.
Saved 2026-05-25 after testing confirmed success.

## Why This Script Works
1. **`context.add_cookies()`** CAN set httpOnly cookies (sessionid, ig_did, etc.)
2. **`document.cookie`** CANNOT set httpOnly cookies — browser tool fails because of this
3. Prefer Playwright cookie inject; CDP Chrome only when intentionally launched with remote debugging (do not assume port 9222 always up)
4. **Kirim path (updated 2026-07-12):** bottom-right Kirim (`y>300`,`x>700`) first, then `has-text("Kirim").last.click(force=True)`. Never prefer `has-text("Post").last` (false feed matches). See `references/kirim-publish-hard-verify.md`.

## Cookie Injection Flow
```
browser_cookie3.chrome(domain_name='.instagram.com')
    ↓
Raw cookies extracted from Chrome Profile 16
    ↓
Clean control chars (re.sub r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
    ↓
context.add_cookies() with httpOnly flag
    ↓
Navigate to instagram.com → verify logged in
```

## Key Fixes Applied
| Issue | Broken Method | Working Method |
|-------|---------------|----------------|
| httpOnly cookies | `document.cookie` | `context.add_cookies()` |
| "Lanjutkan" button | Playwright `.click()` | JS `span.parentElement.click()` |
| "Tambahkan ke utas" | Playwright `browser_click` | JS `el.click()` |
| "Kirim" button | `__reactProps.onClick()` alone / `Post.last` first | Bottom-right Kirim (`y>300`,`x>700`) then `has-text("Kirim").last.click(force=True)` |
| Publish success claim | UI click / soft HTML profile match | GraphQL Create/Publish mutation **or** strict `inner_text` unique snip |
| "Buat" button | `page.click('text=Buat')` | `page.get_by_role("button", name="Buat")` / `[aria-label="Buat"]` |
| SSO Auth Loop / Mismatch | Injecting `.threads.com` only | Injecting `.instagram.com` AND `.threads.com`; identity assert `ds=3310347890` + username jagonya |
| Headless Composer Missing | Triggering `page.keyboard.press("n")` or clicking side menus | Logging in via `threads.com/login` → feed → active `[contenteditable="true"]` |

## Script Location
`~/.hermes/scripts/threads_post_v6.py` (canonical executor; history under `~/.hermes/scripts/`)

## Running Manually
```bash
cd ~/.hermes/scripts
uv run python3 threads_post_v4.py
```

## Debugging Tips
1. Use `headless=False` during development
2. Check screenshots in `/tmp/debug_after_send.png`, `/tmp/debug_editor.png`
3. If post not visible after Kirim → **check network for Create/Publish mutation** (click alone is not success)
4. If "Lanjutkan" / signup wall → cookies wrong/expired; re-extract Profile 16 + identity assert (`auth-preflight-jagonya.md`)
5. Soft profile HTML match without mutation → false success; revert history/USED (see `kirim-publish-hard-verify.md`)
