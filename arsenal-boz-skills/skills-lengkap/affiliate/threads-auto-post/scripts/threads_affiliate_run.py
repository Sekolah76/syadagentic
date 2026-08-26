#!/usr/bin/env python3
"""
Threads Affiliate Bot - Standalone CDP-only implementation (websocke-client)
Full 8-step flow: scan threads → find product → get affiliate link → post comment

Requirements: pip3 install websocket-client
Chrome must be running with --remote-debugging-port=9222 (Profile 16)

Usage: python3 threads_affiliate_run.py
"""

import json, time, random, re, sys, os, hashlib
import websocket

# ---- Configuration ----
CDP_HOST = "localhost"
CDP_PORT = 9222
CDP_TIMEOUT = 90
MY_USERNAME = "jagonya_shopee"

TOPICS = [
    "parfum", "skincare", "earphone", "tas", "sepatu",
    "jam tangan", "foundation", "sunblock", "lip tint", "hair oil"
]

USED_PRODUCTS_FILE = os.path.expanduser("~/.hermes/hermes-agent/scripts/used_products.json")


# ---- CDP Class ----

class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=CDP_TIMEOUT)
        self.msg_id = 0

    def send(self, method, params=None):
        self.msg_id += 1
        msg = {"id": self.msg_id, "method": method}
        if params: msg["params"] = params
        self.ws.send(json.dumps(msg))
        return self.msg_id

    def recv_until(self, msg_id, timeout=CDP_TIMEOUT):
        start = time.time()
        while time.time() - start < timeout:
            try:
                self.ws.settimeout(min(5, timeout - (time.time() - start)))
                data = self.ws.recv()
                parsed = json.loads(data)
                if parsed.get("id") == msg_id:
                    return parsed
            except:
                continue
        return None

    def call(self, method, params=None):
        mid = self.send(method, params)
        return self.recv_until(mid)

    def navigate(self, url):
        result = self.call("Page.navigate", {"url": url})
        time.sleep(5)
        return result

    def get_text(self):
        result = self.call("Runtime.evaluate", {
            "expression": "document.body.innerText", "returnByValue": True
        })
        if result and "result" in result:
            return result["result"].get("result", {}).get("value", "")
        return ""

    def eval_js(self, expression):
        result = self.call("Runtime.evaluate", {
            "expression": expression, "returnByValue": True, "awaitPromise": True
        })
        if result and "result" in result:
            return result["result"].get("result", {}).get("value")
        return None

    def click_at(self, x, y):
        """Reliable click: mouseMoved -> mousePressed -> mouseReleased"""
        self.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
        time.sleep(0.2)
        self.call("Input.dispatchMouseEvent", {
            "type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1
        })
        time.sleep(0.1)
        self.call("Input.dispatchMouseEvent", {
            "type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1
        })

    def type_text(self, text):
        self.call("Input.insertText", {"text": text})

    def scroll_down(self, pixels=500):
        self.eval_js(f"window.scrollBy(0, {pixels})")
        time.sleep(1)

    def scroll_up(self, pixels=500):
        self.eval_js(f"window.scrollBy(0, -{pixels})")
        time.sleep(1)

    def close(self):
        try: self.ws.close()
        except: pass


# ---- Helpers ----

def get_page_ws_url():
    import subprocess
    result = subprocess.run(
        ["curl", "-s", f"http://{CDP_HOST}:{CDP_PORT}/json/list"],
        capture_output=True, text=True, timeout=10
    )
    tabs = json.loads(result.stdout)
    for tab in tabs:
        if tab.get("type") == "page":
            return tab["webSocketDebuggerUrl"], tab.get("url", "")
    return None, None


def create_tab(url):
    import subprocess
    result = subprocess.run(
        ["curl", "-s", "-X", "PUT", f"http://{CDP_HOST}:{CDP_PORT}/json/new?{url}"],
        capture_output=True, text=True, timeout=10
    )
    return json.loads(result.stdout)


def load_used_products():
    try:
        with open(USED_PRODUCTS_FILE, "r") as f: return json.load(f)
    except: return []


def save_used_products(products):
    products = products[-200:]
    with open(USED_PRODUCTS_FILE, "w") as f: json.dump(products, f)


# ---- Step 2: Scan Threads for fresh posts ----

def find_fresh_post(cdp, topic):
    print(f"🔍 Searching Threads for: {topic}")
    cdp.navigate(f"https://www.threads.net/search?q={topic}&serp_type=default")
    time.sleep(6)

    # Wait for content
    for attempt in range(5):
        text = cdp.get_text()
        if "Memuat" not in text[:100] and len(text) > 200: break
        time.sleep(2)

    # Get post links with timestamps
    posts_data = cdp.eval_js("""
        (function() {
            var results = [];
            var links = document.querySelectorAll('a[href*="/post/"]');
            for (var i = 0; i < Math.min(links.length, 30); i++) {
                var link = links[i];
                var href = link.getAttribute('href');
                var parent = link.parentElement;
                var timeText = '';
                for (var j = 0; j < 5 && parent; j++) {
                    var spans = parent.querySelectorAll('span, time');
                    for (var s = 0; s < spans.length; s++) {
                        var t = spans[s].textContent;
                        if (t.match(/\\d+\\s*(menit|jam|hari|detik|hour|minute)/i)) {
                            timeText = t.trim(); break;
                        }
                    }
                    if (timeText) break;
                    parent = parent.parentElement;
                }
                results.push({
                    url: href.startsWith('http') ? href : 'https://www.threads.net' + href,
                    time: timeText,
                    text: link.textContent.substring(0, 300),
                    index: i
                });
            }
            return results;
        })()
    """)

    if not posts_data:
        print("❌ No posts found")
        return None, None, None

    # Filter for fresh (<24h) — SKIP "hari" always
    fresh_posts = []
    for post in posts_data:
        time_text = post["time"].lower()
        if not time_text: continue
        is_fresh = False
        if "menit" in time_text or "detik" in time_text:
            is_fresh = True
        elif "jam" in time_text:
            match = re.search(r'(\d+)\s*jam', time_text)
            if match and int(match.group(1)) < 24: is_fresh = True
        if "hari" in time_text: continue  # SKIP — always >24h
        if is_fresh: fresh_posts.append(post)

    if not fresh_posts:
        fresh_posts = [p for p in posts_data if len(p["text"]) > 20][:5]
    if not fresh_posts:
        return None, None, None

    chosen = random.choice(fresh_posts)
    print(f"✅ Selected: {chosen['time']} ago | {chosen['url'][:80]}")
    return chosen["url"], chosen["text"], chosen["time"]


# ---- Step 3-4: Search Shopee ----

def search_shopee(cdp, topic, used_products):
    import urllib.parse
    keyword = urllib.parse.quote(topic)
    print(f"🛒 Searching Shopee for: {topic}")
    cdp.navigate(f"https://shopee.co.id/search?keyword={keyword}")
    time.sleep(5)

    products = cdp.eval_js("""
        (function() {
            var results = [];
            var links = document.querySelectorAll('a[href*="-i."]');
            for (var i = 0; i < Math.min(links.length, 20); i++) {
                var href = links[i].getAttribute('href');
                if (href && href.includes('-i.') && href.includes('shopee.co.id')) {
                    var fullUrl = href.startsWith('http') ? href : 'https://shopee.co.id' + href;
                    results.push({url: fullUrl, text: links[i].textContent.substring(0, 150)});
                }
            }
            return results;
        })()
    """)

    if not products:
        all_links = cdp.eval_js("""
            Array.from(document.querySelectorAll('a')).map(a => ({
                url: a.href, text: a.textContent.substring(0, 100)
            })).filter(a => a.url.includes('shopee.co.id') && a.url.includes('-i.'))
        """)
        if all_links: products = all_links

    if not products: return None, None

    # Normalize url key (fallback search uses 'href')
    for p in products:
        if 'url' not in p and 'href' in p: p['url'] = p['href']
        if 'text' not in p: p['text'] = ''
    products = [p for p in products if 'url' in p]
    if not products: return None, None

    available = [p for p in products if not any(p["url"].split("?")[0] == u for u in used_products)]
    if not available: available = products

    chosen = random.choice(available)
    print(f"✅ Product: {chosen['text'][:80]}")
    return chosen["url"], chosen["text"]


# ---- Step 5: Generate affiliate link ----

def generate_affiliate_link(cdp, product_url):
    print(f"🔗 Generating affiliate link...")
    cdp.navigate("https://affiliate.shopee.co.id/offer/custom_link")
    time.sleep(5)

    cdp.scroll_up(1000)
    time.sleep(1)

    # Find textarea
    ta_pos = cdp.eval_js("""
        (function() {
            var textareas = document.querySelectorAll('textarea');
            for (var i = 0; i < textareas.length; i++) {
                var rect = textareas[i].getBoundingClientRect();
                if (rect.height > 0 && rect.width > 0)
                    return {x: rect.x + rect.width/2, y: rect.y + rect.height/2, index: i};
            }
            return null;
        })()
    """)
    if not ta_pos:
        print("❌ Cannot find textarea on affiliate page")
        return None

    cdp.click_at(ta_pos["x"], ta_pos["y"])
    time.sleep(0.5)
    cdp.eval_js(f"""
        (function() {{
            var ta = document.querySelectorAll('textarea')[{ta_pos.get('index',0)}] || document.querySelector('textarea');
            if (!ta) return;
            ta.focus();
            ta.value = '{product_url}';
            ta.dispatchEvent(new Event('input', {{bubbles:true}}));
            ta.dispatchEvent(new Event('change', {{bubbles:true}}));
        }})()
    """)
    time.sleep(1)

    cdp.scroll_down(400)
    time.sleep(2)

    # Find "Buat Link" via TreeWalker (more reliable than CSS)
    btn_pos = cdp.eval_js("""
        (function() {
            var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            while (walker.nextNode()) {
                var node = walker.currentNode;
                if (node.textContent.trim() === 'Buat Link') {
                    var parent = node.parentElement;
                    if (parent) {
                        var rect = parent.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0)
                            return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                    }
                }
            }
            var els = document.querySelectorAll('[role="button"], button');
            for (var i = 0; i < els.length; i++) {
                if (els[i].textContent.trim().includes('Buat Link')) {
                    var rect = els[i].getBoundingClientRect();
                    if (rect.width > 0) return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                }
            }
            return null;
        })()
    """)

    if not btn_pos:
        print("❌ Cannot find 'Buat Link' button")
        return None

    cdp.click_at(btn_pos["x"], btn_pos["y"])
    time.sleep(8)  # Wait 8s for link generation

    # Extract from all sources
    affiliate_link = cdp.eval_js("""
        (function() {
            // All textareas
            var tas = document.querySelectorAll('textarea');
            for (var i = 1; i < tas.length; i++) {
                if (tas[i].value && (tas[i].value.includes('s.shopee.co.id') || tas[i].value.includes('shope.ee')))
                    return tas[i].value;
            }
            for (var i = 0; i < tas.length; i++) {
                if (tas[i].value && (tas[i].value.includes('s.shopee.co.id') || tas[i].value.includes('shope.ee')))
                    return tas[i].value;
            }
            // Input fields
            var inputs = document.querySelectorAll('input');
            for (var i = 0; i < inputs.length; i++) {
                if (inputs[i].value && (inputs[i].value.includes('s.shopee.co.id') || inputs[i].value.includes('shope.ee')))
                    return inputs[i].value;
            }
            // innerText regex
            var bodyText = document.body.innerText;
            var m = bodyText.match(/s\\.shopee\\.co\\.id\\/[^\\s]+/);
            if (m) return m[0];
            m = bodyText.match(/shope\\.ee\\/[^\\s]+/);
            if (m) return m[0];
            // href attributes
            var links = document.querySelectorAll('a[href*="s.shopee.co.id"], a[href*="shope.ee"]');
            for (var i = 0; i < links.length; i++) return links[i].href;
            return null;
        })()
    """)

    if affiliate_link:
        if not affiliate_link.startswith('http'): affiliate_link = 'https://' + affiliate_link
        print(f"✅ Affiliate link: {affiliate_link[:80]}")
        return affiliate_link

    print("❌ Failed to extract affiliate link")
    return None


# ---- Step 6-7: Post comment ----

def post_comment(cdp, post_url, comment_text):
    print(f"💬 Posting on: {post_url[:80]}")
    cdp.navigate(post_url)
    time.sleep(5)

    # Find reply button (SVG with aria-label "balas")
    reply_btn = cdp.eval_js("""
        (function() {
            var svgs = document.querySelectorAll('svg[aria-label]');
            for (var i = 0; i < svgs.length; i++) {
                var label = svgs[i].getAttribute('aria-label');
                if (label && (label.toLowerCase().includes('balas') || label.toLowerCase().includes('reply'))) {
                    var rect = svgs[i].getBoundingClientRect();
                    if (rect.width > 0) return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                }
            }
            return null;
        })()
    """)
    if not reply_btn:
        print("❌ Reply button not found")
        return False

    cdp.click_at(reply_btn["x"], reply_btn["y"])
    time.sleep(3)

    # Find contenteditable input
    edit = cdp.eval_js("""
        (function() {
            var editables = document.querySelectorAll('[contenteditable="true"]');
            for (var i = 0; i < editables.length; i++) {
                var rect = editables[i].getBoundingClientRect();
                if (rect.height > 0 && rect.height < 300) {
                    editables[i].focus();
                    return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                }
            }
            return null;
        })()
    """)
    if not edit:
        print("❌ Comment input not found")
        return False

    cdp.click_at(edit["x"], edit["y"])
    time.sleep(0.5)
    cdp.type_text(comment_text)
    time.sleep(1)

    # Find Kirim button
    kirim = cdp.eval_js("""
        (function() {
            var elements = document.querySelectorAll('[role="button"]');
            for (var i = 0; i < elements.length; i++) {
                if (elements[i].textContent.trim() === 'Kirim') {
                    var rect = elements[i].getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0)
                        return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                }
            }
            return null;
        })()
    """)
    if not kirim:
        print("❌ Kirim button not found")
        return False

    cdp.click_at(kirim["x"], kirim["y"])
    time.sleep(5)
    return True


def verify_post(cdp, post_url):
    cdp.navigate(post_url)
    time.sleep(5)
    text = cdp.get_text()
    if MY_USERNAME in text:
        print("✅ Verified: comment found")
        return True
    print("⚠️ Username not found in page")
    return False


# ---- Main ----

def main():
    topic = random.choice(TOPICS)
    print(f"📌 Topic: {topic}")
    used = load_used_products()

    ws_url, _ = get_page_ws_url()
    if not ws_url:
        return "FAILED", "Cannot connect to Chrome CDP"

    tab = create_tab("about:blank")
    cdp = CDP(tab["webSocketDebuggerUrl"])

    try:
        post_url, post_text, post_age = find_fresh_post(cdp, topic)
        if not post_url:
            return "NO_POSTS", "No fresh posts found"

        product_url, product_name = search_shopee(cdp, topic, used)
        if not product_url:
            return "NO_PRODUCTS", "No Shopee products found"

        affiliate_link = generate_affiliate_link(cdp, product_url)
        if not affiliate_link:
            affiliate_link = product_url
            print("⚠️ Using direct product link")

        templates = [
            f"bestie coba ini {topic} bgt, enak bgt hasilnya 🔥 {affiliate_link}",
            f"gila si ini {topic} worth it bgt, auto beli lagi {affiliate_link} 💅",
            f"slay {topic} ini the best sih, gw recommend bgt 💪 {affiliate_link}",
            f"bestie ini {topic} murah tp kualitasnya gila {affiliate_link} 😍",
            f"auto checkout {topic} ini, murah bgt tp bagus {affiliate_link} 🤌",
        ]
        comment = random.choice(templates)

        success = post_comment(cdp, post_url, comment)
        if success:
            time.sleep(3)
            verified = verify_post(cdp, post_url)
            used.append(product_url.split("?")[0])
            save_used_products(used)
            return "SUCCESS", {
                "username": MY_USERNAME, "age": post_age, "comment": comment,
                "affiliate_link": affiliate_link, "product": product_name,
                "post_url": post_url, "verified": verified
            }
        return "POST_FAILED", "Failed to post"
    finally:
        import subprocess
        try:
            subprocess.run(["curl", "-s", "-X", "PUT",
                          f"http://{CDP_HOST}:{CDP_PORT}/json/close/{tab['id']}"],
                         capture_output=True, timeout=5)
        except: pass
        cdp.close()


if __name__ == "__main__":
    status, result = main()
    if status == "SUCCESS":
        r = result
        print(f"\n🟢 THREADS POST SUCCESS!")
        print(f"👤 @{r['username']}")
        print(f"⏱️ {r['age']} ago")
        print(f"📝 {r['comment']}")
        print(f"🔗 {r['affiliate_link']}")
        print(f"🛒 {r['product']}")
        print(f"💬 {r['post_url']}")
    elif status == "NO_POSTS":
        print(f"\n⏸️ No fresh posts found")
    else:
        print(f"\n🔴 THREADS POST FAILED\n❌ Reason: {result}")
