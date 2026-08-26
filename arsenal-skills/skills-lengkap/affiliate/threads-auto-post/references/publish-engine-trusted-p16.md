# Publish Engine — Trusted Profile 16 (2026-07-13)

## Why cookie Chromium alone fails
| Path | Typical result |
|------|----------------|
| Playwright + injected cookies (headless/headed) | Composer may type; **Kirim UI no-op** → Create mutation=0 |
| CDP on **default** Chrome user-data-dir | Chrome refuses DevTools: *remote debugging requires a non-default data directory* |
| AppleScript `execCommand('insertText')` + JS `.click()` | Text often **not** in React state; click untrusted → mutation=0 |
| Soft profile text match | False success / USED pollution |

## Engine order (locked in `cron_post.py`)
1. **`threads_post_applescript.py`** — Chrome Profile 16 live window  
   - Fill: **System Events paste** (`pbcopy` + cmd+v) — trusted input  
   - Send: score Kirim **y>300 x>700 first**, Quartz/OS mouse + Meta+Enter fallback  
   - Hook fetch/XHR for Create/Publish names  
   - Hard verify profile or mutation  
2. **`threads_post_p16_playwright.py`** — clone minimal P16 → `/tmp/chrome_threads_p16_ud`  
   - Non-default user-data so Chrome allows automation  
   - Playwright keyboard.type + mouse.click (trusted-ish)  
   - Clone Cookies/Network/Local Storage only; clear Singleton* locks  
3. **`threads_post_v6.py`** — legacy cookie inject (last resort)

Env override: `THREADS_FORCE_PLAYWRIGHT=1` → skip AS, use cookie PW path only (debug).

## Hard gate (same for all engines)
```text
success = create.mutation OR (hook_hit AND (link_hit OR prod_hit) AND body_len >= 120)
```
On fail: exit non-zero → `cron_post` must **not** mark USED / must not append history.

## Auth preflight before any engine
| Check | Pass |
|-------|------|
| P16 Threads UI | Logged-in feed; **not** guest / “Lanjutkan dengan Instagram” |
| Cookie `ds_user_id` | `3310347890` |
| `web_form_data` username | `jagonya_shopee` |
| Home after cookie inject | Not “halaman ini memang hilang” / broken link page |
| Threads vs IG ds | Equal — else **DROP** foreign Threads session, mirror IG |

Live fail class 2026-07-13: P16 guest + cookie file **expired** (ds present, session dead). Content layer OK; do not rebuild story engine.

## AppleScript operational notes
- `defaults write com.google.Chrome AllowJavascriptAppleEvents -bool true` **every run**; may reset after restart  
- Menu toggle if needed: View/Developer or **Lihat/Pengembang → Izinkan JavaScript dari Apple Events**  
- Always ensure **window count ≥ 1** before `active tab of front window` (-1719)  
- Put complex JS in **temp file** + `read POSIX file` (avoid AppleScript quote hell)  
- Lock: `fcntl` on `/tmp/chrome_applescript.lock`  
- JS `execute` does **not** await Promises — boot async → poll `window.__TH_PUB_DONE__`

## Cookie sanitize (`extract_threads_cookies.py`)
```text
if threads.ds != ig.ds → DROP threads session; mirror IG keys onto threads domains
EXPECTED_DS = 3310347890 (@jagonya_shopee)
```
Never let foreign Threads `sessionid` override jagonya.

## Resume checklist
1. SYADAGENTIC login `@jagonya_shopee` on Chrome **Profile 16** (Threads feed OK)
2. `python3 ~/.hermes/scripts/extract_threads_cookies.py`
3. Identity assert (`auth-preflight-jagonya.md`)
4. Live: `python3 ~/.hermes/scripts/cron_post.py` (or AS script + content JSON)
5. Require mutation or hard profile proof
6. Only then unpause cron `23199a7b2d5b` (+ cookie refresh)

## Do NOT
- Unpause cron while session dead / guest P16  
- Mark USED without mutation or hook+link/product  
- Prefer top-bar Kirim (y≈114) over bottom (y>300)  
- Launch persistent context on default Chrome user-data-dir expecting CDP  
- Trust soft hook-only profile match  
