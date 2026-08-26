#!/usr/bin/env python3
"""Threads Auto-Reply via CDP (non-headless Chrome) — v4.8
Proven pattern: 2026-06-04, 2/2 replies verified visible.
Run: cd /Users/user/.hermes/hermes-agent && venv/bin/python3 scripts/threads_reply_cdp_v2.py
"""

import json, time, sys, os, re, subprocess, random
import requests, websocket

# ─── Config ───
REPLIES_TARGET = 2
LINKS = [
    # Fill from affiliate-link-database.md (first ❌ UNUSED per category)
    {"product": "PRODUCT_NAME", "url": "https://s.shopee.co.id/XXXXX", "category": "CATEGORY"},
]
KEYWORDS = ["keyword1", "keyword2"]  # Match keyword to link category

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def cdp(ws, method, params=None, timeout=30):
    """Send CDP command and get response. Handles WS timeout drain."""
    mid = random.randint(100, 99999)
    cmd = {"id": mid, "method": method}
    if params:
        cmd["params"] = params
    ws.send(json.dumps(cmd))
    deadline = time.time() + timeout
    while time.time() < deadline:
        ws.settimeout(5)
        try:
            resp = json.loads(ws.recv())
            if resp.get("id") == mid:
                return resp
        except Exception:
            continue
    return None

def cdp_eval(ws, expr, timeout=30):
    """Evaluate JS and return value."""
    resp = cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True}, timeout)
    if resp and "result" in resp:
        return resp["result"].get("result", {}).get("value")
    return None

# ─── Step 1: Kill stale Chrome (CRITICAL — port 9222 lock) ───
log("Killing stale Chrome...")
subprocess.run(["pkill", "-9", "-f", "Google Chrome"], capture_output=True)
time.sleep(2)

# ─── Step 2: Launch Chrome with CDP ───
log("Launching Chrome with CDP...")
chrome_proc = subprocess.Popen([
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--remote-debugging-port=9222",
    "--remote-allow-origins=*",
    "--no-first-run",
    "--disable-sync",
    "--user-data-dir=/tmp/chrome-cdp-threads",  # NON-default required for Chrome 148+
    "--window-size=1440,900",
    "https://www.threads.com",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)

try:
    ver = requests.get("http://localhost:9222/json/version", timeout=5).json()
    log(f"CDP OK: {ver.get('Browser', 'unknown')}")
except Exception as e:
    log(f"CDP connection failed: {e}")
    sys.exit(1)

# ─── Step 3: Get page WebSocket ───
tabs = requests.get("http://localhost:9222/json", timeout=5).json()
page_tab = next((t for t in tabs if t.get("type") == "page"), None)
if not page_tab:
    log("No page tab found!")
    sys.exit(1)

ws = websocket.create_connection(page_tab["webSocketDebuggerUrl"], timeout=30)
ws.settimeout(5)
log(f"Connected to: {page_tab.get('url', 'unknown')}")

# ─── Step 4: Inject cookies via CDP ───
log("Enabling Network...")
cdp(ws, "Network.enable", {})

log("Injecting IG cookies to .instagram.com...")
ig_cookies = json.load(open("/Users/user/instagram_cookies.json"))
for name, value in ig_cookies.items():
    cdp(ws, "Network.setCookie", {"name": name, "value": value, "domain": ".instagram.com", "path": "/", "secure": True})

log("Injecting Threads cookies to .threads.com...")
threads_cookies = json.load(open("/Users/user/threads_cookies.json"))
for name, value in threads_cookies.items():
    cdp(ws, "Network.setCookie", {"name": name, "value": value, "domain": ".threads.com", "path": "/", "secure": True})

# ─── Step 5: Navigate and verify login ───
log("Navigating to threads.com...")
cdp(ws, "Page.navigate", {"url": "https://www.threads.com"})
time.sleep(8)

current_url = cdp_eval(ws, "window.location.href") or ""
if "suspended" in current_url:
    log("❌ ACCOUNT SUSPENDED — aborting")
    ws.close()
    sys.exit(1)

body = cdp_eval(ws, "document.body.innerText.substring(0, 2000)") or ""
login_indicators = ["Beranda", "For you", "Home", "Search", "Profile", "Activity", "Untuk Anda", "Profil", "Notifikasi"]
logged_in = any(x in body for x in login_indicators)
if not logged_in:
    # Try SSO button
    sso_btn = cdp_eval(ws, '''(function() {
        for (var btn of document.querySelectorAll("[role=button], button, a")) {
            var t = btn.textContent.trim();
            if (/instagram/i.test(t) || /continue/i.test(t) || /masuk/i.test(t)) {
                var r = btn.getBoundingClientRect();
                return JSON.stringify({x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2), text: t});
            }
        }
        return null;
    })()''')
    if sso_btn:
        log(f"Clicking SSO via JS .click()...")
        cdp_eval(ws, '''(function() {
            for (var btn of document.querySelectorAll("[role=button], button, a")) {
                var t = btn.textContent.trim();
                if (/instagram/i.test(t) || /continue/i.test(t) || /masuk/i.test(t)) {
                    btn.click(); return "clicked: " + t;
                }
            }
            return "not found";
        })()''')
        time.sleep(10)
        body = cdp_eval(ws, "document.body.innerText.substring(0, 2000)") or ""
        logged_in = any(x in body for x in login_indicators)
    if not logged_in:
        log("❌ Login failed!")
        ws.close()
        sys.exit(1)

log("✅ Logged in!")

# ─── Helper functions ───
def search_posts(keyword):
    url = f"https://www.threads.com/search?q={keyword.replace(' ', '%20')}&filter=recent"
    log(f"Searching: {keyword}")
    cdp(ws, "Page.navigate", {"url": url})
    time.sleep(10)
    urls = cdp_eval(ws, '''(function() {
        var links = [];
        document.querySelectorAll("a").forEach(function(a) {
            var href = a.getAttribute("href");
            if (href && href.includes("/post/")) links.push(href);
        });
        var unique = [];
        links.forEach(function(u) { if (unique.indexOf(u) === -1) unique.push(u); });
        return unique;
    })()''')
    if isinstance(urls, str):
        try: urls = json.loads(urls)
        except: urls = []
    return urls or []

def reply_to_post(post_url, comment_text, link_url, product_name):
    """Returns: 'success', 'pending', 'failed', 'restricted', 'hard_blocked', 'already_replied'"""
    full_url = f"https://www.threads.com{post_url}" if post_url.startswith("/") else post_url
    log(f"Opening: {full_url}")
    cdp(ws, "Page.navigate", {"url": full_url})
    time.sleep(8)

    # Check already replied
    body = cdp_eval(ws, "document.body.innerText") or ""
    if "s.shopee.co.id" in body:
        log("Already has shopee link — skipping")
        return "already_replied"

    # Install fetch monkey-patch (must be AFTER page.goto — JS context resets)
    cdp_eval(ws, '''(function() {
        var origFetch = window.fetch;
        window._apiLogs = [];
        window.fetch = function() {
            var args = arguments;
            var req = typeof args[0] === "string" ? args[0] : (args[0] && args[0].url ? args[0].url : "");
            var entry = {url: req, method: (args[1] && args[1].method) || "GET"};
            return origFetch.apply(this, args).then(function(resp) {
                var clone = resp.clone();
                entry.status = resp.status;
                clone.text().then(function(t) { entry.body = t.substring(0, 2000); }).catch(function(){});
                window._apiLogs.push(entry);
                return resp;
            });
        };
        return "patched";
    })()''')

    # Find reply button (handles Comment/Balas/Reply + numbered) — use JS .click()
    reply_found = cdp_eval(ws, '''(function() {
        var btns = document.querySelectorAll('div[role="button"], span[role="button"]');
        for (var i = 0; i < btns.length; i++) {
            var text = btns[i].textContent.trim();
            if (/^(Comment|Balas|Reply)\\s*\\d+$/.test(text) && btns[i].offsetWidth > 0) {
                btns[i].click();
                return text;
            }
        }
        var plain = [];
        for (var i = 0; i < btns.length; i++) {
            var text = btns[i].textContent.trim();
            if (/^(Comment|Balas|Reply)$/.test(text) && btns[i].offsetWidth > 0) {
                plain.push(btns[i]);
            }
        }
        if (plain.length >= 1) { plain[0].click(); return 'plain-only'; }
        return null;
    })()''')

    if not reply_found:
        log("No reply button found")
        return "failed"

    log(f"Clicked: {reply_found}")

    # Wait for dialog (retry up to 6 times, 2s each)
    dialog_found = False
    for attempt in range(6):
        time.sleep(2)
        has_dialog = cdp_eval(ws, '!!document.querySelector("[role=\\"dialog\\"]")')
        if has_dialog:
            dialog_found = True
            break

    if not dialog_found:
        log("Dialog never appeared — skip")
        return "failed"

    # Check restriction
    dialog_text = cdp_eval(ws, '(document.querySelector("[role=\\"dialog\\"]") || {}).innerText || ""') or ""
    if "Sign up to chime in" in dialog_text:
        log("❌ Account restricted")
        return "restricted"

    # Type via execCommand (React compat)
    escaped = json.dumps(comment_text)
    cdp_eval(ws, f'''(function() {{
        var dialog = document.querySelector('[role="dialog"]');
        if (!dialog) return 'no dialog';
        var editor = dialog.querySelector('[contenteditable="true"]');
        if (!editor) return 'no editor';
        editor.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, {escaped});
        return 'ok';
    }})()''')
    time.sleep(2)

    # Click Post/Kirim via JS .click()
    posted = cdp_eval(ws, '''(function() {
        var dialog = document.querySelector('[role="dialog"]');
        if (!dialog) return "no dialog";
        for (var b of dialog.querySelectorAll('[role="button"]')) {
            var t = b.textContent.trim();
            if ((t === "Post" || t === "Kirim") && b.getBoundingClientRect().width > 0 && b.getBoundingClientRect().y > 0) {
                b.click();
                return t;
            }
        }
        return "not found";
    })()''')

    if not posted or posted in ("no dialog", "not found"):
        log(f"Post/Kirim button not found: {posted}")
        return "failed"

    log(f"Clicked {posted}...")

    time.sleep(10)

    # Check API response
    try:
        api_logs = cdp_eval(ws, '''(function() {
            return (window._apiLogs || []).filter(function(l) {
                return l.url.indexOf("configure_text_only_post") !== -1;
            });
        })()''')
        if isinstance(api_logs, str):
            api_logs = json.loads(api_logs)
        if api_logs:
            body_resp = api_logs[0].get("body", "")
            if "Media blocked due to integrity" in body_resp:
                log("❌ HARD BLOCKED")
                return "hard_blocked"
            if '"fail"' in body_resp and '"status":"fail"' in body_resp:
                log("❌ API fail")
                return "hard_blocked"
    except Exception:
        pass

    # Verify by reload
    time.sleep(5)
    log("Verifying...")
    cdp(ws, "Page.navigate", {"url": full_url})
    time.sleep(8)
    verify_body = cdp_eval(ws, "document.body.innerText") or ""
    if "s.shopee.co.id" in verify_body:
        log("✅ REPLY VISIBLE!")
        return "success"
    else:
        log("⚠️ Not visible (may be pending)")
        return "pending"

# ─── Execute replies ───
replies_done = 0
replies_success = 0
results = []

for i, (keyword, link_info) in enumerate(zip(KEYWORDS, LINKS)):
    if replies_done >= REPLIES_TARGET:
        break

    post_urls = search_posts(keyword)
    log(f"Found {len(post_urls)} posts for '{keyword}'")

    if not post_urls:
        continue

    # Generate comment
    openers = [
        "Btw ini", "Kalo cari yang worth it, coba deh", "Udah coba yang ini blm?",
        "Rekomen banget ini", "Gw pake ini dan emang gila si", "Yang lagi cari, ini no cap bagus bgt",
    ]
    opener = random.choice(openers)
    comment = f"{opener} {link_info['product']} recommended bgt deh ✨\n{link_info['url']}"

    keyword_success = False
    for j, post_url in enumerate(post_urls[:8]):
        if replies_done >= REPLIES_TARGET:
            break
        if "/@jagonya_shopee/" in post_url:
            continue

        result = reply_to_post(post_url, comment, link_info["url"], link_info["product"])

        if result in ("hard_blocked", "restricted"):
            results.append({"link": link_info, "post_url": post_url, "result": result})
            replies_done = REPLIES_TARGET
            break
        elif result in ("success", "pending"):
            results.append({"link": link_info, "post_url": post_url, "result": result})
            replies_done += 1
            if result == "success": replies_success += 1
            keyword_success = True
            log(f"Reply {replies_done}/{REPLIES_TARGET}: {result.upper()}")
            time.sleep(random.randint(30, 60))
            break
        else:
            continue

# ─── Summary ───
log(f"\n=== SUMMARY: {replies_success}/{replies_done} verified visible ===")
for r in results:
    log(f"  - {r['link']['product']} → {r['result']} ({r['post_url']})")

# Save + cleanup
with open("/tmp/threads_reply_result.json", "w") as f:
    json.dump({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "results": results}, f, indent=2)

ws.close()
subprocess.run(["pkill", "-9", "-f", "Google Chrome"], capture_output=True)
log("Done.")
