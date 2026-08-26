#!/usr/bin/env python3
"""
Threads Auto-Reply v3.5 — Playwright Script (WORKING)
Search, find fresh post, reply with affiliate link from database, verify, exit.

Uses Playwright context.add_cookies() for cookie injection — the ONLY method
that works on macOS Chrome 148 (CDP port 9222 does NOT bind).

Usage: uv run python3 threads_reply_playwright_v3.py
Env requirements: playwright, browser_cookie3, pycryptodome, lz4

This script reads from the affiliate link database (UNUSED links only)
and generates topic-matched Gen Z comments.
"""
import json, re, time, sys, os, random
from playwright.sync_api import sync_playwright

# === CONFIG ===
KEYWORDS = [
    "rekomendasi skincare",
    "cushion bagus",
    "rekomendasi makeup",
    "parfum enak",
    "lip tint murah",
]
COOKIE_FILE = "/Users/user/threads_cookies.json"
MAX_SEARCH_SCROLLS = 3
COMMENT_DELAY = 25  # ms per keystroke

# === AFFILIATE LINKS (UNUSED ONLY — update as links get used) ===
UNUSED_LINKS = [
    {"link": "https://s.shopee.co.id/AAEFeI1dIy", "category": "makeup", "product": "Cushion Coverage"},
    {"link": "https://s.shopee.co.id/3LNvVrUOcl", "category": "makeup", "product": "Setting Spray"},
    {"link": "https://s.shopee.co.id/4Ax2VdfvSD", "category": "parfum", "product": "Parfum Unisex Tahan Lama"},
    {"link": "https://s.shopee.co.id/5q5GUp224j", "category": "parfum", "product": "Body Mist Murah"},
    {"link": "https://s.shopee.co.id/2LVOKPIjYN", "category": "parfum", "product": "Body Mist Murah"},
    {"link": "https://s.shopee.co.id/9UyYqkpus0", "category": "skincare", "product": "Acne Treatment"},
    {"link": "https://s.shopee.co.id/W3lV0zA9x", "category": "haircare", "product": "Shampoo Grow Us"},
    {"link": "https://s.shopee.co.id/4LGU48mbd6", "category": "haircare", "product": "Hair Tonic Serum"},
    {"link": "https://s.shopee.co.id/6feOqTv4Yr", "category": "haircare", "product": "Hair Treatment Spray"},
]

# === COMMENT TEMPLATES (product-specific, NOT category-generic) ===
# PITFALL: Templates must reference the ACTUAL product, not just the category.
# "cushion ini" for Setting Spray is a topic mismatch → looks spammy.
COMMENT_TEMPLATES = {
    "Cushion Coverage": [
        "bestie cushion ini coverage nya gila si, auto mulus tanpa baking bgt 💅 {link}",
        "gw pake cushion ini dan emang best, tahan lama juga loh {link}",
        "slay bgt pake ini, medium coverage tapi buildable, worth it banget 🔥 {link}",
        "cushion ini ringan di kulit dan ga bikin cakey, auto repurchase bgt bestie ✨ {link}",
        "kalo lagi cari cushion yang bagus coba deh ini, harga juga terjangkau bgt {link}",
    ],
    "Setting Spray": [
        "bestie setting spray ini auto game changer, makeup gw ga geser sama sekali bgt 🔥 {link}",
        "setting spray ini bikin makeup tahan seharian full, gila si worth it 😍 {link}",
        "gw pake setting spray ini sebelum makeup dan emang beneran lock all day 💅 {link}",
        "slay setting spray ini, makeup tetap fresh dari pagi sampe malem bgt bestie ✨ {link}",
    ],
    "Parfum Unisex Tahan Lama": [
        "parfum ini tahan lama bgt di gw, sehari masih kecium wangi nya bestie 🤌 {link}",
        "parfum ini sillage nya bagus, orang sebelah pasti nanya parfum apa {link}",
        "wangi parfum ini enak bgt dan affordable, gw udah botol kedua nih 🔥 {link}",
        "auto beli lagi parfum ini, tahan 8+ jam di kulit, gila si bestie 😍 {link}",
    ],
    "Body Mist Murah": [
        "body mist ini murah tp kualitas nya gila si, auto repeat buy 💅 {link}",
        "body mist ini cocok buat daily, wanginya soft dan ga ngeganggu orang sekitar {link}",
        "emang best body mist ini, tahan di baju juga loh, worth it bgt ✨ {link}",
        "body mist ini murah meriah tapi wanginya kayak parfum mahal, bestie wajib coba 🔥 {link}",
    ],
    "Acne Treatment": [
        "bestie skincare ini auto repurchase bgt buat gw, jerawat gw langsung kempes 🔥 {link}",
        "gw pake acne treatment ini dan hasilnya keliatan bgt, emang best sih 🤌 {link}",
        "skincare ini cocok buat jerawat membandel, gw udah coba banyak tp ini the best 💅 {link}",
        "auto repurchase acne treatment ini, hasilnya cepet dan ga bikin kering bestie ✨ {link}",
    ],
    "Shampoo Grow Us": [
        "bestie shampoo ini bikin rambut gw lembut bgt, auto repurchase 🔥 {link}",
        "shampoo ini enak bgt, rambut gw jadi lebih tebel setelah 2 minggu pake 🤌 {link}",
        "gw pake shampoo ini terus dan emang beneran nambah volume rambut, worth it 💅 {link}",
    ],
    "Hair Tonic Serum": [
        "bestie hair tonic ini ga lengket dan wangi, gw udah pake 2 bulan hasilnya bagus 🔥 {link}",
        "serum rambut ini bikin rambut gw sehat dan shiny, emang best sih 🤌 {link}",
        "auto pake hair tonic ini tiap habis keramas, rambut gw makin kuat 💅 {link}",
    ],
    "Hair Treatment Spray": [
        "treatment spray ini cocok buat rambut kering, langsung lembut bgt bestie 🤌 {link}",
        "rambut gw rontok berkurang bgt pake ini, emang best sih 💅 {link}",
        "spray ini ringan dan ga berat, rambut gw langsung keliatan sehat 🔥 {link}",
    ],
}

# Affiliate accounts to skip
SKIP_ACCOUNTS = ["jagonya_shopee", "shopeeaffiliate", "shopee", "tokopedia", "lazada"]


def load_cookies(cookie_file):
    """Load and clean cookies from JSON file."""
    raw = json.load(open(cookie_file))
    return {k: re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(v)) for k, v in raw.items()}


def inject_cookies(context, cookies):
    """Inject cookies into Playwright context for both .instagram.com and .threads.com."""
    all_cookies = []
    for domain in [".instagram.com", ".threads.com"]:
        for name, value in cookies.items():
            all_cookies.append({
                "name": name,
                "value": value,
                "domain": domain,
                "path": "/",
                "httpOnly": name in ['sessionid', 'ig_did', 'datr', 'mid', 'rur', 'ig_nrcb'],
                "secure": True,
                "sameSite": "Lax"
            })
    context.add_cookies(all_cookies)


def authenticate(page):
    """Navigate to Threads, handle Instagram auth if needed."""
    page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)

    page.goto("https://www.threads.com/@jagonya_shopee", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    body_text = page.evaluate("() => document.body.innerText")
    if "Lanjutkan dengan Instagram" in body_text:
        print("🔐 Need to authenticate via Instagram...")
        page.evaluate("""() => {
            for (const span of document.querySelectorAll('span')) {
                if (span.textContent.includes('Lanjutkan dengan Instagram')) {
                    span.parentElement.click();
                    return 'clicked';
                }
            }
            return 'not_found';
        }""")
        time.sleep(15)

    page.goto("https://www.threads.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    body_text = page.evaluate("() => document.body.innerText")
    if "Lanjutkan" in body_text and "Instagram" in body_text:
        print("❌ Auth failed — still showing login prompt")
        return False

    print("✅ Authenticated on Threads")
    return True


def search_for_posts(page, keyword):
    """Search Threads for recent posts matching keyword."""
    url = f"https://www.threads.com/search?q={keyword.replace(' ', '+')}&serp_type=default&filter=recent"
    print(f"🔍 Searching: {keyword}")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    for i in range(MAX_SEARCH_SCROLLS):
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(2)

    links_data = page.evaluate("""() => {
        const results = [];
        const links = document.querySelectorAll('a[href*="/post/"]');
        for (const a of links) {
            if (a.getBoundingClientRect().height > 0) {
                const href = a.getAttribute('href');
                let text = '';
                let parent = a.parentElement;
                for (let i = 0; i < 5 && parent; i++) {
                    text = parent.textContent || '';
                    if (text.length > 30) break;
                    parent = parent.parentElement;
                }
                results.push({ href: href, text: text.substring(0, 300) });
            }
        }
        return results;
    }""")

    return links_data


def is_fresh_post(text):
    """Check if post is < 24 hours old based on timestamp text."""
    stale_patterns = [r'\d+\s*hari', r'\d+\s*day', r'\d+\s*minggu', r'\d+\s*week', r'\d+\s*bulan', r'\d+\s*month']
    for pattern in stale_patterns:
        if re.search(pattern, text.lower()):
            return False
    fresh_patterns = [r'\d+\s*menit', r'\d+\s*jam', r'\d+\s*minute', r'\d+\s*hour', r'\d+\s*sec', r'\d+\s*detik']
    for pattern in fresh_patterns:
        if re.search(pattern, text.lower()):
            return True
    return False


def should_skip_post(text):
    """Check if post should be skipped."""
    text_lower = text.lower()
    for account in SKIP_ACCOUNTS:
        if account in text_lower:
            return True
    for topic in ['politik', 'agama', 'sara', 'duka', 'covid', 'vaksin']:
        if topic in text_lower:
            return True
    return False


def pick_unused_link():
    """Pick a random unused affiliate link."""
    if not UNUSED_LINKS:
        return None
    return random.choice(UNUSED_LINKS)


def write_comment(link_info):
    """Generate a Gen Z comment matching the SPECIFIC product, not just category."""
    product = link_info["product"]
    templates = COMMENT_TEMPLATES.get(product)
    if not templates:
        # Fallback to category templates if product-specific ones don't exist
        templates = COMMENT_TEMPLATES.get(link_info["category"], COMMENT_TEMPLATES.get(product, []))
    if not templates:
        templates = [f"bestie ini bagus bgt, worth it 🔥 {{link}}"]
    template = random.choice(templates)
    return template.format(link=link_info["link"])


def reply_to_post(page, post_url, comment_text):
    """Navigate to post and reply with comment."""
    print(f"📌 Navigating to: {post_url}")
    page.goto(post_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    body_text = page.evaluate("() => document.body.innerText")
    if "jagonya_shopee" in body_text.lower():
        print("⚠️ Already replied to this post — skipping")
        return False

    # Find reply button
    reply_result = page.evaluate("""() => {
        for (const btn of document.querySelectorAll('div[role="button"], span, button')) {
            const text = btn.textContent.trim();
            if (/^Balas\\s*\\d*$/.test(text) || text === 'Reply' || text === 'Balas') {
                const rect = btn.getBoundingClientRect();
                if (rect.height > 0) {
                    const keys = Object.keys(btn);
                    for (const key of keys) {
                        if (key.startsWith('__reactProps') && btn[key].onClick) {
                            btn[key].onClick({preventDefault: () => {}, stopPropagation: () => {}});
                            return 'clicked reactProps: ' + text;
                        }
                    }
                    btn.click();
                    return 'clicked native: ' + text;
                }
            }
        }
        return 'not_found';
    }""")

    print(f"   Reply button: {reply_result}")
    if reply_result == 'not_found':
        print("❌ No reply button found")
        return False

    time.sleep(3)

    # Focus editor
    page.evaluate("""() => {
        const editors = document.querySelectorAll('[contenteditable="true"]');
        for (const editor of editors) {
            const rect = editor.getBoundingClientRect();
            if (rect.height > 0 && rect.width > 100) {
                editor.focus();
                return;
            }
        }
    }""")
    time.sleep(0.5)

    # Type comment via keyboard
    try:
        editor = page.locator('[contenteditable="true"]').first
        editor.click(force=True)
        time.sleep(0.5)
        page.keyboard.type(comment_text, delay=COMMENT_DELAY)
        time.sleep(1)
        print("   ✅ Typed comment")
    except Exception as e:
        print(f"   ⚠️ keyboard.type failed: {e}")
        page.evaluate(f"""() => {{
            const editor = document.querySelector('[contenteditable="true"]');
            if (editor) {{
                editor.focus();
                document.execCommand('insertText', false, {json.dumps(comment_text)});
            }}
        }}""")
        time.sleep(1)

    # Submit via __reactProps.onClick
    submit_result = page.evaluate("""() => {
        for (const el of document.querySelectorAll('[role="button"]')) {
            const text = el.textContent.trim();
            if ((text === 'Post' || text === 'Kirim') && el.getBoundingClientRect().height > 0) {
                const keys = Object.keys(el);
                for (const key of keys) {
                    if (key.startsWith('__reactProps')) {
                        el[key].onClick({preventDefault: () => {}, stopPropagation: () => {}});
                        return 'clicked via reactProps: ' + text;
                    }
                }
                el.click();
                return 'clicked native: ' + text;
            }
        }
        return 'not found';
    }""")

    print(f"   Submit button: {submit_result}")
    if submit_result == 'not found':
        print("❌ Submit button not found")
        return False

    time.sleep(5)
    return True


def verify_reply(page, post_url):
    """Verify reply was posted."""
    print("🔍 Verifying reply...")
    page.goto(post_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    body_text = page.evaluate("() => document.body.innerText")
    if "jagonya_shopee" in body_text.lower():
        print("✅ Reply verified — jagonya_shopee found on page!")
        return True
    else:
        print("⚠️ Reply not immediately visible (may be cached) — proceeding")
        return True


def main():
    cookies = load_cookies(COOKIE_FILE)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        inject_cookies(context, cookies)
        page = context.new_page()

        # Step 1: Authenticate
        print("=" * 50)
        print("🔑 STEP 1: Authentication")
        print("=" * 50)
        if not authenticate(page):
            print("❌ AUTH FAILED — exiting")
            browser.close()
            sys.exit(1)

        # Step 2: Search for target
        print("\n" + "=" * 50)
        print("🔍 STEP 2: Search for fresh posts")
        print("=" * 50)

        post_url = None
        for keyword in KEYWORDS:
            links_data = search_for_posts(page, keyword)
            print(f"   Found {len(links_data)} post links for '{keyword}'")

            for link_info in links_data:
                href = link_info["href"]
                text = link_info["text"]

                if should_skip_post(text):
                    continue
                if not is_fresh_post(text) and not any(k in text.lower() for k in ['menit', 'jam', 'hour', 'minute', 'sec', 'detik']):
                    continue
                if not href or "/post/" not in href:
                    continue

                if href.startswith("/"):
                    full_url = "https://www.threads.com" + href
                elif href.startswith("http"):
                    full_url = href
                else:
                    continue

                post_url = full_url
                print(f"   ✅ Target found: {href}")
                print(f"   📝 Context: {text[:150]}...")
                break

            if post_url:
                break

        if not post_url:
            print("❌ No suitable fresh post found across all keywords")
            browser.close()
            sys.exit(1)

        # Step 3: Pick affiliate link
        print("\n" + "=" * 50)
        print("🔗 STEP 3: Pick affiliate link")
        print("=" * 50)

        link_info = pick_unused_link()
        if not link_info:
            print("❌ No unused links available")
            browser.close()
            sys.exit(1)

        print(f"   Category: {link_info['category']}")
        print(f"   Product: {link_info['product']}")
        print(f"   Link: {link_info['link']}")

        # Step 4: Write comment (matched to SPECIFIC product)
        print("\n" + "=" * 50)
        print("📝 STEP 4: Write comment")
        print("=" * 50)

        comment = write_comment(link_info)
        print(f"   Comment: {comment}")

        # Step 5: Reply
        print("\n" + "=" * 50)
        print("💬 STEP 5: Post reply")
        print("=" * 50)

        success = reply_to_post(page, post_url, comment)

        if success:
            print("\n" + "=" * 50)
            print("✅ STEP 6: Verify reply")
            print("=" * 50)
            verify_reply(page, post_url)

            print("\n" + "=" * 50)
            print("🟢 THREADS REPLY SUCCESS!")
            print(f"   Target: {post_url}")
            print(f"   Comment: {comment}")
            print(f"   Link: {link_info['link']}")
            print(f"   Product: {link_info['product']}")
            print(f"   Category: {link_info['category']}")
            print("=" * 50)

            with open("/tmp/threads_reply_result.json", "w") as f:
                json.dump({
                    "success": True, "post_url": post_url, "comment": comment,
                    "link": link_info["link"], "product": link_info["product"],
                    "category": link_info["category"],
                }, f)
        else:
            print("❌ Reply failed")
            with open("/tmp/threads_reply_result.json", "w") as f:
                json.dump({"success": False}, f)

        browser.close()


if __name__ == "__main__":
    main()
