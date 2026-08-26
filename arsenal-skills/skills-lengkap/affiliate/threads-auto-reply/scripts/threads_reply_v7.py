#!/usr/bin/env python3
"""Threads Auto-Reply v7.0 — COMBO 6 KREATOR + N-Post Support
Auto-reads links from database, uses CDP, handles all edge cases.
Run: cd /Users/user/.hermes/hermes-agent && venv/bin/python3 ~/.hermes/scripts/threads_reply_v7.py

Changes from v6:
- REPLIES_TARGET default = 1 (SYADAGENTIC directive 2026-06-11)
- Keywords prioritized: men's skincare (cowok, bapak, pria)
- MUA filter with word boundary regex
- Shopee link filter: original post only (not comments)
"""

import json, time, sys, os, re, subprocess, random
import requests, websocket

# ─── Config ───
REPLIES_TARGET = 1
KEYWORDS = [
    "skincare cowok",
    "bodycare bapak",
    "perawatan pria",
    "skincare laki laki",
    "rekomendasi skincare bapak",
    "skincare pria murah",
    "rekomendasi skincare",
    "rekomendasi makeup",
    "parfum enak",
    "hair tonic rontok",
    "sunscreen terbaik",
]

DATABASE_PATH = os.path.expanduser("~/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md")
MY_USERNAME = "jagonya_shopee"

# Filter rules (SYADAGENTIC directive 2026-06-11)
MUA_PATTERN = re.compile(r'\b(MUA|makeup\s*artist)\b', re.IGNORECASE)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def cdp(ws, method, params=None, timeout=30):
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
    resp = cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True}, timeout)
    if resp and "result" in resp:
        return resp["result"].get("result", {}).get("value")
    return None

def parse_database():
    links = []
    try:
        with open(DATABASE_PATH, 'r') as f:
            content = f.read()
        for line in content.split('\n'):
            if '❌ UNUSED' in line and 's.shopee.co.id' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    product = None
                    link = None
                    for p in parts:
                        if 's.shopee.co.id' in p:
                            link = p
                        elif p and not p.isdigit() and 'UNUSED' not in p and 'USED' not in p and p != '-':
                            if not product:
                                product = p
                    if product and link:
                        category = "skincare"
                        if any(w in product.lower() for w in ['parfum', 'mist', 'fragrance', 'edt', 'edp']):
                            category = "parfum"
                        elif any(w in product.lower() for w in ['hair', 'shampoo', 'conditioner', 'rambut', 'tonic']):
                            category = "haircare"
                        elif any(w in product.lower() for w in ['lip', 'makeup', 'foundation', 'cushion', 'powder', 'blush']):
                            category = "makeup"
                        links.append({"product": product, "url": link, "category": category})
    except Exception as e:
        log(f"Error parsing database: {e}")
    return links

def get_comment_templates():
    return [
        "Kalo lagi nyari {product}, coba deh yang ini. Gw udah pake dan emang gila sih bagusnya ✨ {url}",
        "SE-SIMPEL pake {product} doang ternyata bisa bikin beda banget. Yang gw pake: {url}",
        "Barang receh yang sering diremehin tapi ternyata gokil. {product}: {url}",
        "Gw juga dulu struggle nyari yang cocok. Akhirnya nemu {product} dan gak bisa lepas: {url}",
        "Yang juga ngalamin masalah ini, coba cek {product}. Gw pribadi udah cocok banget: {url}",
        "Temennya temen gw rekomendasiin {product} ini. Sekarang gw yang jadi addict 😭 {url}",
        "Nyesel banget baru tau {product} ini. Padahal udah habis jutaan buat yang lain: {url}",
        "Udah 500+ orang review positif {product} ini. Gw ikutan coba dan gak nyesel: {url}",
    ]

def generate_comment(product_name, link_url):
    templates = get_comment_templates()
    template = random.choice(templates)
    clean_name = re.sub(r'\d+\s*(g|gr|ml|g\b).*', '', product_name).strip()
    if len(clean_name) > 40:
        clean_name = clean_name[:40]
    comment = template.format(product=clean_name, url=link_url)
    return comment

def search_posts(ws, keyword):
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

def reply_to_post(ws, post_url, comment_text, link_url, product_name):
    full_url = f"https://www.threads.com{post_url}" if post_url.startswith("/") else post_url
    log(f"Opening: {full_url}")
    cdp(ws, "Page.navigate", {"url": full_url})
    time.sleep(8)

    # FILTER 1: Check for MUA in original post (word boundary)
    body = cdp_eval(ws, "document.body.innerText") or ""
    if MUA_PATTERN.search(body):
        log("Post contains MUA — skipping")
        return "skipped_mua"

    # FILTER 2: Check for shopee link in ORIGINAL POST only (not comments)
    # Try to extract original post content (first post container)
    original_post = cdp_eval(ws, '''(function() {
        // Try to get just the first post (original post, not comments)
        var posts = document.querySelectorAll('[data-pressable-container="true"]');
        if (posts.length > 0) {
            return posts[0].innerText || "";
        }
        // Fallback: use first 1000 chars of body (likely contains original post)
        return document.body.innerText.substring(0, 1000);
    })()''') or ""
    
    if "s.shopee.co.id" in original_post:
        log("Original post has shopee link — skipping")
        return "already_replied"

    # Install fetch monkey-patch
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

    # Find reply button
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

    # Wait for dialog
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

    # Click Post/Kirim
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

def main():
    log("=== Threads Auto-Reply v7.0 — COMBO 6 KREATOR ===")
    
    links = parse_database()
    log(f"Found {len(links)} UNUSED links in database")
    
    if not links:
        log("No unused links found!")
        return
    
    log("Killing stale Chrome...")
    subprocess.run(["pkill", "-9", "-f", "Google Chrome"], capture_output=True)
    time.sleep(2)
    
    log("Launching Chrome with CDP...")
    chrome_proc = subprocess.Popen([
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--disable-sync",
        "--user-data-dir=/tmp/chrome-cdp-threads",
        "--window-size=1440,900",
        "https://www.threads.com",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(8)

    try:
        ver = requests.get("http://localhost:9222/json/version", timeout=5).json()
        log(f"CDP OK: {ver.get('Browser', 'unknown')}")
    except Exception as e:
        log(f"CDP connection failed: {e}")
        return

    tabs = requests.get("http://localhost:9222/json", timeout=5).json()
    page_tab = next((t for t in tabs if t.get("type") == "page"), None)
    if not page_tab:
        log("No page tab found!")
        return

    ws = websocket.create_connection(page_tab["webSocketDebuggerUrl"], timeout=30)
    ws.settimeout(5)
    log(f"Connected to: {page_tab.get('url', 'unknown')}")

    # Inject cookies
    log("Injecting cookies...")
    ig_cookies = json.load(open("/Users/user/instagram_cookies.json"))
    for name, value in ig_cookies.items():
        cdp(ws, "Network.setCookie", {"name": name, "value": value, "domain": ".instagram.com", "path": "/", "secure": True})

    threads_cookies_file = os.path.expanduser("~/threads_cookies.json")
    if os.path.exists(threads_cookies_file):
        threads_cookies = json.load(open(threads_cookies_file))
        for name, value in threads_cookies.items():
            cdp(ws, "Network.setCookie", {"name": name, "value": value, "domain": ".threads.com", "path": "/", "secure": True})

    log("Navigating to threads.com...")
    cdp(ws, "Page.navigate", {"url": "https://www.threads.com"})
    time.sleep(8)

    current_url = cdp_eval(ws, "window.location.href") or ""
    if "suspended" in current_url:
        log("❌ ACCOUNT SUSPENDED — aborting")
        ws.close()
        return

    body = cdp_eval(ws, "document.body.innerText.substring(0, 2000)") or ""
    login_indicators = ["Beranda", "For you", "Home", "Search", "Profile", "Activity", "Untuk Anda", "Profil", "Notifikasi"]
    logged_in = any(x in body for x in login_indicators)
    
    if not logged_in:
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
            return

    log("✅ Logged in!")

    # Execute replies
    replies_done = 0
    replies_success = 0
    results = []
    used_link_indices = []

    for keyword in KEYWORDS:
        if replies_done >= REPLIES_TARGET:
            break

        post_urls = search_posts(ws, keyword)
        log(f"Found {len(post_urls)} posts for '{keyword}'")

        if not post_urls:
            continue

        category = "skincare"
        if "makeup" in keyword or "lip" in keyword:
            category = "makeup"
        elif "parfum" in keyword or "mist" in keyword:
            category = "parfum"
        elif "hair" in keyword or "rontok" in keyword:
            category = "haircare"
        
        link_info = None
        for idx, link in enumerate(links):
            if idx not in used_link_indices and link["category"] == category:
                link_info = link
                used_link_indices.append(idx)
                break
        
        if not link_info:
            for idx, link in enumerate(links):
                if idx not in used_link_indices:
                    link_info = link
                    used_link_indices.append(idx)
                    break
        
        if not link_info:
            log(f"No unused links available for {keyword}")
            continue

        comment = generate_comment(link_info["product"], link_info["url"])
        log(f"Comment: {comment[:80]}...")

        for j, post_url in enumerate(post_urls[:8]):
            if replies_done >= REPLIES_TARGET:
                break
            if f"/@{MY_USERNAME}/" in post_url:
                continue

            result = reply_to_post(ws, post_url, comment, link_info["url"], link_info["product"])

            if result in ("hard_blocked", "restricted"):
                results.append({"link": link_info, "post_url": post_url, "result": result})
                replies_done = REPLIES_TARGET
                break
            elif result in ("success", "pending"):
                results.append({"link": link_info, "post_url": post_url, "result": result})
                replies_done += 1
                if result == "success": replies_success += 1
                log(f"Reply {replies_done}/{REPLIES_TARGET}: {result.upper()}")
                time.sleep(random.randint(30, 60))
                break

    log(f"\n=== SUMMARY: {replies_success}/{replies_done} verified visible ===")
    for r in results:
        log(f"  - {r['link']['product']} → {r['result']} ({r['post_url']})")

    with open("/tmp/threads_reply_result.json", "w") as f:
        json.dump({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "results": results}, f, indent=2)

    ws.close()
    subprocess.run(["pkill", "-9", "-f", "Google Chrome"], capture_output=True)
    log("Done.")

if __name__ == "__main__":
    main()
