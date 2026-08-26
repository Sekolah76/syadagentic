#!/usr/bin/env python3
"""Threads Post Cron v5 — STORY MODE (jual cerita 3-beat) + category rotation + DB sync."""
import json, re, subprocess, sys, os, random, time, urllib.request, urllib.parse, shutil, ast
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

# Story engine (jual cerita)
sys.path.insert(0, str(Path.home() / ".hermes/scripts"))
from threads_story_engine import build_story_posts  # noqa: E402

DB_PATH = Path.home() / ".hermes/skills/affiliate/threads-auto-post/references/affiliate-link-database.md"
HISTORY_PATH = Path.home() / ".hermes/scripts/threads_post_history.json"
SCRIPT_PATH = Path.home() / ".hermes/scripts/threads_post_v6.py"
CONTENT_PATH = Path("/tmp/threads_post_content.json")

# Database copies to sync after post
DB_COPIES = [
    Path.home() / ".hermes/skills/affiliate/threads-auto-post/references/affiliate-link-database.md",
    Path.home() / ".hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md",
    Path.home() / ".hermes/skills/affiliate-website/references/affiliate-link-database.md",
    Path.home() / ".hermes/skills/threads-auto-reply/references/affiliate-link-database.md",
]

ALL_CATEGORIES = ["skincare", "parfum", "haircare", "makeup"]

# ── Multi-kategori HOOKS ──
HOOKS = {
    "skincare": {
        "edukasi": [
            "Tau gak sih, {product} itu underrated banget buat kulit. Padahal formulanya ringan dan gak bikin berminyak 🔥",
            "Banyak yang gak tau kalau {product} punya kandungan yang cocok banget buat kulit berminyak 📚",
            "Skincare gak harus ribet. Cuma butuh {product} yang bener dan konsisten 💡",
        ],
        "validasi_mental": [
            "Yang udah capek gonta-ganti skincare tapi hasilnya gitu-gitu aja, coba deh {product} ✋",
            "Lo gak sendirian kalau masih bingung milih skincare. Gw dulu juga gitu — sampai nemu {product} 💪",
        ],
        "storytelling": [
            "3 bulan lalu gw hampir nyerah sama skincare. Gw ganti ke {product} dan everything changed 😤",
            "Dulu gw tipe yang cuci muka doang. {product} yang pertama gw pake beneran 🫣",
        ],
        "problem_solving": [
            "Jerawat gak hilang-hilang? Ternyata solusinya simpel: {product} yang formulanya gentle 😭",
            "Kulit kusam meskipun udah minum air banyak? {product} bantu banget buat eksfoliasi 🛠️",
        ],
        "hook_pancingan": [
            "Hot take: {product} > skincare mahal. Gw udah coba keduanya 🗣️",
            "Jangan beli skincare sebelum baca ini. Gw review {product} secara jujur 📝",
        ],
        "transformasi": [
            "Before-after skincare gw 3 bulan lalu vs sekarang. Kuncinya: {product} 🤯",
            "Kalau lo liat foto gw 6 bulan lalu, pasti gak percaya. {product} beneran ngerubah 🔥",
        ],
    },
    "parfum": {
        "edukasi": [
            "Parfum mahal ≠ tahan lama. {product} buktinya — murah tapi performanya gila 🔥",
            "Rahasia parfum tahan lama bukan di harga. {product} ini formula EDP tapi harga receh 📚",
        ],
        "validasi_mental": [
            "Yang udah capek beli parfum mahal tapi sejam ilang, cobain {product} ✋",
            "Gue juga korban parfum overpriced. Sampe nemu {product} yang beneran worth it 💪",
        ],
        "storytelling": [
            "Ke kantor naik motor, sampe kantor masih wangi. Rahasianya? {product} 😤",
            "Dulu gue parfum-an tiap 3 jam. Sekarang cukup pagi doang pake {product} 🫣",
        ],
        "problem_solving": [
            "Parfum cepet ilang? Mungkin lo butuh {product} — EDP grade, harga minum boba 😭",
            "Bau badan balik pas siang? {product} ini yang nolong gue dari insecure parfum 🛠️",
        ],
        "hook_pancingan": [
            "5 parfum cowok under 100rb yang wanginya kayak jutaan. Nomor 3: {product} 👀",
            "Parfum Rp50rb tapi dikira parfum mall. {product} ini sleeper banget 🗣️",
        ],
    },
    "haircare": {
        "edukasi": [
            "Rambut rontok? Bukan shampo-nya yang salah. Tapi lo belum nemu {product} 📚",
            "Kebanyakan orang salah pilih haircare. {product} ini formulanya gentle tapi efektif 🔥",
        ],
        "validasi_mental": [
            "Yang udah gonta-ganti shampo tapi rambut makin rontok, {product} jawabannya ✋",
            "Gue ngerti struggle rambut lepek tiap siang. {product} ini yang akhirnya works 💪",
        ],
        "storytelling": [
            "Dari botak-botak ketempel shampo murahan, ke rambut sehat. Bedanya cuma {product} 😤",
            "Temen kantor nanya 'lo pake shampo apa?' sejak gue ganti ke {product} 🫣",
        ],
        "problem_solving": [
            "Ketombe bandel padahal udah coba 5 shampo? {product} ini yang bersihin sampe ke akar 😭",
            "Rambut kering kayak sapu ijuk? {product} ini lembabin tanpa bikin lepek 🛠️",
        ],
    },
    "makeup": {
        "edukasi": [
            "Makeup natural yang gak ketara makeup itu kuncinya di {product} 💡",
            "Pemula makeup? Mulai dari {product} — gampang dibaurin, gak cakey 📚",
        ],
        "validasi_mental": [
            "Yang udah nyerah sama makeup karena muka langsung cakey, {product} ini game changer ✋",
            "Gue juga dulu makeup-an muka langsung dempul. Terus ketemu {product} 💪",
        ],
        "storytelling": [
            "Pertama kali makeup-an ke kondangan pake {product}, dipuji 'cantik natural'. Padahal pemula 😭",
            "Dari malu makeup-an karena hasilnya aneh, ke pede foto deket. Semua gara-gara {product} 🫣",
        ],
        "problem_solving": [
            "Foundation geser pas siang? {product} ini yang stay dari pagi sampe malem 😭",
            "Lip tint yang transfer ke mana-mana? {product} ini tahan makan minum 🛠️",
        ],
    },
}

POST2_TEMPLATES = {
    "skincare": [
        "Awalnya gw skeptis. Tapi setelah 2 minggu rutin pake, tekstur kulit berubah. Gak perlu 10 step, cukup ini doang udah bikin kulit sehat. Pori-pori keliatan lebih rapet dan minyak berkurang.",
        "Yang bikin {product} beda: formulanya ringan tapi ngena. Gak bikin muka kering atau greasy. Cocok banget buat daily routine — pagi malem. Gw pribadi udah repurchase 3x.",
        "Jujur, gw udah coba banyak skincare. Yang mahal, yang viral, yang direview beauty vlogger. Tapi {product} ini yang bikin gw berhenti hunting. Simple tapi results-nya keliatan.",
        "Kenapa gw rekomen {product}? Karena formulanya balanced. Ada active ingredients-nya tapi gentle. Gak bikin purging parah. Dan yang paling penting: affordable buat pelajar/mahasiswa.",
    ],
    "parfum": [
        "Gw test: semprot jam 7 pagi. Jam 2 siang masih ada wanginya. Jam 6 sore masih samar-samar. Buat parfum harga segini? Ini gila. Performance-nya ngalahin parfum 300rb+ yang pernah gw pake.",
        "Yang bikin {product} beda: base note-nya kuat. Kebanyakan parfum murah cuma top note doang, 30 menit ilang. Ini dari awal sampe dry down konsisten. Cocok buat daily office atau nongkrong.",
        "Orang kantor gw nanya: 'lo pake parfum apa sih enak banget?' Gw tunjukin {product}. Mereka gak percaya harganya di bawah 100rb. Underrated parfum parah ini.",
        "Kunci {product}: semprot di titik nadi (leher, pergelangan), JANGAN diusap. Selesai. Gak perlu 10x semprot. Wanginya nyebar natural, gak nyengat. Rating: 9/10 buat harga segini.",
    ],
    "haircare": [
        "Setelah 2 minggu pake {product}, rambut rontok berkurang drastis. Biasanya tiap sisir rontok segenggam, sekarang cuma 2-3 helai. Rambut jadi lebih tebel dan gak lepek cepet.",
        "Yang gw suka dari {product}: gak bikin rambut kering kayak shampo antidandruff kebanyakan. Membersihkan tapi tetap lembab. Wanginya juga fresh, bukan wangi obat.",
        "Dulu gw harus keramas tiap hari karena rambut cepet lepek. Sekarang 2 hari sekali cukup sejak pake {product}. Scalp jadi lebih sehat, produksi minyak lebih terkontrol.",
        "Shampo ini ada cooling sensation-nya. Enak banget pas dipake, bikin seger di kulit kepala. Plus kandungan tea tree oil-nya bantu ngurangin gatel-gatel.",
    ],
    "makeup": [
        "Gw pake {product} dari jam 8 pagi, jam 6 sore masih stay. Gak touch-up sama sekali. Padahal cuaca panas + pake masker. Ini holy grail buat daily makeup.",
        "Tekstur {product} ringan banget. Kayak kulit kedua. Gak dempul, gak cakey, gak creasing di garis senyum. Cocok buat pemula yang takut makeup-an hasilnya aneh.",
        "Yang paling gw suka: shade-nya natural. Gak terlalu kuning, gak terlalu pink. Blend ke kulit Indonesia banget. Akhirnya nemu shade yang match setelah bertahun-tahun trial-error.",
        "Pake {product} cuma perlu 1 pump buat seluruh muka. Coverage-nya medium tapi buildable. Jerawat merah ketutup tanpa keliatan tebel. Worth every penny.",
    ],
}

CTAS = [
    "SE-SIMPEL nemu produk yang formulanya pas, semuanya berubah. Gw pake ini dan hasilnya gak bohong. Cek rekomendasi gw di bawah 👇",
    "Gw gak bakal rekomen sesuatu yang gw sendiri gak pake. Ini udah gw coba dan hasilnya real. Link-nya di bawah 👇",
    "Kalau lo lagi cari yang beneran works tanpa bikin kantong jebol, cek yang gw pake ini 👇",
    "Daripada lo trial-error sendiri, mending coba yang udah gw buktiin. Detailnya di bawah 👇",
    "Gw tau banyak pilihan di luar sana. Tapi ini yang gw sendiri pake dan repurchase. Link di bawah 👇",
]

SAVE_LINES = [
    "Save biar ga ilang 🫶",
    "Bookmark dulu sebelum lupa 📌",
    "Save buat nanti beli 🛍️",
    "Jangan lupa save ya 🤲",
    "Simpan dulu, beli nanti 💾",
]

KEYWORDS_BY_CATEGORY = {
    "skincare": ["skincare cowok", "rekomendasi skincare", "serum", "sunscreen", "moisturizer"],
    "parfum": ["parfum cowok", "rekomendasi parfum", "parfum murah", "parfum tahan lama"],
    "haircare": ["haircare", "rekomendasi shampoo", "rambut rontok", "shampoo cowok"],
    "makeup": ["makeup natural", "rekomendasi makeup", "lip tint", "foundation pemula"],
}

def detect_category(product_name):
    """Detect product category from name — comprehensive keyword matching."""
    p = product_name.lower()
    # Parfum: fragrance, edt, edp, eau de toilette, mist (except setting spray)
    if any(w in p for w in ["parfum", "fragrance", "edt", "edp", "eau de toilette", "perfume"]):
        return "parfum"
    if "mist" in p and "setting" not in p and "spray" not in p:
        return "parfum"
    # Haircare
    if any(w in p for w in ["hair", "shampoo", "conditioner", "rambut", "tonic", "ketombe", "rontok"]):
        return "haircare"
    # Makeup: comprehensive
    if any(w in p for w in [
        "lip", "makeup", "foundation", "cushion", "powder", "blush", "mascara",
        "eyeliner", "setting spray", "jelly", "tint", "gloss", "melting balm",
        "two way cake", "bb cream", "lipstik", "lipstick", "brows", "concealer",
        "contour", "highlighter", "eyeshadow",
    ]):
        return "makeup"
    # Skincare: default fallback
    return "skincare"

def load_history():
    if HISTORY_PATH.exists():
        data = json.loads(HISTORY_PATH.read_text())
        return data.get("posts", []) if isinstance(data, dict) else data
    return []

def get_used_hook_prefixes(history, n=10):
    return [p.get("hook_text", "")[:50].lower() for p in history[-n:]]

def pick_hook(category, hook_category, product, used_prefixes):
    cat_hooks = HOOKS.get(category, HOOKS["skincare"])
    templates = cat_hooks.get(hook_category, list(cat_hooks.values())[0])
    random.shuffle(templates)
    for tpl in templates:
        hook = tpl.replace("{product}", product)
        prefix = hook[:50].lower()
        overlap = False
        for up in used_prefixes:
            if up:
                words_new = set(prefix.split())
                words_old = set(up.split())
                if words_new and words_old:
                    ratio = len(words_new & words_old) / max(len(words_new), 1)
                    if ratio > 0.5:
                        overlap = True
                        break
        if not overlap:
            return hook
    return templates[0].replace("{product}", product)

def pick_hook_category(history, category):
    recent_cats = [p.get("hook_category", "") for p in history[-3:]]
    cat_hooks = HOOKS.get(category, HOOKS["skincare"])
    all_cats = list(cat_hooks.keys())
    available = [c for c in all_cats if c not in recent_cats]
    return random.choice(available) if available else random.choice(all_cats)

def get_recent_product_categories(history, n=8):
    """Get list of product categories from recent post history (newest first)."""
    cats = []
    for p in reversed(history[-n:]):
        cat = p.get("category", "")
        if cat:
            cats.append(cat)
    return cats

def pick_category_and_product(unused_by_cat, recent_cats):
    """Pick a category using rotation, then a product from that category.
    Prefer categories NOT in recent history. Cycle through all 4 before repeating."""
    # Categories with available products
    available_cats = [c for c in ALL_CATEGORIES if unused_by_cat.get(c)]
    if not available_cats:
        # Fallback: pick from whatever's available
        available_cats = [c for c, items in unused_by_cat.items() if items]
    if not available_cats:
        return None, None

    # Priority 1: categories not seen in last 4 posts (full rotation)
    recent_unique = list(dict.fromkeys(recent_cats))  # dedup preserving order
    fresh_cats = [c for c in available_cats if c not in recent_unique]
    if fresh_cats:
        cat = random.choice(fresh_cats)
        return cat, random.choice(unused_by_cat[cat])

    # Priority 2: least recently used (lowest idx = most recently seen)
    # Track last occurrence, so lowest idx = most recent → prefer highest
    cat_last_idx = {}
    for i, c in enumerate(reversed(recent_cats)):
        cat_last_idx[c] = i  # overwrite = keep last (newest) index
    for c in available_cats:
        if c not in cat_last_idx:
            cat_last_idx[c] = 999  # never used = lowest priority for picking
    available_cats.sort(key=lambda c: cat_last_idx.get(c, 999))  # ascending = prefer older
    cat = available_cats[0]
    return cat, random.choice(unused_by_cat[cat])

def _download_valid_image(url, output_path):
    """Download image only if real size/resolution, return (ok, pixels, kb)."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'image/webp,image/*,*/*'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp, open(output_path, 'wb') as f:
            shutil.copyfileobj(resp, f)
        kb = os.path.getsize(output_path) / 1024
        if kb < 20:
            return False, 0, kb
        im = Image.open(output_path)
        w, h = im.size
        if w < 250 or h < 250:
            return False, w * h, kb
        im.convert('RGB').save(output_path, 'jpeg', quality=92)
        return True, w * h, kb
    except Exception:
        return False, 0, 0


def download_pinterest_review_photo(product_name, output_path="/tmp/threads_post_image.jpg"):
    """Fallback real-looking review photo from Pinterest. Skips first 4 catalog/studio images."""
    print(f"📌 Fallback Pinterest review photo: {product_name}")
    queries = [
        f'"{product_name}" di tangan review',
        f'"{product_name}" review asli',
        f'"{product_name}" pemakaian',
        f'"{product_name}" swatches bibir',
        f'"{product_name}" honest review',
    ]
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(viewport={"width": 1440, "height": 900}, user_agent="Mozilla/5.0")
            page = ctx.new_page()
            for q in queries:
                page.goto(f"https://id.pinterest.com/search/pins/?q={urllib.parse.quote(q)}", timeout=30000)
                page.wait_for_timeout(5000)
                for _ in range(2):
                    page.mouse.wheel(0, 1500)
                    page.wait_for_timeout(1200)
                imgs = page.evaluate("""() => Array.from(document.querySelectorAll('img'))
                    .map(i => i.src).filter(s => s.includes('pinimg.com') && !s.includes('svg') && !s.includes('webapp'))""")
                targets = imgs[4:14] if len(imgs) > 4 else imgs
                for src in targets:
                    hq = src.replace('/236x/', '/736x/').replace('/474x/', '/736x/').replace('/564x/', '/736x/')
                    ok, pix, kb = _download_valid_image(hq, output_path)
                    if ok:
                        browser.close()
                        print(f"   ✅ Pinterest photo: {kb:.0f}KB | {pix} px | query={q}")
                        return output_path
            browser.close()
    except Exception as e:
        print(f"   ⚠️ Pinterest fallback gagal: {e}")
    return ""


def _resolve_shopee_shortlink(link):
    """Resolve Shopee shortlink to clean product URL (/product/{id}/{id})."""
    # If already product format, return as-is
    if '/product/' in link:
        return link.split('?')[0]

    try:
        r = subprocess.run(['curl', '-sI', '-L', '--max-time', '10', link],
            capture_output=True, text=True, timeout=15)
        output = r.stdout + r.stderr
        # Cari URL yg mengandung product ID (/x/y/z format → /product/y/z)
        urls = re.findall(r'https://shopee\.co\.id/[^\s?>\"\']+', output)
        for url in urls:
            clean = url.split('?')[0]
            m = re.match(r'https://shopee\.co\.id/(?:[^/]+)/(\d+)/(\d+)', clean)
            if m:
                # Convert ke format /product/{shop_id}/{item_id}
                return f'https://shopee.co.id/product/{m.group(1)}/{m.group(2)}'
        return link
    except:
        return link

def get_real_review_photo(link, product_name=None):
    """
    PRIMARY: Shopee real user review image via Camoufox.
    Resolves shortlink first → clicks "Penilaian" tab → extracts review images.
    """
    product_name = product_name or "product"
    print(f"📸 Cari foto review asli untuk: {product_name}...")
    output_path = "/tmp/threads_post_image.jpg"
    session_name = f"thr_r_{int(time.time())}"

    # Step 1: resolve shortlink
    resolved = _resolve_shopee_shortlink(link)
    print(f"   Resolved: {resolved}")

    try:
        r = subprocess.run(
            f'camoufox --session {session_name} browser open chrome_local_102130715962900495 "{resolved}" --headed',
            shell=True, capture_output=True, timeout=30)
        if r.returncode != 0:
            print("   ⚠️ Camoufox open gagal → skip image")
            return ""
        time.sleep(5)

        # Step 2: dismiss language popup
        r = subprocess.run(f'camoufox --session {session_name} state', shell=True, capture_output=True, text=True, timeout=10)
        state_html = r.stdout
        if 'Bahasa Indonesia' in state_html or 'Indonesia' in state_html:
            # click any button that says "Indonesia" or first available
            for ref_id in range(1, 10):
                if f'Indonesian' in state_html or f'Indonesia' in state_html:
                    subprocess.run(f'camoufox --session {session_name} click {ref_id}', shell=True, capture_output=True, timeout=5)
                    time.sleep(2)
                    break
                state_html = ''

        # Step 3: scroll sampai ketemu section PENILAIAN PRODUK
        # Ciri: ada tulisan "Penilaian Produk" + filter bintang (Semua, 5 Bintang, ...)
        subprocess.run(f'camoufox --session {session_name} wait stable --timeout 10000', shell=True, capture_output=True, timeout=15)
        time.sleep(2)
        found = False
        for attempt in range(30):
            r = subprocess.run(['camoufox', '--session', session_name, 'eval',
                'document.body.innerText.toLowerCase().includes("penilaian") || (document.querySelector("[class*=star]") !== null)'],
                capture_output=True, text=True, timeout=5)
            if 'true' in r.stdout.lower():
                found = True
                print(f"   Penilaian Produk ditemukan scroll ke-{attempt+1}")
                break
            subprocess.run(f'camoufox --session {session_name} scroll down --amount 1500', shell=True, capture_output=True, timeout=4)
            time.sleep(0.3)
        if not found:
            print("   ⚠️ Penilaian Produk gak ketemu, scroll ke bottom")
            for attempt in range(20):
                r = subprocess.run(f'camoufox --session {session_name} eval "window.scrollY + window.innerHeight >= document.body.scrollHeight ? \\"DONE\\" : \\"more\\""', shell=True, capture_output=True, text=True, timeout=5)
                if 'DONE' in r.stdout:
                    break
                subprocess.run(f'camoufox --session {session_name} scroll down --amount 2000', shell=True, capture_output=True, timeout=4)
                time.sleep(0.3)
        time.sleep(2)

        # Kalau masih ada floating chart/overlay, dismiss
        subprocess.run(f'camoufox --session {session_name} eval "document.querySelector(\'[class*=overlay], [class*=backdrop]\')?.remove()"', shell=True, capture_output=True, timeout=5)
        time.sleep(1)

        # Step 4: extract review images — ambil SEMUA, skip produk carousel
        # Produk gallery pake container class QN2lPu
        # Review images di luar container itu
        js_code = '''(() => {
            const urls = new Set();
            document.querySelectorAll('img').forEach(i => {
                let src = i.src || i.getAttribute('data-src') || '';
                if (!src || !src.includes('susercontent')) return;
                if (/icon|logo|banner|shopee|spay|voucher|chat|avatar/i.test(src)) return;
                
                // Skip produk carousel (parent class QN2lPu atau variasi lain)
                if (i.closest('[class*="QN2lPu"], [class*="product-gallery"], [class*="product-carousel"]')) return;
                
                let clean = src.replace(/_(tn|sm|watermark|cover|thumb)($|[.?_])/, '$2');
                urls.add(clean);
            });
            return JSON.stringify([...urls].filter(u => u.startsWith('http')).slice(0, 80));
        })()'''
        r = subprocess.run(['camoufox', '--session', session_name, 'eval', js_code], capture_output=True, text=True, timeout=20)
        raw = r.stdout.strip()
        # Parse JSON
        urls = []
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                urls = [u for u in parsed if isinstance(u, str) and u.startswith('http') and 'susercontent' in u]
        except:
            # Fallback: regex dari raw
            urls = re.findall(r'https?://[^"\'\\s,\]]+susercontent\.com[^"\'\\s,\]]+', raw)
        
        # Deduplikasi
        urls = list(dict.fromkeys(urls))
        print(f"   Found {len(urls)} susercontent images")

        subprocess.run(['camoufox', '--session', session_name, 'session', 'close'], stderr=subprocess.DEVNULL)

        if not urls:
            print("   ⚠️ Shopee no review images → skip image")
            return ""

        # Pick best image
        candidates = list(dict.fromkeys(urls))
        random.shuffle(candidates)

        best = None
        best_score = 0
        for u in candidates[:15]:
            tmp = f"/tmp/threads_candidate_{abs(hash(u))}.jpg"
            ok, pix, kb = _download_valid_image(u, tmp)
            if ok and pix > best_score:
                best, best_score = tmp, pix
        if best:
            shutil.move(best, output_path)
            print(f"   ✅ Shopee review photo valid: {Path(output_path).stat().st_size / 1024:.0f}KB")
            return output_path

        print("   ⚠️ Shopee images too small/invalid → skip image")
        return ""
    except Exception as e:
        print(f"   ⚠️ Shopee scraper error: {e} → skip image")
        try:
            subprocess.run(['camoufox', '--session', session_name, 'session', 'close'], stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return ""

def sync_all_db_copies():
    """Sync affiliate link DB to all 4 copies."""
    src = DB_COPIES[0]
    for dst in DB_COPIES[1:]:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text())
        except Exception:
            pass  # non-critical


def mark_link_used(link: str, product: str, story_type: str) -> bool:
    """Mark affiliate link ✅ USED in primary DB (line-safe, no regex row-merge)."""
    if not DB_PATH.exists():
        return False
    lines = DB_PATH.read_text().splitlines(keepends=True)
    today = time.strftime("%Y-%m-%d")
    note = f"✅ USED ({today}) — original post: [{story_type}] {product[:40]}"
    changed = False
    for i, line in enumerate(lines):
        if link in line and "❌ UNUSED" in line:
            lines[i] = line.replace("❌ UNUSED", note)
            changed = True
            break
    if not changed:
        return False
    DB_PATH.write_text("".join(lines))
    return True


def auto_reset_db_if_empty(used_links: set) -> int:
    """If no UNUSED remain (after history filter), reset all USED → UNUSED. Returns reset count."""
    text = DB_PATH.read_text()
    unused_n = len(re.findall(r"❌ UNUSED", text))
    if unused_n > 0:
        return 0
    lines = text.splitlines(keepends=True)
    n = 0
    for i, line in enumerate(lines):
        if "s.shopee.co.id" in line and "✅ USED" in line:
            # strip USED annotation back to UNUSED
            lines[i] = re.sub(r"✅ USED[^\n|]*", "❌ UNUSED", line)
            n += 1
    if n:
        DB_PATH.write_text("".join(lines))
        sync_all_db_copies()
        print(f"🔄 Auto-reset DB batch: {n} links → UNUSED")
    return n


def main():
    # ── Main ──
    history = load_history()
    used_links = {p.get("affiliate_link") for p in history if p.get("affiliate_link")}

    db_text = DB_PATH.read_text()
    unused_by_cat = {c: [] for c in ALL_CATEGORIES}

    for line in db_text.split("\n"):
        if "❌ UNUSED" in line and "s.shopee.co.id" in line:
            link_match = re.search(r'https://s\.shopee\.co\.id/\w+', line)
            if not link_match or link_match.group(0) in used_links:
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            product = "Product"
            for p in parts:
                if p and not p.startswith("`http") and "UNUSED" not in p and p != "-":
                    if not re.match(r'^#?\d+$', p.strip('#').strip()):
                        product = p
                        break
            cat = detect_category(product)
            unused_by_cat[cat].append({"link": link_match.group(0), "product": product})

    # Count total — auto-reset if empty
    total_unused = sum(len(v) for v in unused_by_cat.values())
    if total_unused == 0:
        if auto_reset_db_if_empty(used_links) > 0:
            # rebuild after reset, still respect history link dedup
            unused_by_cat = {c: [] for c in ALL_CATEGORIES}
            db_text = DB_PATH.read_text()
            for line in db_text.split("\n"):
                if "❌ UNUSED" in line and "s.shopee.co.id" in line:
                    link_match = re.search(r'https://s\.shopee\.co\.id/\w+', line)
                    if not link_match or link_match.group(0) in used_links:
                        continue
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    product = "Product"
                    for p in parts:
                        if p and not p.startswith("`http") and "UNUSED" not in p and p != "-":
                            if not re.match(r'^#?\d+$', p.strip('#').strip()):
                                product = p
                                break
                    cat = detect_category(product)
                    unused_by_cat[cat].append({"link": link_match.group(0), "product": product})
            total_unused = sum(len(v) for v in unused_by_cat.values())

    if total_unused == 0:
        print("❌ Post gagal — database link kosong (history juga penuh)")
        sys.exit(1)

    # Category rotation pick
    recent_cats = get_recent_product_categories(history, n=8)
    category, pick = pick_category_and_product(unused_by_cat, recent_cats)

    if not pick:
        print("❌ Post gagal — no product in rotation")
        sys.exit(1)

    link = pick["link"]
    product = pick["product"]
    product_short = product[:40].strip() if len(product) > 40 else product

    # ── STORY MODE v1: jual cerita 3-beat (no hard sell di post 1-2) ──
    # Retry story generation if dedup would reject (story type / hook phrasing)
    from threads_post_v6 import check_dedup  # local hard dedup same as executor

    story = None
    last_reason = ""
    for attempt in range(8):
        candidate = build_story_posts(
            category=category,
            product=product,
            link=link,
            history=history,
        )
        ok, reason = check_dedup(
            history,
            candidate["affiliate_link"],
            candidate["story_type"],
            candidate["hook_text"],
        )
        if ok:
            story = candidate
            break
        last_reason = reason
        # if link itself is the issue, abort (should not happen after unused filter)
        if "Link already used" in reason:
            print(f"❌ Post gagal — {reason}")
            sys.exit(1)

    if not story:
        print(f"❌ Post gagal — story dedup exhausted: {last_reason}")
        sys.exit(1)

    hook_cat = story["story_type"]
    keywords = KEYWORDS_BY_CATEGORY.get(category, KEYWORDS_BY_CATEGORY["skincare"])

    # Generate Image — REAL review photo from Shopee (bintang 5), bukan AI
    image_path = get_real_review_photo(link, product_short)

    content = {
        "post_1": story["post_1"],
        "post_2": story["post_2"],
        "post_3": story["post_3"],
        "affiliate_link": link,
        "product_name": product,
        "hook_category": hook_cat,  # story_type (compat history/dedup)
        "story_type": hook_cat,
        "category": category,
        "hook_text": story["hook_text"],
        "keywords": keywords,
        "image_path": image_path,
        "content_mode": "story_v1",
    }

    CONTENT_PATH.write_text(json.dumps(content, indent=2, ensure_ascii=False))

    # Run post script
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(CONTENT_PATH)],
        capture_output=True, text=True, timeout=300
    )

    if result.returncode == 0:
        # mark USED only after real success
        if mark_link_used(link, product, hook_cat):
            sync_all_db_copies()
            print("📝 DB marked USED + synced")
        else:
            sync_all_db_copies()
            print("⚠️ DB mark USED failed (link line not found) — history still records")
        print(f"✅ Post SUCCESS")
        print(f"📦 {product}")
        print(f"🏷️ {category} | story:{hook_cat}")
        print(f"📖 {story['post_1'][:70]}")
        print(f"🔗 {link}")
        print(f"🔄 Rotation: {recent_cats[-4:]}")
        remaining = {c: len([x for x in unused_by_cat[c] if x['link'] != link]) for c in ALL_CATEGORIES if unused_by_cat[c]}
        print(f"📊 Stock: {remaining}")
    else:
        output = result.stdout or ""
        stderr = result.stderr or ""
        error_msg = ""
        for line in (output + "\n" + stderr).split('\n'):
            if any(w in line.upper() for w in ['ERROR', 'DEDUP', 'FAILED', 'REJECT']):
                error_msg = line.strip()
                break
        print(f"❌ Post FAILED")
        print(f"📦 {product}")
        print(f"🏷️ {category} | story:{hook_cat}")
        if error_msg:
            print(f"⚠️ {error_msg}")
        # surface last lines for no_agent alert
        tail = "\n".join((output + "\n" + stderr).strip().split("\n")[-8:])
        if tail:
            print(tail)

    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
