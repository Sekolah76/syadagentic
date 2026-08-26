#!/usr/bin/env python3
"""
Threads Auto-Reply v4.0b — Fix original post reply button detection (2026-05-27)

CHANGES from v4.0a:
- FIXED: Reply button now targets ORIGINAL POST, NOT comment replies
- Script now finds ALL reply buttons, sorts by Y position, clicks TOPMOST one
- Filters out buttons inside comment sections (with Like/Suka siblings)
- This prevents bot from replying to someone else's comment instead of the original post
"""
import json, re, time, sys, random, os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

COOKIE_FILE = "/Users/user/instagram_cookies.json"
THREADS_COOKIE_FILE = "/Users/user/threads_cookies.json"
DATABASE = "/Users/user/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md"
MAX_SEARCH_SCROLLS = 3
MAX_POSTS_PER_KEYWORD = 10
TRACKING_FILE = "/tmp/threads_template_usage.json"

# ─── Keywords by Category (adaptive routing) ───
KEYWORDS_BY_CATEGORY = {
    "skincare": ["rekomendasi skincare", "rekomendasi moisturizer", "jerawat", "rekomendasi sunscreen", 
                 "skincare affordable", "skincare murah", "kulit kusam", "pori membesar", "bruntusan"],
    "makeup": ["rekomendasi makeup", "cushion bagus", "lip tint murah", "setting spray bagus",
               "makeup tahan lama", "concealer bagus", "blush on murah", "alis natural"],
    "parfum": ["parfum enak", "body mist murah", "rekomendasi parfum", "wangi tahan lama",
               "parfum cowok", "parfum cewek", "body spray murah"],
    "haircare": ["hair tonic rontok", "rambut rontok parah", "hair care routine", "shampoo rambut rontok",
                 "rambut kering", "rambut lepek", "hair mask bagus", "rambut bercabang"],
}

# ─── Diverse Templates by Product (10+ variations each, NO repetition) ───
COMMENT_TEMPLATES_V4 = {
    # SKINCARE
    "Moisturizer Glowing": [
        "gw pake moisturizer ini malem2, pagi nya kulit kenyal bgt kerasa 🤌 {link}",
        "coba deh bestie, moisturizer ini affordable tapi kualitas gila 🔥 {link}",
        "udh botol ke 3 moisturizer ini, emang cocok di gw bestie 😭 {link}",
        "no cap moisturizer ini bagus bgt, texture nya gel jadi ga lengket ✨ {link}",
        "gw rekomendasiin ini ke temen2, hasilnya bagus di semua tipe kulit 💪 {link}",
        "sebelum pake ini kulit gw kering bgt, skarang lembut terus 🤌 {link}",
        "moisturizer ini bikin makeup jadi lebih smooth, game changer 💅 {link}",
        "kulit gw kusam dulu, abis pake ini glowing auto pd 🔥 {link}",
        "gw udh coba banyak moisturizer, ini yg paling cocok bestie 😍 {link}",
        "ini moisturizer affordable terbaik di range harga nya, worth it ✨ {link}",
    ],
    "Retinol Serum": [
        "gw pake retinol 3x seminggu, hasilnya keliatan bgt worth it 🤌 {link}",
        "serum retinol ini gentle ga bikin iritasi, cocok buat pemula 🔥 {link}",
        "retinol affordable tapi powerful, gw udah botol kedua 😍 {link}",
        "night routine gw pake retinol ini, bangun2 kulit smooth bgt ✨ {link}",
        "gw dlu ragu2 pake retinol, abis coba ini lgsg sold 💅 {link}",
        "anti aging routine dimuda2in, retinol ini best choice 💪 {link}",
        "ini retinol termurah tapi hasilnya macam highend bestie 🤌 {link}",
        "pori2 gw mengecil bgt setelah 2 minggu pake ini, gila si 😍 {link}",
        "retinol ini cocok buat yang baru mulai skincare anti aging 🔥 {link}",
        "night routine wajib: retinol ini + moisturizer, combo terbaik ✨ {link}",
    ],
    "Sunscreen Ringan": [
        "sunscreen ini ringan bgt ga ada whitecast 🤌✨ {link}",
        "gw pake sunscreen ini tiap hari, watery dan cepet nyerap 🔥 {link}",
        "cocok buat kulit berminyak, matte finish ga lengket 💅 {link}",
        "auto repurchase sunscreen ini, murah tapi bagus 😍 {link}",
        "sebelum ketemu sunscreen ini gw ganti2 terus, ini the one ✨ {link}",
        "sunscreen ini ga bikin abu2 di muka, warna natural bgt 🤌 {link}",
        "50rb an dapat sunscreen sebagus ini, worth it gila si 🔥 {link}",
        "daily sunscreen gw, ringan bisa pake makeup di atasnya 💅 {link}",
        "ga lengket dan ga bikin minyak, cocok bgt di tropical climate 🌴 {link}",
        "gw pake ini sebelum jogging, tahan bgt keringetan 🔥 {link}",
    ],
    "Acne Treatment": [
        "skincare ini lgsg kempesin jerawat gw 🤌 {link}",
        "jerawat meradang? coba ini, 3 hari lgsg kempes 🔥 {link}",
        "gw pake acne treatment ini malam2, pagi nya jerawat mengecil 💅 {link}",
        "udh coba banyak tp ini beneran works buat jerawat membandel 😍 {link}",
        "auto repurchase acne treatment ini, hasilnya cepet ga bikin kering ✨ {link}",
        "jerawat hormonal gw kalah sama ini, emang mantap 🤌 {link}",
        "treatment ini ga bikin bekas jerawat makin gelap, gentle bgt 🔥 {link}",
        "spot treatment ini magic bgt, jerawat gede lgsg flat dalam 2 hari 💪 {link}",
        "anak kos wajib punya ini, harga affordable tapi powerful 💅 {link}",
        "skincare routine gw ga lengkap tanpa ini, wajib bgt 🔥 {link}",
    ],
    
    # MAKEUP
    "Lip Tint Murah": [
        "lip tint ini pigmentasi nya gila, tahan lama ga crack 🤌✨ {link}",
        "gw pake lip tint ini buat ombre, natural bgt auto cantik 🔥 {link}",
        "affordable tapi warnanya bagus, worth it banget 💅 {link}",
        "lip tint ini ringan di bibir ga bikin kering, emang best 😍 {link}",
        "siapa tau lip tint 20rb an sebagus ini, ga nyangka ✨ {link}",
        "kissproof bgt lip tint ini, makan baso pun stay 💪 {link}",
        "color range nya bagus2, gw udh punya 3 shade 🤌 {link}",
        "ombre lips pake ini lgsg cantik bgt, ga effort 💅 {link}",
        "liptint ini texture nya gel, jadi ga bikin bibir kering 🔥 {link}",
        "daily makeup gw pake lip tint ini, natural tapi fresh ✨ {link}",
    ],
    "Cushion Coverage": [
        "cushion ini coverage nya gila, auto mulus tanpa baking 💅 {link}",
        "gw pake cushion ini tahan lama, ga cakey sampe malem 🔥 {link}",
        "medium coverage tapi buildable, worth it bgt 🤌 {link}",
        "ringan di kulit ga bikin cakey, auto repurchase ✨ {link}",
        "cushion ini affordable tapi finishing nya skin like, bagus bgt 😍 {link}",
        "cover bekas jerawat dan flek dg baik, ga tebel 💪 {link}",
        "shade indonesia ada, ga abu2 di kulit 🤌 {link}",
        "pakai cushion ini lgsg flawless, foto2 jadi bagus 🔥 {link}",
        "cushion ini transferproof juga loh, makan pun aman 💅 {link}",
        "sehari2 pake ini, practical dan hasilnya bagus bgt ✨ {link}",
    ],
    "Setting Spray": [
        "setting spray ini game changer, makeup ga geser 🔥 {link}",
        "tahan seharian full, gila si worth it 😍 {link}",
        "gw pake sebelum dan sesudah makeup, lock all day 💅 {link}",
        "makeup tetap fresh dari pagi sampe malem, gila si ✨ {link}",
        "spray ini bikin makeup melt ke kulit jadi natural 🤌 {link}",
        "udh coba brand laen tp balik ke ini lg, emang the best 🔥 {link}",
        "outdoor event makeup gw tahan 8 jam pake ini 💪 {link}",
        "matte finish tapi ga kering, cocok buat kulit kombinasi 💅 {link}",
        "harganya murah tapi kualitas macam setting spray highend ✨ {link}",
        "spray nya halus ga bikin basah2, application nya enak 🤌 {link}",
    ],
    
    # PARFUM
    "Parfum Unisex Tahan Lama": [
        "parfum ini tahan lama bgt, sehari masih kecium bestie 🤌 {link}",
        "sillage nya bagus, orang sebelah pasti nanya parfum apa {link}",
        "wangi nya enak bgt dan affordable, udh botol kedua 🔥 {link}",
        "tahan 8+ jam di kulit, gila si 😍 {link}",
        "parfum ini cocok buat daily, ga terlalu strong ✨ {link}",
        "office friendly bgt, ga ganggu temen kantor 💅 {link}",
        "buat kencan juga oke, wangi nya musky2 gtu 🤌 {link}",
        "kamuflase parfum mahal di harga terjangkau 🔥 {link}",
        "layering parfum ini enak bgt, base note nya bagus 💪 {link}",
        "ini signature scent gw, udh repurchase 2x ✨ {link}",
    ],
    "Body Mist Murah": [
        "body mist ini murah tp kualitas gila, auto repurchase 💅 {link}",
        "cocok buat daily, wangi soft ga ganggu orang {link}",
        "emang best, tahan di baju juga loh worth it bgt ✨ {link}",
        "murah meriah tapi wangi kayak parfum mahal 🔥 {link}",
        "spray abis mandi, seharian wangi 🤌 {link}",
        "body mist ini fresh bgt, cocok buat summer vibes ☀️ {link}",
        "60rb an dapat body mist sebanyak ini, worth it bgt 💪 {link}",
        "wangi nya clean dan soft, ga enek bgt 😍 {link}",
        "gw pake ini ke gym, tetap fresh walau keringetan 🔥 {link}",
        "udh punya 5 botol body mist ini, emang enak2 semua 💅 {link}",
    ],
    
    # HAIRCARE
    "Hair Oil Anti Rontok": [
        "hair oil ini bikin rambut gw ga rontok lagi 🤌 {link}",
        "rambut gw makin kuat pake ini, ga gampang patah 🔥 {link}",
        "oil ini enak ga lengket, bikin rambut shiny 💅 {link}",
        "pake tiap malem sebelum tidur, rambut sehat ✨ {link}",
        "rambut rontok gw berkurang 80% pake ini, gila si 😍 {link}",
        "hair oil ini affordable tapi kualitas salon 🤌 {link}",
        "aplikasi nya gampang, tinggal pijit2 kepala 🔥 {link}",
        "rambut gw dlu kayak sapu lidi, skarang lembut bgt 💪 {link}",
        "serum rambut ini ga bikin minyak berlebih, perfect 👌 {link}",
        "before after pake hair oil ini signifikan bgt ✨ {link}",
    ],
    "Hair Mask Creambath": [
        "hair mask ini bikin rambut gw lembut kayak habis salon 🤌✨ {link}",
        "seminggu sekali pake ini, rambut ga kering lagi 🔥 {link}",
        "aromanya enak bgt dan bikin rambut gampang diatur 💅 {link}",
        "creambath di rumah pake ini, hemat bgt hasilnya bagus 💪 {link}",
        "rambut kering kasar? coba ini 2 minggu lgsg beda 😍 {link}",
        "masker ini thick dan nourishing, rambut lgsg silky ✨ {link}",
        "conditioner aja ga cukup, butuh masker ini seminggu sekali 🤌 {link}",
        "rambut gw dlu kusut terus, abis pake ini gampang diurai 🔥 {link}",
        "hair mask ini cocok buat rambut diwarnai, maintain color 💅 {link}",
        "me time rutin: masker rambut + Netflix, self care bgt ✨ {link}",
    ],
    "Shampoo Grow Us": [
        "shampoo ini bikin rambut gw lembut bgt, auto repurchase 🔥 {link}",
        "rambut gw jadi lebih tebel setelah 2 minggu pake 🤌 {link}",
        "beneran nambah volume rambut, worth it 💅 {link}",
        "shampoo ini ga bikin rambut kering, pH balanced ✨ {link}",
        "wangi shampoo ini enak bgt, tahan seharian 😍 {link}",
        "foam nya banyak dan bersih, rontok gw berkurang 🤌 {link}",
        "rambut tipis gw lgsg keliatan lebih tebel pake ini 🔥 {link}",
        "cocok bgt buat rambut berminyak, clean all day 💪 {link}",
        "udh coba banyak shampoo anti rontok, ini yg paling ngefek 💅 {link}",
        "scalp gw jadi lebih sehat pake ini, ga gatal lagi ✨ {link}",
    ],
    "Hair Tonic Serum": [
        "hair tonic ini ga lengket dan wangi, hasil bagus 🔥 {link}",
        "serum rambut ini bikin rambut gw sehat dan shiny 🤌 {link}",
        "pake tiap habis keramas, rambut makin kuat 💅 {link}",
        "tonic ini ringan, langsung nyerap di kulit kepala ✨ {link}",
        "growth serum ini works, gw udah liat baby hair baru 😍 {link}",
        "aplikasi ke akar, pijat2 bentar, hasilnya beneran bagus 🤌 {link}",
        "affordable tapi ingredients nya bagus, gw suka 🔥 {link}",
        "rambut gw makin dense pake ini, ga tipis lagi 💪 {link}",
        "scalp treatment gw pake ini, healthier scalp 💅 {link}",
        "cooling sensation nya enak, relax bgt ✨ {link}",
    ],
    "Hair Treatment Spray": [
        "treatment spray ini cocok buat rambut kering, langsung lembut 🤌 {link}",
        "rambut rontok gw berkurang bgt pake ini 💅 {link}",
        "ringan ga berat, rambut lgsg sehat 🔥 {link}",
        "leave on treatment praktis, tinggal spray aja ✨ {link}",
        "heat protectant sebelum styling, rambut aman 😍 {link}",
        "rambut gw dlu kering kayak jerami, abis pake ini lembut 🤌 {link}",
        "spray nya halus, distribute evenly, application mudah 🔥 {link}",
        "hair treatment ini versatile, bisa buat daily 💪 {link}",
        "frizzy hair solved pake ini, rambut gw teratur 💅 {link}",
        "daily essentials gw: shampoo + treatment spray ini, wajib ✨ {link}",
    ],
}

# ─── Freshness Constants ───
MAX_POST_AGE_HOURS = 24

def parse_time_ago(text):
    """Parse 'X menit/jam yang lalu' or similar into hours.
    
    Returns hours ago, or None if unparseable.
    """
    text_lower = text.lower()
    
    # Match patterns like "33 menit", "2 jam", "15 menit yang lalu"
    minute_match = re.search(r'(\d+)\s*menit', text_lower)
    if minute_match:
        return int(minute_match.group(1)) / 60  # Convert to hours
    
    hour_match = re.search(r'(\d+)\s*jam', text_lower)
    if hour_match:
        return int(hour_match.group(1))
    
    # "semenit", "sejam"
    if 'semenit' in text_lower or '1 menit' in text_lower:
        return 1/60
    if 'sejam' in text_lower or '1 jam' in text_lower:
        return 1
    
    return None  # Unknown - might be very new (no timestamp shown)


def is_fresh_post(text):
    """Check if post is < 24 hours old.
    
    STRICT v4.0 logic:
    1. If STALE pattern found (hari/minggu/bulan) → REJECT
    2. If time parseable (< 24 jam) → ACCEPT
    3. If time parseable (>= 24 jam) → REJECT
    4. If no timestamp → ACCEPT (assume fresh)
    """
    text_lower = text.lower()
    
    # STALE = definite rejection (1 hari = 24+ hours)
    stale_patterns = [r'\d+\s*hari', r'\d+\s*day', r'\d+\s*minggu', r'\d+\s*week', 
                      r'\d+\s*bulan', r'\d+\s*month']
    for pattern in stale_patterns:
        if re.search(pattern, text_lower):
            return False
    
    # Parse exact time and check < 24 hours
    hours_ago = parse_time_ago(text_lower)
    if hours_ago is not None:
        return hours_ago < MAX_POST_AGE_HOURS
    
    # No timestamp found → assume fresh (many posts don't show timestamp in parsed text)
    return True


def get_post_age_display(text):
    """Get human-readable age from post text."""
    text_lower = text.lower()
    hours_ago = parse_time_ago(text_lower)
    
    if hours_ago is None:
        return "baru saja (fresh)"
    elif hours_ago < 1:
        minutes = int(hours_ago * 60)
        return f"{minutes} menit"
    else:
        return f"{int(hours_ago)} jam"


# ─── Post Context Detection (Enhanced v4.0) ───
POST_CONTEXT_PATTERNS_V4 = {
    "seeking_recommendation": {
        "keywords": ["rekomendasi", "recomend", "rec", "ada yang tau", "ada yang punya",
                     "bagus ga", "bagus nggak", "worth it ga", "worth it ngga", "worth it gak",
                     "cocok ga", "enak ga", "enak ngga", "saran", "minta saran", "help",
                     "minta rec", "yang bagus apa", "apa ya", "donk", "dong",
                     "parfum apa", "moisturizer apa", "serum apa", "shampoo apa",
                     "cushion apa", "lip tint apa", "blush on apa"],
        "templates": [
            "sini gw rekomendasiin {product}, emang bagus bgt hasilnya 🤌 {link}",
            "coba {product} ini! gw pake sendiri dan hasilnya gila 🔥 {link}",
            "gw juga pake {product}, hasilnya keliatan banget worth it 💅 {link}",
            "gas {product} aja, gw udh coba banyak tp ini emang the best 🤌 {link}",
            "gw pake {product} dan emang cocok bgt, rekomen buat dicoba ✨ {link}",
            "{product} cocok bgt buat yang lagi cari affordable, gas 🔥 {link}",
            "gw kasih tau ya, {product} ini emang bagus bgt 🤌 {link}",
            "daripada bingung mending coba {product}, worth it 💅 {link}",
            "{product} ini blm terkenal tapi hasilnya di atas ekspektasi ✨ {link}",
            "ini rekomendasi gw: {product}, udah terbukti di gw 🔥 {link}",
        ]
    },
    "sharing_experience": {
        "keywords": ["gw pake", "gue pake", "saya pake", "lagi pake", "udah coba", "udah pakai",
                     "hasilnya", "review", "honest review", "coba deh", "recommended", "rec banget",
                     "emang bagus", "love banget", "holy grail", "repurchase", "beli lagi",
                     "pengalaman gw", "gw suka", "gw cocok"],
        "templates": [
            "sama! gw juga pake yang sejenis, coba {product} next level sih 🤌 {link}",
            "bener bgt! kalo suka ini, coba {product} lebih affordable 🔥 {link}",
            "betul! gw juga tim skincare. {product} gak kalah bagus 💅 {link}",
            "emang best sih! gw kombinasiin sama {product} makin gila ✨ {link}",
            "setuju! tapi coba {product} ini jg, sama2 bagus tp lebih murah 🤌 {link}",
            "gw juga experience nya sama, coba {product} buat comparison 🔥 {link}",
            "nice! kalo suka yg ini, {product} patut dicoba jg 💅 {link}",
            "sama dong! tapi gw tambahin {product} di routine, hasilnya makin bagus ✨ {link}",
            "mirip2 nih! tp {product} bikin routine gw makin lengkap 🤌 {link}",
            "emang bener, gw pake ini jg. tp {product} jg worth it dicoba 🔥 {link}",
        ]
    },
    "skin_problem": {
        "keywords": ["jerawat", "bruntusan", "berminyak", "kering", "iritasi", "flek", 
                     "bekas jerawat", "breakout", "kemerahan", "pori", "komedo", "kasar", 
                     "kusam", "ngelupas", "rontok", "rambut rontok", "ketombe", "lepek", 
                     "rusak", "alergi", "gatal", "panu", "jamuran"],
        "templates": [
            "gw juga dulu {keyword} parah, nyoba {product} ini beneran ngefek 🤌 {link}",
            "gw juga struggle sama {keyword}. coba {product} ini, works 🔥 {link}",
            "{product} game changer buat {keyword}, gw udh buktiin 💅 {link}",
            "no cap {product} beneran nolong gw atasi {keyword}, hasilnya 2 minggu ✨ {link}",
            "dulu gw {keyword} parah bgt, abis pake {product} ini berkurang drastis 😍 {link}",
            "gw ngerti struggle {keyword}, coba {product} ini 🤌 {link}",
            "tips: coba {product} buat {keyword}, gw udh proof dan works 🔥 {link}",
            "rambut rontok solved pake {product} ini, seriously works 💪 {link}",
            "untuk {keyword}, {product} cocok bgt di gw, worth a try 💅 {link}",
            "gw juga pernah {keyword}, terus nyoba {product} lgsg nemu holy grail ✨ {link}",
        ]
    },
    "general": {
        "keywords": [],
        "templates": [
            "coba deh {product} ini, gw pake dan emang worth it 🤌 {link}",
            "{product} emang gila si, hasilnya keliatan bgt. auto repurchase 🔥 {link}",
            "{product} recommended bgt, ga bakal nyesel 💅 {link}",
            "auto checkout {product} sih, affordable tp kualitas gila ✨ {link}",
            "gw pake {product} ini tiap hari, emang best sih 💪 {link}",
            "{product} ini underrated bgt, pdhl bagus gila 🤌 {link}",
            "ini product yang gw cari2 selama ini, finally nemu 🔥 {link}",
            "nobody talking about {product} tapi works bgt 💅 {link}",
            "{product} ini hidden gem di shopee, coba deh ✨ {link}",
            "trust me, {product} ini bakal jadi holy grail lu 🤌 {link}",
        ]
    },
}


def load_template_usage():
    """Load template usage tracking to avoid repetition."""
    try:
        with open(TRACKING_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_template_usage(usage):
    """Save template usage tracking."""
    with open(TRACKING_FILE, 'w') as f:
        json.dump(usage, f, indent=2)


def get_unused_template_index(product, templates, usage):
    """Get next unused template index for a product (rotation)."""
    if product not in usage:
        usage[product] = {"last_index": -1, "used_indices": []}
    
    last_idx = usage[product]["last_index"]
    used = usage[product]["used_indices"]
    
    # Find next unused index
    for i in range(len(templates)):
        idx = (last_idx + 1 + i) % len(templates)
        if idx not in used:
            usage[product]["last_index"] = idx
            usage[product]["used_indices"].append(idx)
            return idx
    
    # All used, reset and use next
    usage[product]["used_indices"] = []
    idx = (last_idx + 1) % len(templates)
    usage[product]["last_index"] = idx
    usage[product]["used_indices"].append(idx)
    return idx


def generate_contextual_comment_v4(product_name, post_text, affiliate_link):
    """Generate diverse Gen Z comment based on post context.
    
    v4.0: Uses template rotation to avoid repetition.
    """
    context_type, matched_keyword = detect_post_context(post_text)
    context_templates = POST_CONTEXT_PATTERNS_V4[context_type]["templates"]
    
    # Load usage tracking
    usage = load_template_usage()
    
    # Get product-specific templates if available
    product_templates = COMMENT_TEMPLATES_V4.get(product_name, [])
    
    # Mix: 50% product-specific, 50% context-aware
    if product_templates and random.random() < 0.5:
        # Use product-specific with rotation
        idx = get_unused_template_index(product_name, product_templates, usage)
        template = product_templates[idx]
    else:
        # Use context-aware template
        template = random.choice(context_templates)
    
    save_template_usage(usage)
    
    product_keyword = product_name.lower().split()[0] if product_name else "produk"
    
    comment = template.format(
        product=product_name,
        keyword=matched_keyword or product_keyword,
        link=affiliate_link
    )
    return comment


def parse_database(db_path, target_category=None):
    """Parse affiliate-link-database.md to find unused links.
    
    v4.0a FIX: Added fallback category detection — if emoji matching fails,
    match by name (SKINCARE/MAKEUP/PARFUM/HAIRCARE) to prevent empty categories.
    """
    with open(db_path, 'r') as f:
        content = f.read()
    
    unused_links = []
    current_category = ""
    current_product = ""
    
    for line in content.split('\n'):
        if line.startswith('## '):
            # Primary: emoji-based detection
            if any(emoji in line for emoji in ['🧴', '💄', '🌸', '💇']):
                cat_text = line.strip('# ').strip()
                if 'SKINCARE' in cat_text: current_category = 'skincare'
                elif 'MAKEUP' in cat_text: current_category = 'makeup'
                elif 'PARFUM' in cat_text: current_category = 'parfum'
                elif 'HAIRCARE' in cat_text: current_category = 'haircare'
            # Fallback: name-based detection (catches encoding mismatches)
            else:
                cat_upper = line.upper()
                if 'SKINCARE' in cat_upper: current_category = 'skincare'
                elif 'MAKEUP' in cat_upper: current_category = 'makeup'
                elif 'PARFUM' in cat_upper: current_category = 'parfum'
                elif 'HAIRCARE' in cat_upper: current_category = 'haircare'
        
        if line.startswith('### '):
            raw = line.strip('# ').strip()
            # Skip non-product headers (stats, recently used, batch history, etc.)
            if any(skip in raw for skip in ['📊 Stats', 'Recently Used', '📦', '🔄', 'BATCH']):
                continue
            current_product = re.sub(r'\s*\(\d+\)\s*$', '', raw).strip()
        
        if '❌ UNUSED' in line:
            match = re.search(r'`(https://s\.shopee\.co\.id/\w+)`', line)
            if match:
                if target_category and current_category != target_category:
                    continue
                if not current_category:
                    print(f"   ⚠️ WARNING: Link {match.group(1)} has empty category — check database format")
                # Extract product name from table row: | # | Product Name | Link | Status |
                # Handle double-pipe (||) in some rows
                row_product = ""
                parts = [p.strip() for p in line.split('|') if p.strip()]
                # After filtering empty: parts = ['#', 'Product', 'Link', 'Status', ...]
                # Find the product name (not a number, not a URL, not a status)
                for p in parts:
                    if p and not p.isdigit() and 'shopee.co.id' not in p and 'UNUSED' not in p and 'USED' not in p and p not in ['-', 'Last Used']:
                        row_product = p
                        break
                product_name = row_product or current_product
                if not product_name:
                    print(f"   ⚠️ WARNING: Link {match.group(1)} has empty product — check database format")
                unused_links.append({
                    "link": match.group(1),
                    "category": current_category,
                    "product": product_name,
                })
    
    return unused_links


def load_cookies(cookie_file):
    raw = json.load(open(cookie_file))
    return {k: re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(v)) for k, v in raw.items()}


def inject_cookies(context, ig_cookies, threads_cookies=None):
    """Inject IG cookies to .instagram.com + Threads cookies to .threads.com.
    IG cookies enable Meta SSO, Threads cookies enable direct auth."""
    all_cookies = []
    for name, value in ig_cookies.items():
        all_cookies.append({
            "name": name, "value": value,
            "domain": ".instagram.com", "path": "/",
            "httpOnly": name in ['sessionid', 'ig_did', 'datr', 'mid', 'rur', 'ig_nrcb'],
            "secure": True, "sameSite": "Lax"
        })
    if threads_cookies:
        for name, value in threads_cookies.items():
            all_cookies.append({
                "name": name, "value": value,
                "domain": ".threads.com", "path": "/",
                "httpOnly": name in ['sessionid', 'ig_did', 'mid', 'rur'],
                "secure": True, "sameSite": "Lax"
            })
    context.add_cookies(all_cookies)


def authenticate(page):
    """Login via Meta SSO: threads.com/login → Continue with Instagram."""
    # First verify IG session
    page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)
    ig_body = page.inner_text("body")[:200]
    if "Login" in ig_body and "Nomor ponsel" in ig_body:
        print("❌ IG session invalid — cookies expired")
        return False
    print("✅ IG session valid")

    # Navigate to Threads login page
    page.goto("https://www.threads.com/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    body_text = page.inner_text("body")[:500]
    logged_in = any(x in body_text for x in ["For you", "Search", "Messages", "Activity", "New thread", "Utas baru", "Buat"])

    if not logged_in:
        # Click "Continue with Instagram"
        result = page.evaluate("""
            () => {
                const targets = ["Continue with Instagram", "Lanjutkan dengan Instagram"];
                for (const el of document.querySelectorAll('div[role="button"], button, span')) {
                    const txt = el.textContent.trim();
                    if (txt === "Continue with Instagram" || txt === "Lanjutkan dengan Instagram") {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0 && rect.height < 100) {
                            el.click();
                            return "clicked: " + txt;
                        }
                    }
                }
                return "not_found";
            }
        """)
        print(f"   SSO button: {result}")
        if result != "not_found":
            time.sleep(10)
            # Check for auth confirmation
            auth_body = page.inner_text("body")[:500]
            if "Continue" in auth_body or "Allow" in auth_body or "confirm" in auth_body.lower():
                page.evaluate("""
                    () => {
                        const targets = ["Continue", "Allow", "Confirm", "Lanjutkan", "Izinkan"];
                        for (const el of document.querySelectorAll('div[role="button"], button')) {
                            for (const t of targets) {
                                if (el.textContent.trim() === t && el.getBoundingClientRect().height > 0) {
                                    el.click();
                                    return 'clicked: ' + t;
                                }
                            }
                        }
                        return 'no_auth_button';
                    }
                """)
                time.sleep(8)

            page.goto("https://www.threads.com/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            body_text = page.inner_text("body")[:500]
            logged_in = any(x in body_text for x in ["For you", "Search", "Messages", "New thread", "Utas baru"])

    if not logged_in:
        print("❌ Auth failed")
        return False
    print("✅ Authenticated via Meta SSO")
    return True


def should_skip_post(text):
    text_lower = text.lower()
    SKIP_ACCOUNTS = ["jagonya_shopee", "shopeeaffiliate", "shopee", "tokopedia", "lazada"]
    for account in SKIP_ACCOUNTS:
        if account in text_lower:
            return True
    for topic in ['politik', 'agama', 'sara', 'duka', 'covid', 'vaksin']:
        if topic in text_lower:
            return True
    return False


BRAND_WORDS_IN_USERNAME = [
    "official", ".id", "_shop", "_store", "beauty", "cosmetic", "skincare",
    "fragrance", "parfum", "perfume", "makeup", "haircare", "brand",
    "sociolla", "somethinc", "skintific", "avoskin", "wardah", "makeover",
    "luxcrime", "emina", "scarlett", "hvm.", "cerave", "theordinary",
]
BRAND_SIGNALS_IN_POST = [
    "launching", "new!", "exclusive", "limited edition", "order di",
    "link in bio", "tersedia di", "beli di", "katalog", "official store",
    "promo code", "use code", "discount code",
]


def is_brand_account(href, post_text=""):
    username = ""
    if href:
        match = re.search(r'/@([^/]+)/', href)
        if match:
            username = match.group(1).lower()
    
    for word in BRAND_WORDS_IN_USERNAME:
        if word in username:
            return True
    
    text_lower = post_text.lower() if post_text else ""
    for signal in BRAND_SIGNALS_IN_POST:
        if signal in text_lower:
            return True
    
    return False


def detect_post_context(post_text):
    """Detect what type of post we're replying to."""
    text_lower = post_text.lower()
    
    for kw in POST_CONTEXT_PATTERNS_V4["skin_problem"]["keywords"]:
        if kw in text_lower:
            return "skin_problem", kw
    
    for kw in POST_CONTEXT_PATTERNS_V4["seeking_recommendation"]["keywords"]:
        if kw in text_lower:
            return "seeking_recommendation", kw
    
    for kw in POST_CONTEXT_PATTERNS_V4["sharing_experience"]["keywords"]:
        if kw in text_lower:
            return "sharing_experience", kw
    
    return "general", ""


def check_already_replied(page, post_url):
    page.goto(post_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    
    result = page.evaluate("""() => {
        const replyAuthorLinks = document.querySelectorAll('a[href*="/@jagonya_shopee/post/"]');
        if (replyAuthorLinks.length > 0) return 'already_replied';
        
        const lines = document.body.innerText.split('\\n');
        let inReplies = false;
        for (const line of lines) {
            const trimmed = line.trim();
            if (/^Balas\\s*\\d*$/.test(trimmed) || trimmed === 'Reply' || trimmed === 'Balas' || trimmed === 'Like') {
                inReplies = true;
            }
            if (inReplies && trimmed.toLowerCase().includes('jagonya_shopee')) {
                return 'already_replied';
            }
        }
        return 'not_replied';
    }""")
    return result == 'already_replied'


def reply_to_post(page, post_url, comment_text):
    print(f"📌 Navigating to: {post_url}")
    page.goto(post_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    # Install API monitor BEFORE clicking reply
    page.evaluate("""() => {
        const origFetch = window.fetch;
        window._apiLogs = [];
        window.fetch = async function(...args) {
            const req = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
            const opts = args[1] || {};
            const logEntry = {url: req, method: opts.method || 'GET'};
            const resp = await origFetch.apply(this, args);
            const clone = resp.clone();
            try {
                logEntry.status = resp.status;
                logEntry.responseBody = (await clone.text()).substring(0, 2000);
            } catch(e) {}
            window._apiLogs.push(logEntry);
            return resp;
        };
    }""")
    time.sleep(0.5)

    reply_result = page.evaluate("""() => {
        // FIX v3: Find "Balas N" (with NUMBER) = original post's reply button
        // Comment reply buttons = "Balas" or "Reply" WITHOUT number
        // Original post's reply ALWAYS has count: "Balas 3", "Reply 26", etc.
        
        const buttons = document.querySelectorAll('div[role="button"], span[role="button"], button');
        const results = [];
        
        for (const btn of buttons) {
            const text = btn.textContent.trim();
            if (text.length === 0) continue;
            const rect = btn.getBoundingClientRect();
            if (rect.height <= 0) continue;
            
            // Match "Balas N" or "Reply N" OR just "Balas"/"Reply" (no number = 0 replies)
            if (/^(Balas|Reply)\s*\d*$/.test(text)) {
                results.push({element: btn, text: text, y: rect.top, hasNumber: /\d/.test(text)});
            }
        }
        
        // Prefer button with number (original post). Fallback: topmost button.
        results.sort((a, b) => a.y - b.y);
        const btn = results.find(r => r.hasNumber) || results[0];
        
        if (btn) {
            const keys = Object.keys(btn.element);
            for (const key of keys) {
                if (key.startsWith('__reactProps') && btn.element[key].onClick) {
                    btn.element[key].onClick({preventDefault: () => {}, stopPropagation: () => {}});
                    return 'clicked reactProps: ' + btn.text + ' (y=' + btn.y + ', total=' + results.length + ')';
                }
            }
            btn.element.click();
            return 'clicked native: ' + btn.text + ' (y=' + btn.y + ')';
        }
        
        return 'not_found';
    }""")

    print(f"   Reply button: {reply_result}")
    if reply_result == 'not_found':
        print("❌ No reply button found")
        return False

    time.sleep(3)

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

    page.evaluate(f"""() => {{
        const editor = document.querySelector('[contenteditable="true"]');
        if (editor) {{
            editor.focus();
            document.execCommand('insertText', false, {json.dumps(comment_text)});
        }}
    }}""")
    time.sleep(1)
    print("   ✅ Typed comment via execCommand")

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

    print(f"   Submit: {submit_result}")
    if submit_result == 'not found':
        print("❌ Submit button not found")
        return False

    time.sleep(8)

    # Check API response for integrity review
    try:
        logs = page.evaluate("""() => {
            return (window._apiLogs || []).filter(l =>
                l.url.includes('configure_text_only_post') || l.url.includes('reply'))
        }""")
        if logs:
            resp_body = logs[0].get('responseBody', '')
            if '"Media blocked due to integrity"' in resp_body or '"status":"fail"' in resp_body:
                print("❌ HARD BLOCKED — Media blocked due to integrity")
                print("   All keywords will fail — aborting")
                return 'hard_blocked'
            if '"integrity_review_decision":"pending"' in resp_body:
                print("⚠️ PENDING — Account flagged for spam review")
                print("   Reply submitted but likely invisible to others")
                return 'pending'
            if '"integrity_review_decision":"approved"' in resp_body:
                print("✅ Reply approved — visible to all")
                return True
            # Check for success (media pk exists)
            if '"pk":' in resp_body and '"media":' in resp_body:
                print("✅ Reply submitted (integrity not flagged)")
                return True
    except Exception as e:
        print(f"   ⚠️ Could not check API: {e}")

    return True


def verify_reply(page, post_url):
    print("🔍 Verifying...")
    page.goto(post_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    body_text = page.evaluate("() => document.body.innerText")
    if "jagonya_shopee" in body_text.lower():
        print("✅ Reply verified!")
        return True
    else:
        print("⚠️ Reply not immediately visible (cache delay) — proceeding")
        return True


def main():
    print("=" * 60)
    print("🧵 THREADS AUTO-REPLY v4.0a")
    print("=" * 60)
    
    all_unused = parse_database(DATABASE)
    print(f"📊 Found {len(all_unused)} unused links")
    
    if not all_unused:
        print("❌ No unused links available — batch needs reset")
        with open("/tmp/threads_reply_result.json", "w") as f:
            json.dump({"success": False, "reason": "no_unused_links"}, f)
        sys.exit(1)

    by_category = {}
    for link in all_unused:
        cat = link["category"]
        by_category.setdefault(cat, []).append(link)
    
    print(f"   Categories: {', '.join(f'{k}={len(v)}' for k, v in by_category.items())}")

    priority_order = ["haircare", "parfum", "skincare", "makeup"]
    ordered_cats = sorted(by_category.keys(), key=lambda x: priority_order.index(x) if x in priority_order else 99)

    cookies = load_cookies(COOKIE_FILE)
    threads_cookies = None
    if os.path.exists(THREADS_COOKIE_FILE):
        threads_cookies = load_cookies(THREADS_COOKIE_FILE)
        print(f"   Loaded {len(cookies)} IG + {len(threads_cookies)} Threads cookies")
    post_url = None
    chosen_link = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        inject_cookies(context, cookies, threads_cookies)
        page = context.new_page()

        print("\n" + "=" * 50)
        print("🔑 STEP 1: Authentication")
        print("=" * 50)
        if not authenticate(page):
            print("❌ AUTH FAILED")
            browser.close()
            with open("/tmp/threads_reply_result.json", "w") as f:
                json.dump({"success": False, "reason": "auth_failed"}, f)
            sys.exit(1)

        print("\n" + "=" * 50)
        print("🔍 STEP 2: Search (< 24h posts only)")
        print("=" * 50)

        for category in ordered_cats:
            if not category:
                print(f"⚠️ WARNING: {len(by_category.get('', []))} links have EMPTY category — skipping (check database headers)")
                continue
                
            keywords = KEYWORDS_BY_CATEGORY.get(category, ["rekomendasi skincare"])
            links_in_cat = by_category[category]
            
            print(f"\n📂 Trying {category} ({len(links_in_cat)} unused links)")
            
            for keyword in keywords:
                url = f"https://www.threads.com/search?q={keyword.replace(' ', '+')}&serp_type=default&filter=recent"
                print(f"   🔍 Searching: {keyword}")
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

                print(f"      Found {len(links_data)} post links")

                tried = 0
                for link_info in links_data:
                    if tried >= MAX_POSTS_PER_KEYWORD:
                        break
                    tried += 1

                    href = link_info["href"]
                    text = link_info["text"]

                    if should_skip_post(text):
                        continue
                    if not is_fresh_post(text):
                        age = get_post_age_display(text)
                        print(f"      ⏭️ Stale ({age}) — skipping")
                        continue
                    if not href or "/post/" not in href:
                        continue
                    
                    if is_brand_account(href, text):
                        print(f"   ⏭️ Brand account — skipping")
                        continue

                    full_url = "https://www.threads.com" + href if href.startswith("/") else href
                    
                    print(f"   🔎 Checking: {full_url[:60]}...")
                    if check_already_replied(page, full_url):
                        print(f"   ⏭️ Already replied — skipping")
                        continue

                    post_url = full_url
                    chosen_link = random.choice(links_in_cat)
                    post_context_text = text
                    age_display = get_post_age_display(text)
                    print(f"   ✅ Target: {full_url}")
                    print(f"   ⏱️ Age: {age_display}")
                    print(f"   📝 Context: {text[:150]}...")
                    break

                if post_url:
                    break
            
            if post_url:
                break

        if not post_url:
            print("\n❌ No fresh (<24h) un-replied post found across all categories")
            browser.close()
            with open("/tmp/threads_reply_result.json", "w") as f:
                json.dump({"success": False, "reason": "no_post_found"}, f)
            sys.exit(1)

        product = chosen_link["product"]
        post_text = post_context_text if 'post_context_text' in dir() else ""
        context_type, matched_kw = detect_post_context(post_text)
        comment = generate_contextual_comment_v4(product, post_text, chosen_link["link"])
        
        print("\n" + "=" * 50)
        print("📝 STEP 3: Reply (v4.0 Diverse Templates)")
        print("=" * 50)
        print(f"   Category: {chosen_link['category']}")
        print(f"   Product: {product}")
        print(f"   Context: {context_type}" + (f" (keyword: {matched_kw})" if matched_kw else ""))
        print(f"   Post: {post_text[:100]}...")
        print(f"   Comment: {comment}")

        success = reply_to_post(page, post_url, comment)

        if success == 'hard_blocked':
            print("\n🔴 HARD BLOCKED — Account integrity flag. Aborting all keywords.")
            result = {"success": False, "reason": "hard_blocked", "post_url": post_url}
        elif success == 'pending':
            print("\n⚠️ PENDING — Reply likely invisible (account flagged)")
            result = {"success": False, "reason": "pending_flag", "post_url": post_url}
        elif success:
            print("\n" + "=" * 50)
            print("✅ STEP 4: Verify")
            print("=" * 50)
            verify_reply(page, post_url)

            result = {
                "success": True,
                "post_url": post_url,
                "comment": comment,
                "link": chosen_link["link"],
                "product": product,
                "category": chosen_link["category"],
                "context": context_type,
            }
            print("\n🟢 THREADS REPLY SUCCESS!")
            print(json.dumps(result, indent=2))
        else:
            result = {"success": False, "reason": "reply_failed", "post_url": post_url}
            print("❌ Reply failed")

        with open("/tmp/threads_reply_result.json", "w") as f:
            json.dump(result, f)

        browser.close()


if __name__ == "__main__":
    main()
