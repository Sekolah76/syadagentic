#!/usr/bin/env python3
"""Threads Auto-Post v8 — 3-post max + proper link insertion via clipboard paste."""

import json
import os
import sys
import time
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
# ALWAYS use canonical history under ~/.hermes/scripts (not skill dir)
HISTORY_FILE = Path.home() / ".hermes/scripts/threads_post_history.json"

def load_history():
    if HISTORY_FILE.exists():
        data = json.loads(HISTORY_FILE.read_text())
        if isinstance(data, dict) and "posts" in data:
            return data["posts"]
        elif isinstance(data, list):
            return data
    return []

def save_history(posts):
    posts = posts[-50:]
    HISTORY_FILE.write_text(json.dumps({"posts": posts}, indent=2, ensure_ascii=False))

def check_dedup(posts, affiliate_link, hook_category, hook_text):
    """Hard dedup: link forever (in history window), story type last 3, hook phrasing last 8."""
    used_links = {p.get("affiliate_link") for p in posts if p.get("affiliate_link")}
    if affiliate_link in used_links:
        return False, f"Link already used: {affiliate_link}"
    # story_type / hook_category rotation — no repeat in last 3
    recent_story = [
        (p.get("story_type") or p.get("hook_category") or "")
        for p in posts[-3:]
    ]
    if hook_category and hook_category in recent_story:
        return False, f"Story type '{hook_category}' used in last 3 posts"
    # product category rotation soft-check (last 1 must differ if present)
    hook_words = set(hook_text[:60].lower().split())
    for p in posts[-8:]:
        prev = (p.get("hook_text", "") or "")[:60].lower()
        prev_words = set(prev.split())
        if hook_words and prev_words:
            overlap = len(hook_words & prev_words) / max(len(hook_words), 1)
            if overlap > 0.55:
                return False, f"Hook too similar to recent post (overlap={overlap:.0%})"
    return True, "OK"

def extract_posts(content):
    """Extract all posts from content dict. Supports post_1 through post_N."""
    posts = []
    i = 1
    while True:
        key = f"post_{i}"
        if key in content and content[key].strip():
            posts.append(content[key].strip())
            i += 1
        else:
            break
    return posts

def click_add_to_thread(page, attempt):
    """Click 'Add to thread' / 'Tambahkan ke utas'."""
    result = page.evaluate("""() => {
        const safeClick = (el) => {
            if (!el) return false;
            const target = (el.closest && el.closest('div[role="button"], button, a')) || el;
            try {
                if (target && typeof target.click === 'function') { target.click(); return true; }
                target.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
                return true;
            } catch (e) { return false; }
        };
        for (const el of document.querySelectorAll('span, div[role="button"], button')) {
            const txt = (el.textContent || '').trim();
            if (txt === "Add to thread" || txt === "Tambahkan ke utas") {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0 && rect.y > 0 && safeClick(el)) {
                    return "clicked: " + txt;
                }
            }
        }
        return "not_found";
    }""")
    print(f"Add to thread ({attempt}): {result}")
    return result

def paste_text(page, text):
    """Paste text via clipboard — works better for URLs than keyboard.type()."""
    page.evaluate("""
        async (text) => {
            try {
                await navigator.clipboard.writeText(text);
            } catch(e) {
                // Fallback: create temp textarea
                const ta = document.createElement('textarea');
                ta.value = text;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
            }
        }
    """, text)
    time.sleep(0.3)
    # Cmd+V on Mac
    page.keyboard.press("Meta+v")
    time.sleep(1)

def type_text(page, text, delay=30):
    """Type text handling newlines as explicit Enter presses."""
    lines = text.split("\n")
    for j, line in enumerate(lines):
        page.keyboard.type(line, delay=delay)
        if j < len(lines) - 1:
            page.keyboard.press("Enter")
            time.sleep(0.5)

def main():
    # Load content from JSON file or env vars
    if len(sys.argv) > 1:
        content = json.loads(Path(sys.argv[1]).read_text())
    else:
        content = {
            "post_1": os.environ.get("THREADS_POST_1", ""),
            "post_2": os.environ.get("THREADS_POST_2", ""),
            "post_3": os.environ.get("THREADS_POST_3", ""),
            "affiliate_link": os.environ.get("THREADS_AFFILIATE_LINK", ""),
            "product_name": os.environ.get("THREADS_PRODUCT_NAME", ""),
            "hook_category": os.environ.get("THREADS_HOOK_CATEGORY", ""),
            "hook_text": os.environ.get("THREADS_KEYWORDS", "").split(",")[0] if os.environ.get("THREADS_KEYWORDS") else "",
            "keywords": os.environ.get("THREADS_KEYWORDS", "").split(","),
            "image_path": os.environ.get("THREADS_IMAGE_PATH", ""),
        }

    # Extract posts — max 3 (Threads limit)
    posts_content = extract_posts(content)
    if len(posts_content) < 2:
        print("ERROR: Need at least 2 posts")
        sys.exit(1)
    if len(posts_content) > 3:
        print(f"⚠️ Threads max 3 posts. Truncating {len(posts_content)} → 3")
        posts_content = posts_content[:3]

    affiliate_link = content["affiliate_link"]
    product_name = content["product_name"]
    hook_category = content["hook_category"]
    hook_text = content.get("hook_text", posts_content[0][:80])
    keywords = content.get("keywords", [])
    image_path = content.get("image_path", "")

    # Load history & dedup
    history = load_history()
    ok, reason = check_dedup(history, affiliate_link, hook_category, hook_text)
    if not ok:
        print(f"DEDUP REJECTED: {reason}")
        sys.exit(1)

    # Load cookies (IG primary + optional Threads cookies)
    cookie_file = Path.home() / "instagram_cookies.json"
    raw_cookies = json.loads(cookie_file.read_text())
    cookies = {k: re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(v)) for k, v in raw_cookies.items()}
    threads_cookie_file = Path.home() / "threads_cookies.json"
    threads_cookies = {}
    if threads_cookie_file.exists():
        try:
            threads_cookies = {
                k: re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(v))
                for k, v in json.loads(threads_cookie_file.read_text()).items()
                if v
            }
        except Exception:
            threads_cookies = {}

    num_posts = len(posts_content)
    print(f"Starting Threads post: {product_name}")
    print(f"Format: {num_posts}-post COMBO thread")
    print(f"Hook: {hook_text[:60]}...")
    print(f"Link: {affiliate_link}")
    print(f"Cookies: IG={len(cookies)} TH={len(threads_cookies)} ds={cookies.get('ds_user_id')}")

    from playwright.sync_api import sync_playwright

    create_ok = {"mutation": False, "name": None, "status": None, "body": ""}
    verified = False
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
            ),
            locale="id-ID",
        )

        # Grant clipboard permissions
        context.grant_permissions(["clipboard-read", "clipboard-write"])

        # Inject IG cookies to IG + Threads domains (SSO needs both)
        pw_cookies = []
        http_only = {'sessionid', 'ig_did', 'datr', 'mid', 'rur', 'ig_nrcb', 'ps_l', 'ps_n'}
        for name, value in cookies.items():
            if not value:
                continue
            for domain, same_site in [(".instagram.com", "Lax"), (".threads.com", "None"), (".threads.net", "None")]:
                pw_cookies.append({
                    "name": name,
                    "value": value,
                    "domain": domain,
                    "path": "/",
                    "httpOnly": name in http_only,
                    "secure": True,
                    "sameSite": same_site,
                })
        # native threads cookies override mirrored IG values on .threads.com
        for name, value in threads_cookies.items():
            if not value:
                continue
            pw_cookies.append({
                "name": name,
                "value": value,
                "domain": ".threads.com",
                "path": "/",
                "httpOnly": name in http_only,
                "secure": True,
                "sameSite": "None",
            })
        context.add_cookies(pw_cookies)

        page = context.new_page()

        def dismiss_auth_modals():
            return page.evaluate("""
                () => {
                  const texts = [
                    'Not now', 'Nanti saja', 'Lain Kali', 'Tutup', 'Close',
                    'Maybe later', 'Lewati', 'Skip'
                  ];
                  const safeClick = (el) => {
                    if (!el) return false;
                    const target = (el.closest && el.closest('div[role="button"], button, a')) || el;
                    try {
                      if (target && typeof target.click === 'function') { target.click(); return true; }
                      target.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
                      return true;
                    } catch (e) { return false; }
                  };
                  let clicked = [];
                  for (const el of document.querySelectorAll('div[role="button"], button, span, [aria-label]')) {
                    const t = (el.textContent || el.getAttribute('aria-label') || '').trim();
                    if (texts.includes(t)) {
                      const r = el.getBoundingClientRect();
                      if (r.width > 0 && r.height > 0 && safeClick(el)) clicked.push(t);
                    }
                  }
                  return clicked;
                }
            """)

        def click_sso_if_needed():
            # Playwright text locators first
            for sel in [
                'text=Continue with Instagram',
                'text=Lanjutkan dengan Instagram',
                'div[role="button"]:has-text("Continue with Instagram")',
                'div[role="button"]:has-text("Lanjutkan dengan Instagram")',
            ]:
                loc = page.locator(sel)
                if loc.count() > 0:
                    try:
                        loc.first.click(timeout=4000)
                        return f"clicked:{sel}"
                    except Exception:
                        pass
            return page.evaluate("""
                () => {
                  const safeClick = (el) => {
                    if (!el) return false;
                    const target = (el.closest && el.closest('div[role="button"], button, a')) || el;
                    try {
                      if (target && typeof target.click === 'function') { target.click(); return true; }
                      target.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
                      return true;
                    } catch (e) { return false; }
                  };
                  for (const el of document.querySelectorAll('div[role="button"], button, span, a')) {
                    const txt = (el.textContent || '').trim();
                    if (
                      txt === 'Continue with Instagram' ||
                      txt === 'Lanjutkan dengan Instagram' ||
                      txt.startsWith('Continue as') ||
                      txt.startsWith('Lanjutkan sebagai') ||
                      txt.includes('Lanjutkan dengan Instagram')
                    ) {
                      const rect = el.getBoundingClientRect();
                      if (rect.width > 0 && rect.height > 0 && safeClick(el)) {
                        return 'clicked: ' + txt.slice(0,80);
                      }
                    }
                  }
                  return 'not_found';
                }
            """)

        def open_composer():
            # try multiple compose entry points
            for sel in [
                '[aria-label="Create"]',
                '[aria-label="Buat"]',
                'svg[aria-label="Create"]',
                'svg[aria-label="Buat"]',
                'a[href*="compose"]',
            ]:
                loc = page.locator(sel)
                if loc.count() > 0:
                    try:
                        loc.first.click(timeout=3000, force=True)
                        return f"clicked:{sel}"
                    except Exception as e:
                        print(f"compose click fail {sel}: {e}")
            return page.evaluate("""
                () => {
                  const safeClick = (el, tag) => {
                    if (!el) return null;
                    const target = (el.closest && el.closest('div[role="button"], a, button')) || el;
                    try {
                      if (target && typeof target.click === 'function') { target.click(); return tag; }
                      target.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
                      return tag;
                    } catch (e) { return null; }
                  };
                  for (const s of ['a[href*="compose"]','[aria-label="New thread"]','[aria-label="Buat"]','[aria-label="Create"]','svg[aria-label="Create"]','svg[aria-label="Buat"]']) {
                    const r = safeClick(document.querySelector(s), s);
                    if (r) return r;
                  }
                  for (const el of document.querySelectorAll('div[role="button"], button, a, span')) {
                    const txt = (el.textContent || '').trim();
                    if (txt === 'New thread' || txt === 'Utas baru' || txt === 'Buat' || txt === 'Create') {
                      const rect = el.getBoundingClientRect();
                      if (rect.width > 0 && rect.height > 0 && rect.height < 100) {
                        const r = safeClick(el, 'text:' + txt);
                        if (r) return r;
                      }
                    }
                  }
                  return 'not_found';
                }
            """)

        # Warm Instagram session first
        print("Navigating to Instagram...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=45000)
        time.sleep(3)
        dismiss_auth_modals()
        print(f"IG url: {page.url}")

        # Threads login / SSO
        print("Navigating to Threads login...")
        page.goto("https://www.threads.com/login", wait_until="domcontentloaded", timeout=45000)
        time.sleep(4)
        sso = click_sso_if_needed()
        print(f"SSO button: {sso}")
        # handle possible IG oauth / onboarding redirects
        for i in range(12):
            time.sleep(2)
            url = page.url
            print(f"SSO step{i}: {url[:140]}")
            dismiss_auth_modals()
            # finish onboarding privacy step if present
            for t in ["Berikutnya", "Next", "Selesai", "Done", "Continue", "Lanjutkan"]:
                loc = page.locator(f'text={t}')
                if loc.count() > 0 and ("onboarding" in url or "login" in url):
                    try:
                        loc.first.click(timeout=2000)
                        print(f"onboarding click: {t}")
                    except Exception:
                        pass
            if "threads.com" in url and "login" not in url and "onboarding" not in url and "oidc" not in url:
                break
            # keep clicking SSO if still gated
            if "login" in url or "Sign up" in (page.content()[:2000] if False else ""):
                click_sso_if_needed()

        # Navigate to feed
        print("Navigating to Threads feed...")
        page.goto("https://www.threads.com/", wait_until="domcontentloaded", timeout=45000)
        time.sleep(4)
        dismiss_auth_modals()
        html_probe = page.content()
        if "Sign up to post" in html_probe or "Katakan lebih banyak dengan Threads" in html_probe:
            print("Auth wall still present — retry SSO from modal")
            sso2 = click_sso_if_needed()
            print(f"SSO modal: {sso2}")
            time.sleep(8)
            page.goto("https://www.threads.com/", wait_until="domcontentloaded", timeout=45000)
            time.sleep(4)
            dismiss_auth_modals()
            html_probe = page.content()
        if "Sign up to post" in html_probe or "Katakan lebih banyak dengan Threads" in html_probe:
            page.screenshot(path="/tmp/debug_editor.png")
            print("ERROR: Still logged out on Threads after SSO")
            browser.close()
            sys.exit(1)
        print(f"Threads feed ready: {page.url}")

        # Allow custom starting URL for thread series
        target_url = content.get("target_url", os.environ.get("THREADS_TARGET_URL", ""))
        if target_url:
            print(f"Navigating to target URL for chain post: {target_url}")
            page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            # Reply to the specific thread instead of 'New thread'
            reply_btn_clicked = page.evaluate("""() => {
                const safeClick = (el) => {
                    if (!el) return false;
                    const target = (el.closest && el.closest('div[role=\"button\"], button, a')) || el;
                    try {
                        if (target && typeof target.click === 'function') { target.click(); return true; }
                        target.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
                        return true;
                    } catch (e) { return false; }
                };
                for (const el of document.querySelectorAll('div[role="button"], span[role="button"], button')) {
                    const txt = (el.textContent || '').trim();
                    if (/^(Balas|Reply)/.test(txt) && safeClick(el)) return true;
                }
                return false;
            }""")
            print(f"Reply button clicked: {reply_btn_clicked}")
            time.sleep(5)
        else:
            # Open composer via multi-selector helper
            new_thread_result = open_composer()
            print(f"New thread button: {new_thread_result}")
            time.sleep(4)
            # if still no editor path, retry once after dismiss
            dismiss_auth_modals()
            if page.locator('[contenteditable="true"]').count() == 0:
                new_thread_result = open_composer()
                print(f"New thread retry: {new_thread_result}")
                time.sleep(4)

        # Wait for editor to appear (visible only)
        editor = None
        for attempt in range(12):
            loc = page.locator('[contenteditable="true"]:visible, [data-lexical-editor="true"]:visible, div[role="textbox"]:visible')
            if loc.count() == 0:
                # fallback without :visible
                loc = page.locator('[contenteditable="true"], [data-lexical-editor="true"], div[role="textbox"]')
            # pick first visible
            for idx in range(loc.count()):
                cand = loc.nth(idx)
                try:
                    if cand.is_visible():
                        editor = cand
                        print(f"Editor found visible idx={idx} (attempt {attempt+1})")
                        break
                except Exception:
                    continue
            if editor:
                break
            if attempt in (2, 5, 8):
                dismiss_auth_modals()
                print(f"Re-open composer mid-wait: {open_composer()}")
            time.sleep(2)
            print(f"Waiting for editor... attempt {attempt+1}")

        if not editor:
            page.screenshot(path="/tmp/debug_editor.png")
            print("ERROR: No visible editor found after wait.")
            browser.close()
            sys.exit(1)

        def focus_editor(ed):
            """Force-focus lexical editor even if Playwright visibility is flaky."""
            try:
                ed.click(timeout=3000, force=True)
                return "force_click"
            except Exception as e1:
                try:
                    ed.evaluate("""el => { el.scrollIntoView({block:'center'}); el.focus(); }""")
                    page.mouse.click(640, 360)
                    return f"js_focus_after:{type(e1).__name__}"
                except Exception as e2:
                    return f"focus_fail:{type(e1).__name__}/{type(e2).__name__}"

        # Iterate all posts dynamically
        for i in range(num_posts):
            if i > 0:
                # Add to thread for posts 2, 3, etc.
                editors_before = page.locator('[contenteditable="true"]').count()
                click_add_to_thread(page, i)
                time.sleep(3)

                editors = page.locator('[contenteditable="true"]')
                editors_count = editors.count()
                print(f"Editors before: {editors_before}, after: {editors_count}")

                if editors_count <= editors_before:
                    print(f"⚠️ Retrying Add to thread...")
                    click_add_to_thread(page, i)
                    time.sleep(3)
                    editors_count = page.locator('[contenteditable="true"]').count()

                if i >= editors_count:
                    print(f"❌ Editor {i} doesn't exist (only {editors_count})")
                    break

                print("focus", focus_editor(editors.nth(i)))
                time.sleep(0.5)
            else:
                print("focus", focus_editor(editor))
                time.sleep(0.5)

            post_text = posts_content[i]

            # Last post: CTA text + paste link via clipboard
            if i == num_posts - 1:
                cta_text = post_text
                link_in_post = ""

                # Cek kalo link di-append pake newline (format lama)
                if "https://s.shopee.co.id/" in post_text:
                    parts = post_text.split("https://s.shopee.co.id/")
                    cta_text = parts[0].strip()
                    link_in_post = "https://s.shopee.co.id/" + parts[1].split("\n")[0].strip()

                actual_link = link_in_post if link_in_post else affiliate_link

                # Type CTA text - ONLY if it's not empty
                if cta_text:
                    type_text(page, cta_text)
                    time.sleep(1)

                # Cuma add blank line kalau ada teks CTA sebelumnya
                if cta_text:
                    page.keyboard.press("Enter")
                    time.sleep(0.5)

                # PASTE link via clipboard
                paste_text(page, actual_link)
                time.sleep(3)

                print(f"POST {i+1}/{num_posts}: CTA + pasted link: {actual_link}")
            else:
                type_text(page, post_text)
                print(f"POST {i+1}/{num_posts} typed: {post_text[:50]}...")

            time.sleep(1)

        # VERIFY: Check if link is in last editor
        editors = page.locator('[contenteditable="true"]')
        num_editors = editors.count()
        print(f"Total editors: {num_editors}")

        # prefer last visible editor
        last_idx = max(0, min(num_posts - 1, num_editors - 1))
        try:
            last_editor_text = editors.nth(last_idx).inner_text(timeout=5000)
        except Exception:
            last_editor_text = page.evaluate("""() => {
              const eds=[...document.querySelectorAll('[contenteditable="true"]')];
              return eds.length ? (eds[eds.length-1].innerText || '') : '';
            }""")
        print(f"Last editor text: {repr(last_editor_text)}")

        if affiliate_link not in last_editor_text:
            print(f"⚠️ Link NOT in editor! Retrying with type...")
            try:
                focus_editor(editors.nth(last_idx))
            except Exception:
                pass
            time.sleep(0.5)
            page.keyboard.press("End")
            time.sleep(0.3)
            page.keyboard.press("Enter")
            time.sleep(0.5)
            paste_text(page, affiliate_link)
            time.sleep(2)
            try:
                last_editor_text = editors.nth(last_idx).inner_text(timeout=5000)
            except Exception:
                last_editor_text = page.evaluate("""() => {
                  const eds=[...document.querySelectorAll('[contenteditable="true"]')];
                  return eds.length ? (eds[eds.length-1].innerText || '') : '';
                }""")
            print(f"After paste retry: {repr(last_editor_text)}")

            if affiliate_link not in last_editor_text:
                print(f"⚠️ Paste failed, trying keyboard.type...")
                page.keyboard.type(affiliate_link, delay=80)
                time.sleep(3)
                try:
                    last_editor_text = editors.nth(last_idx).inner_text(timeout=5000)
                except Exception:
                    last_editor_text = ""
                print(f"After type retry: {repr(last_editor_text)}")

        # Final check
        if affiliate_link not in (last_editor_text or ""):
            print(f"❌ Link still missing after all retries!")
        else:
            print(f"✅ Link confirmed in editor")

        # Upload image if available
        if image_path and Path(image_path).exists():
            try:
                img_btn = page.evaluate("""() => {
                    for (const el of document.querySelectorAll('div[role="button"], button, svg')) {
                        const label = el.getAttribute('aria-label') || '';
                        if (label.toLowerCase().includes('photo') || label.toLowerCase().includes('image') || label.toLowerCase().includes('media')) {
                            el.click();
                            return "clicked: " + label;
                        }
                    }
                    return "not_found";
                }""")
                print(f"Image button: {img_btn}")
                time.sleep(2)

                file_input = page.locator('input[type="file"]').first
                if file_input:
                    file_input.set_input_files(image_path)
                    print(f"Image uploaded: {image_path}")
                    time.sleep(5)
            except Exception as e:
                print(f"Image upload failed (continuing without): {e}")

        # Click Send — OLD WORKING METHOD (skill refs):
        # - kirim_btn.click(force=True) is the ONLY reliable path
        # - use .last (not first) — feed has dead "Kirim" at top
        # - prefer bottom-right (y>300, x>700) when multiple Kirim exist
        create_ok = {"mutation": False, "name": None, "status": None, "body": ""}

        def on_request(req):
            try:
                if req.method != "POST" or "threads.com" not in req.url:
                    return
                body = req.post_data or ""
                m = re.search(r"fb_api_req_friendly_name=([^&]+)", body)
                name = m.group(1) if m else ""
                if name and re.search(r"Create|Publish|PostMedia|TextPost|Configure|Barcelona.*Create|create", name, re.I):
                    create_ok["mutation"] = True
                    create_ok["name"] = name
            except Exception:
                pass

        def on_response(resp):
            try:
                req = resp.request
                if req.method != "POST" or "threads.com" not in resp.url:
                    return
                body = req.post_data or ""
                m = re.search(r"fb_api_req_friendly_name=([^&]+)", body)
                name = m.group(1) if m else ""
                if name and re.search(r"Create|Publish|PostMedia|TextPost|Configure|Barcelona.*Create|create", name, re.I):
                    create_ok["mutation"] = True
                    create_ok["name"] = name
                    create_ok["status"] = resp.status
                    try:
                        create_ok["body"] = (resp.text() or "")[:500]
                    except Exception:
                        create_ok["body"] = ""
            except Exception:
                pass

        page.on("request", on_request)
        page.on("response", on_response)

        # Dump candidates for debug (position filter from skill: y>300, x>700)
        send_meta = page.evaluate(
            """() => {
              const isSend = (t) => {
                const s = (t || '').trim();
                return s === 'Kirim' || s === 'Post' || s === 'Posting' || s === 'Bagikan sekarang';
              };
              const cands = [];
              for (const el of document.querySelectorAll('div[role="button"], button')) {
                const t = (el.innerText || el.textContent || '').trim();
                if (!isSend(t)) continue;
                const r = el.getBoundingClientRect();
                if (r.width < 30 || r.height < 15 || r.width === 0) continue;
                cands.push({
                  t, x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2),
                  w: Math.round(r.width), h: Math.round(r.height),
                  disabled: el.getAttribute('aria-disabled') || String(!!el.disabled),
                  score: (r.y > 300 ? 100 : 0) + (r.x > 700 ? 50 : 0) + (r.y > 500 ? 20 : 0)
                });
              }
              cands.sort((a,b) => b.score - a.score);
              return cands;
            }"""
        )
        print(f"Send candidates (scored): {send_meta}")

        clicked = False
        # 1) REAL composer Kirim: bottom-right only (skill: y>300, x>700)
        #    NEVER use has-text("Post").last first — feed has many false "Post"/repost nodes
        for cand in send_meta or []:
            if str(cand.get("disabled")).lower() in ("true", "1"):
                continue
            if cand.get("score", 0) < 100:  # must be y>300
                continue
            try:
                page.mouse.click(cand["x"], cand["y"], delay=50)
                print(f"Send POS-PATH mouse: {cand}")
                clicked = True
                break
            except Exception as e:
                print(f"Send POS-PATH mouse fail {cand}: {e}")

        # 2) Playwright locator Kirim only (ID locale) — .last among Kirim
        if not clicked:
            for label in ("Kirim", "Posting", "Post"):
                try:
                    loc = page.locator(f'div[role="button"]:has-text("{label}")')
                    n = loc.count()
                    print(f"locator has-text({label}) count={n}")
                    if n == 0:
                        continue
                    # Prefer last for Kirim (composer), but for Post only if no Kirim
                    if label == "Post" and any(
                        (c.get("t") == "Kirim" and c.get("score", 0) >= 100) for c in (send_meta or [])
                    ):
                        continue
                    loc.last.click(force=True, timeout=5000)
                    print(f"Send LOC-PATH: div[role=button]:has-text({label}).last force=True")
                    clicked = True
                    break
                except Exception as e:
                    print(f"Send LOC-PATH fail {label}: {e}")

        # 3) JS click on bottom-right exact-text Kirim button
        if not clicked:
            js = page.evaluate(
                """() => {
                  const isSend = (t) => {
                    const s = (t || '').trim();
                    return s === 'Kirim' || s === 'Post' || s === 'Posting';
                  };
                  const nodes = [...document.querySelectorAll('div[role="button"], button')];
                  let best = null, bestScore = -1;
                  for (const el of nodes) {
                    const t = (el.innerText || '').trim();
                    if (!isSend(t)) continue;
                    const r = el.getBoundingClientRect();
                    if (r.width < 30 || r.height < 15) continue;
                    const score = (r.y > 300 ? 100 : 0) + (r.x > 700 ? 50 : 0) + (r.y > 500 ? 20 : 0);
                    if (score > bestScore) { bestScore = score; best = el; }
                  }
                  if (!best || bestScore < 100) return {ok:false, score:bestScore};
                  best.click();
                  const r = best.getBoundingClientRect();
                  return {ok:true, t:(best.innerText||'').trim(), x:r.x, y:r.y, score:bestScore};
                }"""
            )
            print(f"Send JS-PATH: {js}")
            if isinstance(js, dict) and js.get("ok"):
                clicked = True

        # 4) Meta+Enter (composer shortcut)
        if not clicked:
            try:
                eds = page.locator('[contenteditable="true"]')
                if eds.count():
                    eds.last.click(force=True)
                page.keyboard.press("Meta+Enter")
                print("Send fallback: Meta+Enter")
                clicked = True
            except Exception as e:
                print(f"Meta+Enter fail: {e}")

        if not clicked:
            page.screenshot(path="/tmp/debug_send.png")
            print("ERROR: No send button clickable")
            browser.close()
            sys.exit(1)

        print("Send clicked — waiting create mutation...")
        for _ in range(20):
            if create_ok["mutation"]:
                break
            time.sleep(1)

        # If still no mutation, retry .last force once more + Meta+Enter
        if not create_ok["mutation"]:
            print("No mutation yet — retry Kirim.last + Meta+Enter")
            try:
                page.locator('div[role="button"]:has-text("Kirim")').last.click(force=True, timeout=3000)
            except Exception:
                try:
                    page.locator('div[role="button"]:has-text("Post")').last.click(force=True, timeout=3000)
                except Exception:
                    pass
            try:
                page.keyboard.press("Meta+Enter")
            except Exception:
                pass
            for _ in range(12):
                if create_ok["mutation"]:
                    break
                time.sleep(1)

        page.screenshot(path="/tmp/debug_after_send.png")
        print(f"Create mutation: {create_ok}")

        # Verify on profile — STRICT: require hook snippet OR product + not generic page chrome
        page.goto("https://www.threads.com/@jagonya_shopee", wait_until="domcontentloaded", timeout=30000)
        time.sleep(6)
        for _ in range(4):
            page.mouse.wheel(0, 1200)
            time.sleep(1)
        body_text = page.inner_text("body")
        page_html = page.content()
        hook_snip = (hook_text or "")[:24]
        prod_snip = (product_name or "")[:18]
        link_tail = affiliate_link.rstrip("/").split("/")[-1]
        verified = bool(
            (hook_snip and (hook_snip in body_text or hook_snip in page_html))
            or (prod_snip and len(prod_snip) >= 8 and (prod_snip in body_text or prod_snip in page_html))
            or (link_tail and link_tail in body_text)
        )
        # Guard: if only mutation missing and body is tiny/login, force fail
        if verified and len(body_text) < 80:
            verified = False
        print("✅ Post verified on profile!" if verified else "⚠️ Post not visible on profile")
        print(f"Verify snips hook={hook_snip!r} prod={prod_snip!r} link_tail={link_tail!r} body_len={len(body_text)}")

        browser.close()

    # HARD success: mutation preferred; profile text alone only if unique snip present
    success = bool(create_ok.get("mutation") or verified)
    if not success:
        print("❌ HARD FAIL: no create mutation and not on profile — not writing history/USED")
        Path("/tmp/threads_post_result.json").write_text(
            json.dumps(
                {
                    "status": "failed",
                    "reason": "send_no_create_mutation",
                    "create": create_ok,
                    "product": product_name,
                    "link": affiliate_link,
                    "story_type": content.get("story_type") or hook_category,
                    "category": content.get("category", ""),
                    "date": time.strftime("%Y-%m-%dT%H:%M"),
                },
                indent=2,
            )
        )
        sys.exit(1)

    # If only "verified" without mutation, still accept but flag soft
    if not create_ok.get("mutation") and verified:
        print("⚠️ SUCCESS soft: profile text match without create mutation name")

    # Record to history (canonical path) ONLY after hard success
    category = content.get("category", "")
    story_type = content.get("story_type") or hook_category
    new_entry = {
        "date": time.strftime("%Y-%m-%dT%H:%M"),
        "hook_category": hook_category,
        "story_type": story_type,
        "category": category,
        "hook_text": hook_text[:80],
        "product": product_name,
        "affiliate_link": affiliate_link,
        "keywords": keywords,
        "num_posts": num_posts,
        "content_mode": content.get("content_mode", "story_v1"),
        "status": "posted",
        "verified": bool(verified),
        "create_name": create_ok.get("name"),
    }
    history.append(new_entry)
    save_history(history)
    print(f"History updated. Total posts: {len(history)} → {HISTORY_FILE}")

    result = {
        "status": "success",
        "product": product_name,
        "link": affiliate_link,
        "hook_category": hook_category,
        "story_type": story_type,
        "category": category,
        "hook_text": hook_text[:80],
        "num_posts": num_posts,
        "verified": bool(verified),
        "create_name": create_ok.get("name"),
        "date": time.strftime("%Y-%m-%dT%H:%M"),
    }
    Path("/tmp/threads_post_result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()