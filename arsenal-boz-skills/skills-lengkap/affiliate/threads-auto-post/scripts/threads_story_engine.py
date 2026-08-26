#!/usr/bin/env python3
"""Threads Story Engine v1 — jual cerita 3-beat (soft sell).

POST1: scene + konflik (NO product / NO CTA / NO link)
POST2: twist / insight (masih cerita; product opsional soft)
POST3: resolusi + soft CTA + save + affiliate link
"""
from __future__ import annotations

import random
import re
from typing import Any

STORY_TYPES = [
    "keresahan_malam",
    "malu_sosial",
    "salah_beli",
    "teman_bukti",
    "open_loop",
    "regret",
]

# Beat templates per story_type × category
# Placeholders: {product} optional in beat2 only
STORIES: dict[str, dict[str, list[dict[str, list[str]]]]] = {
    "keresahan_malam": {
        "skincare": [
            {
                "p1": [
                    "tadi malem ngaca, tiba2 ngerasa muka gw “lelah banget” padahal baru cuci muka 2x",
                    "jam 1 malem, lampu kamar redup, muka keliatan kusam gitu… bikin overthinking",
                    "abis mandi malem, ngaca sebentar. kok pori-pori keliatan lebih bandel ya",
                ],
                "p2": [
                    "ternyata bukan males rawat diri. gw cuma salah urutan + pake yang bikin makin ketarik",
                    "bukan kurang air. lebih ke step malam yang kebalik + formula yang ga cocok sama tipe kulit gw",
                    "setelah ganti 1 step malam yang lebih gentle, seminggu keliatan beda di foto deket",
                ],
            },
            {
                "p1": [
                    "tiap malem bilang “besok mulai skincare beneran”… tapi pagi tetep gitu-gitu aja",
                    "mirror selfie malem selalu bikin gw ngerasa “kok gini terus sih”",
                ],
                "p2": [
                    "pas dipaksa konsisten 21 hari, baru sadar yang bikin beda itu simple routine, bukan 10 produk",
                    "yang ngerubah bukan “mahal”, tapi konsisten + formula yang ga bikin kulit panik",
                ],
            },
        ],
        "parfum": [
            {
                "p1": [
                    "malem-malem nyium baju yang dipake seharian… baunya udah ilang dari siang",
                    "pulang kerja, jaket masih wangi dikit. 1 jam kemudian? udah netral lagi",
                ],
                "p2": [
                    "ternyata masalahnya bukan cuma parfumnya. cara semprot + titik nadi yang bikin nahan",
                    "abis ganti ke yang dry down-nya lebih nempel, baru kerasa “oh ini yang dicium orang”",
                ],
            }
        ],
        "haircare": [
            {
                "p1": [
                    "malem beres-beres bantal, ada helai rambut lagi. kecil sih, tapi bikin panik pelan-pelan",
                    "habis keramas malem, rambut keliatan oke. pagi-paginya? lepek + rontok di sisir",
                ],
                "p2": [
                    "bukan shampo “viral” yang kurang. lebih ke formula yang ga cocok + overwash",
                    "pas ganti yang lebih gentle di scalp, rontok di bantal berkurang seminggu",
                ],
            }
        ],
        "makeup": [
            {
                "p1": [
                    "malem pulang acara, cek mirror mobil: makeup udah geser di T-zone",
                    "foto malem keliatan oke. foto siang? bedanya jauh banget",
                ],
                "p2": [
                    "ternyata bukan “kurang bedak”. urutan + 1 produk yang bikin nahan seharian",
                    "abis rapihin base-nya, makeup ga gampang dempul di jam 4 sore",
                ],
            }
        ],
    },
    "malu_sosial": {
        "skincare": [
            {
                "p1": [
                    "ada yang bilang “lo keliatan capek banget”. padahal tidur cukup",
                    "ketemu temen lama, dia nanya “lo ga apa-apa?” sambil liat muka gw",
                ],
                "p2": [
                    "malunya diem. abis itu gw benahi routine malam biar ga keliatan “lelah permanen”",
                    "bukan makeup. yang bikin beda justru skincare yang bikin tekstur lebih rapi",
                ],
            }
        ],
        "parfum": [
            {
                "p1": [
                    "ditanya “pake parfum apa?”… gw diem. soalnya yang dipake udah 3 tahun, baunya ilang sejam",
                    "masuk lift bareng orang, gw ngerasa baunya netral. insecure pelan-pelan",
                ],
                "p2": [
                    "abis ganti cara semprot (titik nadi, jangan diusap) baru kerasa bedanya",
                    "pas nemu yang dry down-nya nempel, orang mulai nanya sendiri tanpa gw promo",
                ],
            }
        ],
        "haircare": [
            {
                "p1": [
                    "ada yang nyentuh rambut gw, “kok kering banget?”. gw cuma ketawa kaku",
                    "foto bareng, rambut gw keliatan lepek dibanding yang lain",
                ],
                "p2": [
                    "bukan styling doang. scalp care yang bikin rambut ga gampang “mati” di siang",
                    "abis ganti haircare yang cocok, pujian dateng sendiri. aneh tapi bener",
                ],
            }
        ],
        "makeup": [
            {
                "p1": [
                    "di foto bareng, muka gw keliatan cakey. yang lain natural",
                    "ada yang bilang “makeup-an ya?” dengan tone yang ga enak",
                ],
                "p2": [
                    "pas ganti base yang lebih tipis, makeup keliatan kayak kulit, bukan dempul",
                    "yang bikin pede: shade + tekstur yang ga ketara makeup",
                ],
            }
        ],
    },
    "salah_beli": {
        "skincare": [
            {
                "p1": [
                    "4x ganti skincare “viral”… hasilnya gitu-gitu aja, malah breakout sesekali",
                    "keranjang kuning isinya trial error. dompet tipis, kulit tetep gitu",
                ],
                "p2": [
                    "barusan sadar: bukan mereknya doang, tapi tipe kulit gw ga cocok sama formula “semua orang”",
                    "pas stop ikut hype dan pilih yang gentle, baru kerasa progress pelan-pelan",
                ],
            }
        ],
        "parfum": [
            {
                "p1": [
                    "3 botol parfum murah, semuanya ilang sejam. dompet gw yang wangi",
                    "kejar yang “mirip branded”, abis 2 jam baunya aneh",
                ],
                "p2": [
                    "akhirnya nyari yang performancenya jujur, bukan yang cuma enak di toko",
                    "yang bikin worth: nahan + ga nyengat. bukan cuma first spray doang",
                ],
            }
        ],
        "haircare": [
            {
                "p1": [
                    "4x beli haircare viral… rambut malah lepek + rontok nambah",
                    "tiap liat review bintang 5, gw gas. hasil di kepala? beda cerita",
                ],
                "p2": [
                    "bukan “semua orang cocok”. tipe rambut + frekuensi keramas yang nentuin",
                    "pas cocok formula-nya, rontok di sisir berkurang tanpa drama",
                ],
            }
        ],
        "makeup": [
            {
                "p1": [
                    "beli foundation 3 shade beda… semuanya “hampir cocok” tapi ga pas",
                    "lip tint bagus di foto review, di bibir gw transfer ke mana-mana",
                ],
                "p2": [
                    "akhirnya mikir: texture > hype. yang ringan dan nahan lebih worth",
                    "pas nemu yang blend natural, makeup ga keliatan usaha berlebih",
                ],
            }
        ],
    },
    "teman_bukti": {
        "skincare": [
            {
                "p1": [
                    "temen gw tiba2 kulitnya keliatan “mahal”. gw kira treatment klinik",
                    "ada temen yang muka-nya glowing natural. gw nanya skincare-nya sambil pura-pura santai",
                ],
                "p2": [
                    "taunya cuma ganti 1 step malam + konsisten 21 hari. gw nyoba, baru ngerti bedanya",
                    "bukan 10 produk. yang dia pake simpel banget, tapi rutin",
                ],
            }
        ],
        "parfum": [
            {
                "p1": [
                    "temen kantor wangi-nya nempel seharian. padahal naik motor bareng",
                    "ada yang baunya “bersih mahal” tanpa nyengat. gw iri pelan-pelan",
                ],
                "p2": [
                    "dia kasih tau trik semprot + 1 parfum yang dry down-nya beneran nahan",
                    "abis dicoba, orang nanya ke gw juga. aneh rasanya jadi yang ditanya",
                ],
            }
        ],
        "haircare": [
            {
                "p1": [
                    "rambut temen gw keliatan tebel padahal dulu rontok. gw kira vitamin mahal",
                    "ada yang scalp-nya keliatan sehat banget di foto deket",
                ],
                "p2": [
                    "taunya ganti haircare + ga keramas berlebihan. simple, tapi ngena",
                    "gw ikut, 2 minggu baru kerasa di sisir & bantal",
                ],
            }
        ],
        "makeup": [
            {
                "p1": [
                    "temen makeup-an natural, padahal seharian di luar. base-nya tetep rapi",
                    "ada yang lip-nya awet makan minum. gw penasaran banget",
                ],
                "p2": [
                    "dia bilang kuncinya 1 produk yang bener, bukan numpuk layer",
                    "abis nyoba approach yang sama, makeup ga gampang “hancur” di jam 4",
                ],
            }
        ],
    },
    "open_loop": {
        "skincare": [
            {
                "p1": [
                    "ada 1 kebiasaan kecil yang bikin muka gw ga gampang “lelah” di foto… padahal dulu kusam gampang",
                    "gw nemu 1 step malam yang bikin beda di minggu kedua. kelihatannya sepele",
                ],
                "p2": [
                    "bukan treatment mahal. lebih ke konsistensi + formula yang ga bikin kulit panik",
                    "triiknya bukan numpuk produk. 1-2 step yang pas lebih ngena",
                ],
            }
        ],
        "parfum": [
            {
                "p1": [
                    "ada 1 kebiasaan kecil yang bikin parfum gw “nanya orang”… padahal dulu ilang sejam",
                    "gw nemu trik semprot yang bikin wangi ga gampang mati di siang",
                ],
                "p2": [
                    "bukan semprot 10x. titik nadi + jangan diusap. plus pilih yang dry down-nya jujur",
                    "setelah itu, first impression beda tanpa keliatan berusaha",
                ],
            }
        ],
        "haircare": [
            {
                "p1": [
                    "ada 1 kebiasaan kecil yang bikin rambut gw ga gampang lepek… padahal dulu tiap siang down",
                    "gw nemu pola keramas yang bikin rontok di bantal berkurang",
                ],
                "p2": [
                    "bukan vitamin mahal dulu. mulai dari formula yang cocok + frekuensi yang bener",
                    "hasilnya pelan, tapi keliatan di sisir tiap pagi",
                ],
            }
        ],
        "makeup": [
            {
                "p1": [
                    "ada 1 kebiasaan kecil yang bikin makeup gw awet seharian… padahal dulu luntur 2 jam",
                    "gw nemu urutan base yang bikin ga gampang cakey di cuaca panas",
                ],
                "p2": [
                    "triiknya bukan bedak numpuk. lebih ke base tipis + 1 produk yang nahan",
                    "abis itu touch-up jarang banget, padahal seharian di luar",
                ],
            }
        ],
    },
    "regret": {
        "skincare": [
            {
                "p1": [
                    "nyesel baru serius soal ini sekarang. padahal masalahnya udah 2 tahunan",
                    "kalo tau solusinya se-simple ini, dompet trial error gw ga bolong",
                ],
                "p2": [
                    "dulu mikir “ya udah, biasa aja”. ternyata fix-nya di routine yang bener, bukan numpuk produk",
                    "progress-nya ga instan, tapi lebih jujur daripada janji 3 hari glowing",
                ],
            }
        ],
        "parfum": [
            {
                "p1": [
                    "nyesel baru tau cara semprot yang bener. padahal udah buang duit ke botol yang ilang sejam",
                    "kalo dari dulu pilih yang performance-nya jujur, ga perlu gonta-ganti tiap bulan",
                ],
                "p2": [
                    "bukan soal mahal. yang nahan + ga nyengat lebih worth buat daily",
                    "sekarang pagi semprot, siang masih ada. bedanya kerasa di confidence",
                ],
            }
        ],
        "haircare": [
            {
                "p1": [
                    "nyesel baru stop overwash. padahal rontok di bantal udah jadi “normal”",
                    "kalo dari dulu pilih formula yang cocok, ga perlu panik tiap liat sisir",
                ],
                "p2": [
                    "perubahannya pelan. tapi seminggu-dua keliatan di helai yang ga gampang putus",
                    "bukan magic. lebih ke stop yang ngerusak + pilih yang gentle",
                ],
            }
        ],
        "makeup": [
            {
                "p1": [
                    "nyesel baru nemu base yang tipis. padahal dulu makeup-an selalu keliatan usaha",
                    "kalo dari dulu tau shade + texture yang pas, ga perlu buang duit ke yang cakey",
                ],
                "p2": [
                    "yang bikin beda: keliatan natural tapi tetep rapi seharian",
                    "bukan numpuk layer. 1 produk yang bener lebih ngena",
                ],
            }
        ],
    },
}

SOFT_CTAS = [
    "yang mau coba, link ada di bawah 🫶",
    "yang penasaran, gw taro link-nya 👇",
    "save dulu aja, nanti kalo butuh tinggal klik 📌",
    "buat yang mau coba, cek di bawah ya 🤍",
    "biar ga ilang, save. linknya di bawah 🫶",
    "yang lagi nyari yang nyambung, link di bawah 👇",
]

SAVE_LINES = [
    "Save biar ga ilang 🫶",
    "Bookmark dulu sebelum lupa 📌",
    "Save buat nanti 🤍",
    "Jangan lupa save ya",
    "Simpan dulu, coba nanti 💾",
]

# Soft product mentions for beat2 (optional, not always used)
SOFT_PRODUCT_BRIDGES = [
    "btw yang bantu gw belakangan: {product}",
    "yang akhirnya nyambung di case gw: {product}",
    "salah satu yang bikin beda: {product}",
    "yang gw stick-an sekarang: {product}",
]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _overlap_ratio(a: str, b: str) -> float:
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / max(len(wa), len(wb))


def pick_story_type(history: list[dict], n: int = 4) -> str:
    recent = [p.get("story_type") or p.get("hook_category") or "" for p in history[-n:]]
    recent = [r for r in recent if r]
    fresh = [t for t in STORY_TYPES if t not in recent]
    return random.choice(fresh or STORY_TYPES)


def build_story_posts(
    *,
    category: str,
    product: str,
    link: str,
    history: list[dict] | None = None,
    force_story_type: str | None = None,
) -> dict[str, Any]:
    """Return content dict for threads_post_v6 + metadata."""
    history = history or []
    category = category if category in ("skincare", "parfum", "haircare", "makeup") else "skincare"
    product_short = product[:40].strip() if len(product) > 40 else product

    story_type = force_story_type or pick_story_type(history)
    # fallback category packs
    packs = STORIES.get(story_type, {}).get(category) or STORIES.get(story_type, {}).get("skincare") or []
    if not packs:
        # ultimate fallback
        packs = STORIES["regret"]["skincare"]

    used_hooks = [p.get("hook_text", "") for p in history[-12:]]
    random.shuffle(packs)

    chosen = None
    post1 = post2 = ""
    for pack in packs:
        p1_opts = list(pack["p1"])
        p2_opts = list(pack["p2"])
        random.shuffle(p1_opts)
        random.shuffle(p2_opts)
        for a in p1_opts:
            if any(_overlap_ratio(a, h) > 0.55 for h in used_hooks if h):
                continue
            for b in p2_opts:
                # avoid near-duplicate of post1
                if _overlap_ratio(a, b) > 0.45:
                    continue
                chosen = pack
                post1, post2 = a, b
                break
            if chosen:
                break
        if chosen:
            break

    if not chosen:
        pack = packs[0]
        post1 = random.choice(pack["p1"])
        post2 = random.choice(pack["p2"])

    # ~40% soft product bridge at end of beat2 (never brand dump)
    if random.random() < 0.40 and product_short:
        bridge = random.choice(SOFT_PRODUCT_BRIDGES).format(product=product_short)
        # keep short
        if len(post2) < 140:
            post2 = f"{post2}. {bridge}"

    # Safety: strip any accidental URL from p1/p2
    post1 = re.sub(r"https?://\S+", "", post1).strip()
    post2 = re.sub(r"https?://\S+", "", post2).strip()

    cta = random.choice(SOFT_CTAS)
    save = random.choice(SAVE_LINES)
    post3 = f"{cta}\n{save}\n{link}"

    return {
        "post_1": post1,
        "post_2": post2,
        "post_3": post3,
        "affiliate_link": link,
        "product_name": product,
        "hook_category": story_type,  # keep field name for history/dedup compat
        "story_type": story_type,
        "category": category,
        "hook_text": post1[:80],
        "content_mode": "story_v1",
    }


def build_story_reply_prompt(op_text: str, product: str, url: str) -> tuple[str, str]:
    """System + user prompt for story-mode soft reply (not hard sell)."""
    clean_product = re.sub(r"\d+\s*(g|gr|ml|g\b).*", "", product, flags=re.I).strip()[:40]
    op_snippet = (op_text or "")[:220]
    system = (
        "Lo gen-z Indo di Threads. Reply kayak temen curhat, BUKAN seller.\n"
        "Rules keras:\n"
        "- 8-18 kata, 1 baris\n"
        "- Mulai empati / lanjut cerita / nanya balik\n"
        "- JANGAN hard sell, JANGAN 'rekomendasi terbaik', JANGAN 'cek sekarang'\n"
        "- Boleh soft sebut produk SEKALI secara natural ATAU skip produk kalau ga nyambung\n"
        "- Akhir: taruh URL plain sekali\n"
        "- Bahasa chat: gak, bgt, aja, tp oke\n"
        "- No markdown, no bullet, no hashtag spam"
    )
    user = (
        f'Post OP: "{op_snippet}"\n'
        f"Produk (opsional soft): {clean_product}\n"
        f"URL: {url}\n\n"
        "Tulis 1 reply story-mode: empati dulu, baru soft pointer. End with url."
    )
    return system, user


def story_reply_fallback(product: str, url: str) -> str:
    clean = re.sub(r"\d+\s*(g|gr|ml|g\b).*", "", product, flags=re.I).strip()[:36]
    templates = [
        f"ih iya bgt, gw juga gitu… belakangan nemu {clean} yang nyambung {url}",
        f"real, dulu gw juga nyerah. skrg lebih tenang abis nyoba {clean} {url}",
        f"relate banget. gw save dulu biar ga ilang, ini yang bantu gw {url}",
        f"sama, overthinking mulu. yang bikin beda di case gw: {clean} {url}",
        f"gw juga pernah, terus pelan2 rapihin. kalo penasaran {url}",
        f"ceritanya mirip. soft aja ya, ini yang gw stick-an {url}",
    ]
    return random.choice(templates)


if __name__ == "__main__":
    # self-check
    hist = []
    for cat in ("skincare", "parfum", "haircare", "makeup"):
        c = build_story_posts(
            category=cat,
            product=f"Sample {cat.title()} Product 100ml",
            link="https://s.shopee.co.id/TESTLINK",
            history=hist,
        )
        assert "s.shopee.co.id" in c["post_3"]
        assert "http" not in c["post_1"]
        assert c["story_type"] in STORY_TYPES
        hist.append(c)
        print(cat, c["story_type"], "→", c["post_1"][:60])
    print("story_engine_ok")
