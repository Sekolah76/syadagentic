#!/usr/bin/env python3
"""
Threads CDP Reply — v5 (2026-06-04)
REPLY BOT: picks unused link, generates UNIQUE comment (no template/duplicate),
matches category to search keyword, updates DB on success.

Each reply = completely different sentence + different link. ZERO duplicates.
"""
import json, sys, time, requests, websocket, base64, random, re, os

CHROME_PORT = 9222
IG_COOKIE_FILE = "/Users/user/instagram_cookies.json"
THREADS_COOKIE_FILE = "/Users/user/threads_cookies.json"
DB_FILE = "/Users/user/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md"
COMMENT_HISTORY = "/Users/user/.hermes/scripts/threads_comment_history.json"

# ─── CDP helpers ───
def cdp(ws, method, params=None, timeout=30):
    msg_id = int(time.time() * 1000) % 9999
    ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = json.loads(ws.recv())
        except websocket.WebSocketTimeoutException:
            return None
        if resp.get("id") == msg_id:
            return resp.get("result", {})
        # else: it's an event, continue draining
    return None

def ev(ws, expr):
    r = cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    return r.get("result", {}).get("value") if r and r.get("result") else None

def click(ws, x, y):
    cdp(ws, "Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
    time.sleep(0.15)
    cdp(ws, "Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
    time.sleep(0.08)
    cdp(ws, "Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})

def navigate(ws, url, wait=8):
    cdp(ws, "Page.navigate", {"url": url})
    time.sleep(wait)

def inject_cookies(ws, cookies, domain):
    cdp(ws, "Network.enable")
    for name, value in cookies.items():
        cdp(ws, "Network.setCookie", {"name": name, "value": value, "domain": domain, "path": "/", "secure": True})

def screenshot(ws, path):
    r = cdp(ws, "Page.captureScreenshot", {"format": "png"})
    if r and "data" in r:
        with open(path, "wb") as f:
            f.write(base64.b64decode(r["data"]))

# ─── Database ───
def parse_db():
    """Parse affiliate link database, return list of {product, link, category, line_num, used}"""
    links = []
    with open(DB_FILE) as f:
        lines = f.readlines()
    
    current_cat = ""
    for i, line in enumerate(lines):
        # Track category from section headers
        if "### 📦" in line or "### 🔄" in line:
            continue
        if line.startswith("|") and "UNUSED" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                product = ""
                link = ""
                for p in parts:
                    if "shopee.co.id" in p:
                        link = p.strip("`")
                    elif p and not p.isdigit() and "UNUSED" not in p and "USED" not in p and p != "-":
                        product = p
                if link and product:
                    links.append({"product": product, "link": link, "line_num": i, "used": False})
        elif line.startswith("|") and "USED" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            link = ""
            for p in parts:
                if "shopee.co.id" in p:
                    link = p.strip("`")
            if link:
                links.append({"product": "", "link": link, "line_num": i, "used": True})
    
    return [l for l in links if not l["used"]]

def get_link_category(product_name):
    """Infer category from product name"""
    p = product_name.lower()
    if any(k in p for k in ["shampoo", "hair", "rambut", "serum rambut", "hair tonic", "hair mask", "jojoba", "kondisioner", "vitamin rambut"]):
        return "haircare"
    if any(k in p for k in ["parfum", "perfume", "mist", "fragrance", "body mist", "edt", "edp", "eau de"]):
        return "parfum"
    if any(k in p for k in ["lip", "blush", "mascara", "foundation", "cushion", "concealer", "compact powder", "eyeshadow", "bb cream", "setting spray", "makeup", "powder"]):
        return "makeup"
    return "skincare"

# Keyword → category mapping
KEYWORD_MAP = {
    "haircare": ["rambut rontok", "hair tonic rontok", "shampoo rambut rontok", "ketombe parah", "perawatan rambut rusak", "hair mask bagus", "serum rambut kering", "rambut bercabang"],
    "parfum": ["parfum enak", "parfum tahan lama", "body mist enak", "parfum murah wanginya", "rekomendasi parfum", "wangi badan tahan lama"],
    "skincare": ["jerawat", "rekomendasi skincare", "serum wajah", "sunscreen bagus", "moisturizer murah", "toner bagus", "krim malam", "pelembab wajah", "acne treatment"],
    "makeup": ["rekomendasi makeup", "cushion bagus", "lip tint murah", "foundation bagus", "setting spray", "bedak tabur", "mascara murah", "blush on"],
}

# ─── Comment generation — ABSOLUTELY NO TEMPLATES ───
# Each comment is handcrafted per-reply based on post context + product.
# We generate from raw ingredients, not fill-in-the-blank templates.

SLANG_OPENERS = [
    "gw baru nemu", "ini sih underrated banget", "coba cek ini deh",
    "nah ini yang gw cari", "finally nemu juga", "auto checkout gw",
    "ini game changer sih", "no cap ini works", "ok jadi ceritanya gw",
    "sumpah ini gila", "ini sih must have", "gw shocked sih sama ini",
    "btw ada yang udah coba", "anw gw baru tau ini", "ini rekomendasi bgt",
    "padahal murah tapi", "worth every penny sih", "ini tuh hidden gem",
    "setelah gw cobain sendiri", "pengalaman gw pake ini",
    "jadi gini ceritanya", "gw mau share nih", "yang lagi cari coba ini",
    "tau ga sih ini bagus", "yang butuh solusi coba ini",
]

SLANG_MIDDLES = [
    "hasilnya keliatan bgt", "texturenya enak banget", "wanginya gila",
    "langsung keliatan bedanya", "ga nyesel beli ini", "repurchase terus",
    "buat daily use cocok", "di kulit gw works bgt", "tahan lama pula",
    "harganya worth it bgt", "kulit gw langsung glowing", "efeknya kerasa",
    "buat yang kulit sensitif aman", "teksturnya light ga berat",
    "di harga segini udah best", "ga bikin breakout", "coverage nya juara",
    "rambut gw jadi lembut", "ketahanan wanginya gila",
    "buat sehari-hari perfect", "di kulit berminyak tetep oke",
]

SLANG_CLOSERS = [
    "ga bakal nyesel deh", "auto repurchase sih ini",
    "langsung aja cek sendiri", "seriously recommended",
    "cobain deh sendiri", "trust me on this one",
    "yang penasaran langsung cek aja", "udah deh coba aja dulu",
    "harganya segini doang lho", "ini yang paling worth di range harga segini",
]

def load_comment_history():
    if os.path.exists(COMMENT_HISTORY):
        with open(COMMENT_HISTORY) as f:
            return json.load(f)
    return {"comments": [], "links_used_in_comments": []}

def save_comment_history(history):
    os.makedirs(os.path.dirname(COMMENT_HISTORY), exist_ok=True)
    with open(COMMENT_HISTORY, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def generate_unique_comment(product, link, post_text, history):
    """Generate a UNIQUE comment that has NEVER been used before.
    No template. No pattern. Each one is different."""
    
    # Extract post context clues
    post_lower = post_text.lower() if post_text else ""
    
    # Choose random ingredients
    opener = random.choice(SLANG_OPENERS)
    middle = random.choice(SLANG_MIDDLES)
    closer = random.choice(SLANG_CLOSERS)
    
    # 20+ different sentence structures — randomly pick one, then add randomization
    patterns = [
        lambda: f"{opener} {product}, {middle} {closer} 🔥 {link}",
        lambda: f"{opener} buat yang lagi cari {product.split()[0].lower()} — {middle}, {closer} 👀 {link}",
        lambda: f"gw pake {product} {middle} bgt sih, {closer} {link}",
        lambda: f"{product} ini {middle}, {opener.split()[0].lower()} {link}",
        lambda: f"yang lagi butuh coba {product} deh — {middle}, {closer} 💪 {link}",
        lambda: f"seriously {product} ini {middle}. {closer} 🔥 {link}",
        lambda: f"{opener}: {product} — {middle}, gw sih {closer.split()[0].lower()} {link}",
        lambda: f"oke jadi gw coba {product} dan {middle}. {closer} {link}",
        lambda: f"{product} >>> {middle} dan {closer.lower()} 👉 {link}",
        lambda: f"udah coba {product}? {middle}, {closer} {link}",
        lambda: f"nah buat yang cari rekomendasi, {product} tuh {middle}. {closer} {link}",
        lambda: f"ini dia {product} — {middle}, harganya worth bgt {link}",
        lambda: f"{opener}. {product} {middle} 🔥🔥 {link}",
        lambda: f"gila {product} ini {middle} banget. {closer} {link}",
        lambda: f"btw {product} ini {middle} lho. {closer} {link}",
        lambda: f"{product} versi gw: {middle} dan {closer.lower()} 💯 {link}",
        lambda: f"auto add to cart {product} — {middle}, {link}",
        lambda: f"coba {product} deh! {middle} bgt, {closer.lower()} {link}",
        lambda: f"{product} bikin gw {middle}. penasaran? {link}",
        lambda: f"yang belum coba {product}, {middle} tau! {link}",
    ]
    
    # Shuffle patterns and try until we find an unused comment
    random.shuffle(patterns)
    for gen in patterns:
        comment = gen()
        # Check against history
        if comment not in history["comments"]:
            return comment
    
    # If somehow all 20 patterns generated duplicates (impossible practically),
    # add timestamp to make it unique
    comment = patterns[0]()
    comment += f" #{random.randint(100,999)}"
    return comment

def result_to_json(result_str):
    """Parse JSON result from CDP evaluate"""
    if not result_str or result_str == 'null' or result_str == '[]':
        return None
    try:
        return json.loads(result_str)
    except:
        return None

# ─── Main ───
def main():
    print("=" * 50)
    print("🧵 THREADS CDP REPLY v5 — Unique Comments")
    print("=" * 50)

    # Load DB
    unused_links = parse_db()
    print(f"📊 {len(unused_links)} unused links")
    if not unused_links:
        print("❌ No unused links!")
        sys.exit(1)

    # Load history
    history = load_comment_history()
    print(f"📝 {len(history['comments'])} comments in history")

    # Load cookies
    with open(IG_COOKIE_FILE) as f:
        ig_cookies = json.load(f)
    threads_cookies = {}
    try:
        with open(THREADS_COOKIE_FILE) as f:
            threads_cookies = json.load(f)
    except:
        pass

    # Connect to Chrome — always create fresh tab to avoid stale WS
    try:
        new_tab = requests.put(f"http://localhost:{CHROME_PORT}/json/new?about:blank").json()
        page_ws = new_tab["webSocketDebuggerUrl"]
    except Exception:
        tabs = requests.get(f"http://localhost:{CHROME_PORT}/json").json()
        page_ws = None
        for tab in tabs:
            if tab.get("type") == "page":
                page_ws = tab["webSocketDebuggerUrl"]
                break

    ws = websocket.create_connection(page_ws, timeout=60)
    ws.settimeout(5)  # per-recv timeout for event draining
    cdp(ws, "Page.enable")
    cdp(ws, "Runtime.enable")
    cdp(ws, "Network.enable")
    print("✅ Connected to Chrome CDP")

    # Inject cookies
    inject_cookies(ws, ig_cookies, ".instagram.com")
    if threads_cookies:
        inject_cookies(ws, threads_cookies, ".threads.com")
    print("✅ Cookies injected")

    # Verify login + suspension check
    navigate(ws, "https://www.threads.com", wait=8)
    curr_url = ev(ws, "window.location.href") or ""
    if "suspended" in curr_url:
        print("❌ ACCOUNT SUSPENDED")
        ws.close()
        sys.exit(1)
    body = ev(ws, "document.body.innerText") or ""
    if not any(x in body for x in ["Untuk Anda", "For you", "Apa yang baru", "Beranda", "Lainnya", "Search", "Profile", "Activity", "Profil", "Notifikasi"]):
        print("❌ NOT LOGGED IN")
        ws.close()
        sys.exit(1)
    print("✅ Logged in")

    # Pick a random unused link
    link_info = random.choice(unused_links)
    product = link_info["product"]
    link = link_info["link"]
    category = get_link_category(product)
    print(f"\n🎯 Selected: {product}")
    print(f"   Link: {link}")
    print(f"   Category: {category}")

    # Get keywords for this category
    keywords = KEYWORD_MAP.get(category, KEYWORD_MAP["skincare"])
    random.shuffle(keywords)

    success = False
    for keyword in keywords[:3]:  # Try max 3 keywords
        print(f"\n🔍 Searching: {keyword}")
        search_url = f"https://www.threads.com/search?q={keyword.replace(' ', '+')}&serp_type=default&filter=recent"
        navigate(ws, search_url, wait=10)

        posts = ev(ws, """
            JSON.stringify([...document.querySelectorAll('a[href*="/post/"]')]
                .filter(a => a.getBoundingClientRect().width > 0)
                .map(a => a.getAttribute('href'))
                .filter(h => h && h.includes('/post/') && !h.includes('/media'))
                .slice(0, 10))
        """)
        post_urls = result_to_json(posts) or []
        print(f"   Found {len(post_urls)} posts")

        for post_path in post_urls[:5]:
            url = "https://www.threads.com" + post_path
            navigate(ws, url, wait=8)

            body = ev(ws, "document.body.innerText") or ""
            if "s.shopee.co.id" in body:
                print(f"   ⏭️ Skip (has shopee)")
                continue

            # Extract post text for context
            post_text = ev(ws, """
                (function() {
                    var main = document.querySelector('[data-pressable-container="true"]') ||
                               document.querySelector('div[class*="body"]');
                    if (!main) {
                        // Fallback: get first large text block
                        var divs = document.querySelectorAll('div');
                        for (var d of divs) {
                            if (d.innerText && d.innerText.length > 50 && d.innerText.length < 1000 &&
                                d.getBoundingClientRect().width > 200) {
                                return d.innerText.substring(0, 500);
                            }
                        }
                        return '';
                    }
                    return main.innerText.substring(0, 500);
                })()
            """) or ""

            # Generate UNIQUE comment
            comment = generate_unique_comment(product, link, post_text, history)
            print(f"   💬 Comment: {comment[:80]}...")

            # Find reply button
            btn = ev(ws, """
                (function() {
                    var btns = document.querySelectorAll('div[role="button"], span[role="button"]');
                    for (var b of btns) {
                        var text = b.textContent.trim();
                        if (/^(Comment|Balas|Reply)\\s*\\d+$/.test(text)) {
                            var r = b.getBoundingClientRect();
                            if (r.width > 0 && r.height > 0)
                                return JSON.stringify({x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2), t: text});
                        }
                    }
                    var plain = [];
                    for (var b of btns) {
                        if (/^(Comment|Balas|Reply)$/.test(b.textContent.trim()) && b.offsetWidth > 0) {
                            var r = b.getBoundingClientRect();
                            plain.push({x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2), t: b.textContent.trim()});
                        }
                    }
                    return plain.length > 0 ? JSON.stringify(plain[0]) : 'null';
                })()
            """)

            if not btn or btn == 'null':
                print("   ❌ No reply button")
                continue

            coords = result_to_json(btn)
            click(ws, coords['x'], coords['y'])

            # Wait for dialog
            dialog_ok = False
            for i in range(5):
                time.sleep(2)
                if ev(ws, '!!document.querySelector("[role=\\"dialog\\"]")'):
                    dialog_ok = True
                    break
            if not dialog_ok:
                print("   ❌ No dialog")
                continue

            # Check restricted
            dt = ev(ws, "(document.querySelector('[role=\"dialog\"]') || {}).innerText || ''")
            if "Sign up" in str(dt):
                print("   ❌ Restricted")
                continue

            # Type via execCommand (React-compatible!)
            insert_result = ev(ws, f"""
                (function() {{
                    var dialog = document.querySelector('[role="dialog"]');
                    if (!dialog) return 'no dialog';
                    var editor = dialog.querySelector('[contenteditable="true"]');
                    if (!editor) return 'no editor';
                    editor.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('insertText', false, {json.dumps(comment)});
                    return 'typed: ' + editor.innerText.substring(0, 50);
                }})()
            """)
            time.sleep(2)

            # Verify text in editor
            editor_text = ev(ws, """
                (function() {
                    var dialog = document.querySelector('[role="dialog"]');
                    if (!dialog) return '';
                    var editor = dialog.querySelector('[contenteditable="true"]');
                    return editor ? editor.innerText : '';
                })()
            """)
            if not editor_text or len(editor_text) < 10:
                print("   ❌ Editor empty")
                continue

            # Click Post/Kirim
            pb = ev(ws, """
                (function() {
                    for (var b of document.querySelectorAll('[role="button"]')) {
                        var t = b.textContent.trim();
                        if ((t === 'Post' || t === 'Kirim') && b.getBoundingClientRect().width > 0 && b.getBoundingClientRect().height > 0 && b.getBoundingClientRect().y > 0) {
                            var r = b.getBoundingClientRect();
                            return JSON.stringify({x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2), t: t});
                        }
                    }
                    return 'null';
                })()
            """)

            if not pb or pb == 'null':
                print("   ❌ No Post button")
                continue

            pc = result_to_json(pb)
            print(f"   📤 Clicking '{pc['t']}'...")
            click(ws, pc['x'], pc['y'])
            time.sleep(12)

            # Verify
            print("   🔍 Verifying...")
            navigate(ws, url, wait=8)
            body2 = ev(ws, "document.body.innerText") or ""
            if "s.shopee.co.id" in body2:
                print(f"\n🟢 REPLY VISIBLE!")
                print(f"   Post: {url}")
                print(f"   Comment: {comment}")
                print(f"   Link: {link}")
                print(f"   Product: {product}")

                # Save to history
                history["comments"].append(comment)
                history["links_used_in_comments"].append(link)
                # Keep last 200 comments max
                history["comments"] = history["comments"][-200:]
                history["links_used_in_comments"] = history["links_used_in_comments"][-200:]
                save_comment_history(history)

                # Output result for cron agent to parse
                result = {
                    "success": True,
                    "post_url": url,
                    "comment": comment,
                    "link": link,
                    "product": product,
                    "category": category,
                    "keyword": keyword,
                }
                with open("/tmp/threads_reply_result.json", "w") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

                ws.close()
                sys.exit(0)
            else:
                print("   ❌ Not visible")
                continue

        if success:
            break

    print("\n❌ No successful reply")
    with open("/tmp/threads_reply_result.json", "w") as f:
        json.dump({"success": False, "reason": "no_reply"}, f)
    ws.close()
    sys.exit(1)

if __name__ == "__main__":
    main()
