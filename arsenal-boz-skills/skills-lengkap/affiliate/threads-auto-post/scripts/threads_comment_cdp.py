#!/usr/bin/env python3
"""
Threads CDP Comment Script - FIXED v2
Click reply → Type via insertText → Post via Kirim button (role=button selector)
Usage: python3 threads_comment_cdp.py <post_url> <comment_text>
"""

import json
import sys
import time
import requests
import websocket

CHROME_PORT = 9222


def cdp(ws, method, params=None):
    msg_id = int(time.time() * 1000) % 9999
    msg = {"id": msg_id, "method": method}
    if params:
        msg["params"] = params
    ws.send(json.dumps(msg))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id:
            return resp.get("result", {})


def cdp_eval(ws, expr):
    result = cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    return result.get("result", {}).get("value", "")


def click_at(ws, x, y):
    """Reliable CDP click — move mouse first, then press/release"""
    cdp(ws, "Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
    time.sleep(0.2)
    cdp(ws, "Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
    time.sleep(0.1)
    cdp(ws, "Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})


def comment_threads(post_url: str, comment: str) -> bool:
    """Post a comment on a Threads post via CDP"""
    tabs = requests.get(f"http://localhost:{CHROME_PORT}/json").json()
    ws = websocket.create_connection(tabs[0]["webSocketDebuggerUrl"], timeout=60)

    # Navigate to post
    print(f"Navigating to: {post_url}")
    cdp(ws, "Page.navigate", {"url": post_url})
    time.sleep(6)

    # Find and click Balas button (SVG with aria-label="Balas")
    btn_raw = cdp_eval(ws, """
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
    """)

    if btn_raw == "null":
        print("❌ Reply button not found")
        ws.close()
        return False

    coords = json.loads(btn_raw)
    print(f"Clicking Balas at ({coords['x']}, {coords['y']})...")
    click_at(ws, coords['x'], coords['y'])
    time.sleep(3)

    # Focus input (contenteditable DIV)
    cdp_eval(ws, """
        (function() {
            var ces = document.querySelectorAll('[contenteditable="true"]');
            for (var ce of ces) {
                if (ce.offsetHeight > 0 && ce.offsetHeight < 300) {
                    ce.focus();
                    return 'focused';
                }
            }
            return 'no input';
        })()
    """)
    time.sleep(1)

    # Type via Input.insertText (NOT textarea.value)
    print(f"Typing comment ({len(comment)} chars)...")
    cdp(ws, "Input.insertText", {"text": comment})
    time.sleep(2)

    # Find and click Kirim button (CRITICAL: use role="button", NOT button tag)
    kirim_raw = cdp_eval(ws, """
        (function() {
            var result = [];
            document.querySelectorAll('[role="button"]').forEach(function(b) {
                var text = b.textContent.trim();
                var r = b.getBoundingClientRect();
                if (r.width > 0 && r.height > 0 && r.y > 0 && text.toLowerCase() === 'kirim') {
                    result.push({text: text, x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)});
                }
            });
            return JSON.stringify(result);
        })()
    """)

    buttons = json.loads(kirim_raw) if kirim_raw and kirim_raw != '[]' else []
    if buttons:
        b = buttons[0]
        print(f"Clicking Kirim at ({b['x']}, {b['y']})...")
        click_at(ws, b['x'], b['y'])
        time.sleep(5)
        ws.close()
        return True
    else:
        print("❌ Kirim button not found")
        ws.close()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 threads_comment_cdp.py <post_url> <comment>")
        sys.exit(1)

    post_url = sys.argv[1]
    comment = " ".join(sys.argv[2:])

    if comment_threads(post_url, comment):
        print("✅ Comment posted!")
    else:
        print("❌ Failed to post comment")
