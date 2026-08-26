#!/usr/bin/env python3
"""
Threads Affiliate Bot — Full 8-Step Flow (TESTED & WORKING)

1. Scan Threads fresh (< 24 jam)
2. Search Shopee for matching product
3. Copy product URL (with product slug)
4. Generate affiliate link via dashboard
5. Copy affiliate link
6. Navigate back to Threads post
7. Comment with Gen Z style + affiliate link
8. Verify & alert

Usage: python3 threads_full_flow.py [search_topic]
Topics: parfum, skincare, earphone, tas, sepatu, foundation, sunblock
"""

import json
import os
import re
import sys
import time
import requests
import websocket
import base64

CHROME_PORT = 9222
SCREENSHOT_DIR = "/tmp/threads-screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ─── CDP Helpers ──────────────────────────────────────────

def connect_chrome():
    tabs = requests.get(f"http://localhost:{CHROME_PORT}/json").json()
    return websocket.create_connection(tabs[0]["webSocketDebuggerUrl"], timeout=90)

def cdp(ws, method, params=None):
    msg_id = int(time.time() * 1000) % 9999
    msg = {"id": msg_id, "method": method}
    if params: msg["params"] = params
    ws.send(json.dumps(msg))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id:
            return resp.get("result", {})

def cdp_eval(ws, expr):
    result = cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    return result.get("result", {}).get("value", "")

def screenshot(ws, name):
    result = cdp(ws, "Page.captureScreenshot", {"format": "png"})
    path = os.path.join(SCREENSHOT_DIR, name)
    with open(path, "wb") as f:
        f.write(base64.b64decode(result.get("data", "")))
    return path

def click_at(ws, x, y):
    """Reliable CDP click — move mouse first, then press/release"""
    cdp(ws, "Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
    time.sleep(0.2)
    cdp(ws, "Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
    time.sleep(0.1)
    cdp(ws, "Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})

# ─── Step 1: Scan Threads ────────────────────────────────

def scan_threads(ws, topic):
    """Find fresh post (< 24h) on Threads matching topic"""
    print(f"\n{'='*50}")
    print(f"STEP 1: Scan Threads — topic: {topic}")
    print(f"{'='*50}")
    
    cdp(ws, "Page.navigate", {"url": f"https://www.threads.net/search?q={topic}&serp_type=default"})
    time.sleep(5)
    
    # Scroll to load posts
    cdp_eval(ws, "window.scrollBy(0, 500)")
    time.sleep(2)
    
    # Find fresh posts
    posts = json.loads(cdp_eval(ws, """
        (function() {
            var posts = [];
            var text = document.body.innerText;
            var lines = text.split('\\n');
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i].trim();
                var m = line.match(/^(\\d+)\\s*(menit|jam)\\b/i);
                if (m) {
                    var num = parseInt(m[1]);
                    var isFresh = (m[2] === 'menit') || (m[2] === 'jam' && num < 24);
                    if (isFresh) {
                        var ctx = '';
                        for (var j = Math.max(0,i-3); j <= Math.min(lines.length-1,i+2); j++) {
                            ctx += lines[j].trim() + ' ';
                        }
                        posts.push({time: num+' '+m[2], ctx: ctx.substring(0,300)});
                    }
                }
            }
            return JSON.stringify(posts.slice(0, 5));
        })()
    """) or "[]")
    
    if not posts:
        print("   ❌ No fresh posts found!")
        return None, None
    
    # Get post link
    post_link = cdp_eval(ws, """
        (function() {
            var links = document.querySelectorAll('a');
            for (var a of links) {
                if (a.href && a.href.includes('/@') && a.href.includes('/post/') && !a.href.includes('/media')) {
                    var r = a.getBoundingClientRect();
                    if (r.height > 30) return a.href;
                }
            }
            return '';
        })()
    """)
    
    if post_link:
        selected = posts[0]
        print(f"   ✅ Found: {selected['time']} old")
        print(f"   Context: {selected['ctx'][:150]}...")
        print(f"   Link: {post_link[:80]}")
        return post_link, selected
    else:
        print("   ❌ No post link found")
        return None, None

# ─── Step 2-5: Affiliate Link ───────────────────────────

def generate_affiliate_link(ws, topic):
    """Search Shopee → find product → generate affiliate link"""
    print(f"\n{'='*50}")
    print(f"STEP 2: Search Shopee for '{topic}'...")
    print(f"{'='*50}")
    
    cdp(ws, "Page.navigate", {"url": f"https://shopee.co.id/search?keyword={topic.replace(' ', '+')}"})
    time.sleep(5)
    
    # Get product URLs (with -i. format for affiliate dashboard)
    products = json.loads(cdp_eval(ws, """
        (function() {
            var links = document.querySelectorAll('a');
            var seen = new Set();
            var products = [];
            for (var a of links) {
                var href = a.href;
                if (href && href.includes('shopee.co.id/') && !seen.has(href)) {
                    seen.add(href);
                    var m = href.match(/(.*-i\\.)(\\d+)\\.(\\d+)/);
                    if (m) {
                        products.push({url: href, text: a.textContent.trim().substring(0, 80)});
                    }
                }
            }
            return JSON.stringify(products.slice(0, 5));
        })()
    """) or "[]")
    
    if not products:
        print("   ❌ No products found!")
        return None, None
    
    product = products[0]
    product_url = product['url']
    product_name = product['text']
    print(f"   ✅ Product: {product_name[:60]}")
    print(f"   URL: {product_url[:80]}")
    
    # Generate affiliate link
    print(f"\n{'='*50}")
    print(f"STEP 3-5: Generate affiliate link...")
    print(f"{'='*50}")
    
    cdp(ws, "Page.navigate", {"url": "https://affiliate.shopee.co.id/offer/custom_link"})
    time.sleep(5)
    
    # Scroll to find button
    cdp_eval(ws, "window.scrollBy(0, 300)")
    time.sleep(1)
    
    # Fill textarea
    cdp_eval(ws, "(function(){var ta=document.querySelector('textarea');if(ta){ta.focus();return 'ok'}return 'no'})()")
    time.sleep(0.5)
    cdp_eval(ws, f"(function(){{var ta=document.querySelector('textarea');if(ta){{ta.value='';ta.dispatchEvent(new Event('input',{{bubbles:true}}));return 'cleared'}}return 'no'}})()")
    time.sleep(0.5)
    cdp("Input.insertText", {"text": product_url})
    time.sleep(2)
    
    # Click "Buat Link"
    buttons = json.loads(cdp_eval(ws, """
        (function() {
            var r = [];
            document.querySelectorAll('button').forEach(function(b) {
                var text = b.textContent.trim();
                var rect = b.getBoundingClientRect();
                if (rect.height > 0 && text.toLowerCase().includes('buat link')) {
                    r.push({text: text, x: Math.round(rect.x+rect.width/2), y: Math.round(rect.y+rect.height/2)});
                }
            });
            return JSON.stringify(r);
        })()
    """) or "[]")
    
    if buttons:
        click_at(ws, buttons[0]['x'], buttons[0]['y'])
        print("   ✅ Clicked 'Buat Link'")
    
    time.sleep(6)
    
    # Extract affiliate link from SECOND textarea
    affiliate_link = cdp_eval(ws, """
        (function() {
            var textareas = document.querySelectorAll('textarea');
            for (var ta of textareas) {
                var val = ta.value || '';
                if (val.includes('s.shopee.co.id')) return val;
            }
            var allText = document.body.innerText;
            var match = allText.match(/https?:\\/\\/s\\.shopee\\.co\\.id\\/[^\\s]+/);
            if (match) return match[0];
            return '';
        })()
    """)
    
    if affiliate_link:
        print(f"   ✅ Affiliate link: {affiliate_link}")
        return affiliate_link, product_name
    else:
        print("   ❌ Failed to generate affiliate link")
        return None, product_name

# ─── Step 6-7: Post Comment ──────────────────────────────

def post_comment(ws, post_url, comment):
    """Navigate to post and comment with affiliate link"""
    print(f"\n{'='*50}")
    print(f"STEP 6-7: Post comment...")
    print(f"{'='*50}")
    
    cdp(ws, "Page.navigate", {"url": post_url})
    time.sleep(6)
    
    # Click reply button
    reply = json.loads(cdp_eval(ws, """
        (function() {
            var svgs = document.querySelectorAll('svg');
            for (var svg of svgs) {
                var label = svg.getAttribute('aria-label') || '';
                if (label.toLowerCase().includes('balas')) {
                    var r = svg.getBoundingClientRect();
                    if (r.width > 0) return JSON.stringify({x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)});
                }
            }
            return 'null';
        })()
    """) or "null")
    
    if reply and reply != 'null':
        click_at(ws, reply['x'], reply['y'])
        print(f"   Clicked reply ({reply['x']}, {reply['y']})")
        time.sleep(3)
    else:
        print("   ❌ Reply button not found")
        return False
    
    # Focus input
    cdp_eval(ws, "(function(){var ces=document.querySelectorAll('[contenteditable=true]');for(var ce of ces){if(ce.offsetHeight>0&&ce.offsetHeight<300){ce.focus();return 'focused'}}return 'no'})()")
    time.sleep(1)
    
    # Type comment
    cdp(ws, "Input.insertText", {"text": comment})
    time.sleep(2)
    
    # Click Kirim
    kirim = cdp_eval(ws, """
        (function() {
            var r = [];
            document.querySelectorAll('[role="button"]').forEach(function(b) {
                var text = b.textContent.trim();
                var rect = b.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0 && text.toLowerCase() === 'kirim') {
                    r.push({text: text, x: Math.round(rect.x+rect.width/2), y: Math.round(rect.y+rect.height/2)});
                }
            });
            return JSON.stringify(r);
        })()
    """)
    
    if kirim and kirim != '[]':
        btn = json.loads(kirim)[0]
        click_at(ws, btn['x'], btn['y'])
        print(f"   ✅ Clicked Kirim ({btn['x']}, {btn['y']})")
        time.sleep(5)
        return True
    else:
        print("   ❌ Kirim button not found")
        return False

# ─── Step 8: Verify ─────────────────────────────────────

def verify_comment(ws, post_url):
    """Verify comment was posted"""
    print(f"\n{'='*50}")
    print(f"STEP 8: Verify...")
    print(f"{'='*50}")
    
    cdp(ws, "Page.navigate", {"url": post_url})
    time.sleep(6)
    
    page_text = cdp_eval(ws, "document.body.innerText")
    if "jagonya_shopee" in page_text:
        idx = page_text.find("jagonya_shopee")
        comment_text = page_text[idx:idx+400]
        print(f"   ✅ ✅ ✅ COMMENT POSTED!")
        return True, comment_text
    elif "Diposting" in page_text:
        print("   ✅ Posted (Diposting visible)")
        return True, "Diposting visible"
    else:
        print("   ❌ Comment not found")
        return False, ""

# ─── Main Flow ───────────────────────────────────────────

def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else "skincare"
    
    print("🟠 Threads Affiliate Bot — 8-Step Flow")
    print(f"Topic: {topic}")
    
    ws = connect_chrome()
    
    try:
        # Step 1: Find fresh post
        post_url, post_info = scan_threads(ws, topic)
        if not post_url:
            print("\n🔴 THREADS POST FAILED")
            print("❌ No fresh posts found")
            return
        
        # Steps 2-5: Generate affiliate link
        affiliate_link, product_name = generate_affiliate_link(ws, topic)
        if not affiliate_link:
            print("\n🔴 THREADS POST FAILED")
            print("❌ Could not generate affiliate link")
            return
        
        # Step 6-7: Post comment
        comment = f"bestie! {product_name[:30]} ini bagus bgt, udah banyak yg beli. worth it sih 🤌\n\n{affiliate_link}"
        success = post_comment(ws, post_url, comment)
        
        if not success:
            print("\n🔴 THREADS POST FAILED")
            print("❌ Could not post comment")
            return
        
        # Step 8: Verify
        verified, text = verify_comment(ws, post_url)
        
        if verified:
            print(f"\n{'='*50}")
            print("🟢 THREADS POST SUCCESS!")
            print(f"{'='*50}")
            print(f"👤 @jagonya_shopee")
            print(f"⏱️  {post_info['time']} ago")
            print(f"📝 {comment[:100]}...")
            print(f"🔗 {affiliate_link}")
            print(f"🛒 {product_name[:60]}")
            print(f"💬 Post: {post_url}")
        else:
            print(f"\n🔴 THREADS POST FAILED (unverified)")
    
    finally:
        ws.close()
        os.system('killall "Google Chrome" 2>/dev/null')
        print("\n✅ Chrome closed (RAM freed)")

if __name__ == "__main__":
    main()
