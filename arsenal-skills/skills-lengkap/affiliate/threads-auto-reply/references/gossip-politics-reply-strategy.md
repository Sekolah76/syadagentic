# Gossip & Politics Reply Strategy (Reply 3) — Updated 2026-06-05

## 🚨 CONTENT-TYPE-SPECIFIC HARD BLOCK (Verified 2026-06-05)
**Reply 3 keywords (korupsi, politik, gosip) trigger hard block even when Reply 1-2 (affiliate) succeed in the SAME RUN.** On 2026-06-05: Reply 1 "rekomendasi skincare" ✅ visible, Reply 2 "sunscreen terbaik" ✅ visible, Reply 3 "korupsi" ❌ hard blocked (first attempt). This is NOT an account-wide issue — Threads applies stricter content moderation to political/gossip comments with affiliate links.

**Risk mitigation:**
- During fragile recovery (first 7-14 days post-flag): SKIP Reply 3 entirely
- Only enable Reply 3 after 3+ consecutive successful affiliate-only runs
- When enabled, prefer gossip/celebrity over political topics (lower risk)
- If Reply 3 hits hard block → immediately disable for 3+ days

## Overview
Reply 3 is dedicated to nimbrung di trending Indonesian topics (gosip seleb, isu sosial, politik) dengan natural affiliate link insertion. Tujuan: diversifikasi engagement + tetap promote produk. **⚠️ HIGH RISK — see content-type-specific hard block warning above.**

## ⚠️ Fresh News Requirement (CRITICAL)

**Reply 3 MUST fetch fresh/trending news FIRST before searching Threads.**

### Step 1: Fetch from Google News RSS
```bash
# Celebrity gossip
curl -s "https://news.google.com/rss/search?q=gosip+seleb+indonesia&hl=id&gl=ID&ceid=ID:id" | grep -o "<title>[^<]*</title>" | head -10

# Politics/social issues
curl -s "https://news.google.com/rss/search?q=politik+indonesia+korupsi&hl=id&gl=ID&ceid=ID:id" | grep -o "<title>[^<]*</title>" | head -10

# Specific person (e.g., Sarwendah, Dadan BGN)
curl -s "https://news.google.com/rss/search?q=sarwendah&hl=id&gl=ID&ceid=ID:id" | grep -o "<title>[^<]*</title>" | head -10
```

### Step 2: Pick MOST VIRAL topic
- Choose topic from last 24 hours
- Prefer high engagement (political scandals, celebrity drama)

### Step 3: Search Threads
- Search for the specific topic on Threads
- Find posts with high engagement (likes, replies)
- Craft natural netizen reply

## Target Topics

### 1. Gosip Seleb
- Artis cerai (Raisa, Sherina, Deddy Corbuzier, dll)
- Outfit/makeup seleb viral
- Drama artis (perselingkuhan, konflik)
- Skincare routine seleb

### 2. Isu Sosial
- Korupsi (dana gizi, bansos, dll)
- Harga kebutuhan naik
- Kesehatan masyarakat
- Pendidikan

### 3. Politik Indonesia
- Kebijakan pemerintah
- Pilkada/Pemilu
- Debat politik (non-SARA)
- Figur politik

## Angle Mapping (Issue → Product)

| Issue | Product Angle | Example |
|-------|---------------|---------|
| Korupsi dana gizi | Suplemen makanan | "yang mau kasih makan bergizi buat keluarga, cek ini" |
| Harga naik | Produk murah/alternatif | "buat yang cari alternatif murah, ini worth it" |
| Artis cerai | Self-care products | "yang lagi healing, coba self-care pake ini" |
| Fashion seleb | Outfit/dupes murah | "outfit mirip [seleb] ada di Shopee nih" |
| Skincare seleb | Skincare dupes | "skincare buat glowing kayak [seleb]" |
| Kesehatan | Vitamin/suplemen | "buat jaga kesehatan, coba ini" |
| Kepala BGN ditangkap | Alat masak/suplemen | "anak-anak makan bergizi malah dikorupsi... semoga dihukum berat. Btw yang mau kasih makan bergizi buat keluarga, cek ini" |
| IHSG anjlok/krisis ekonomi | Produk budget-friendly | "ekonomi lagi susah, mending cari yang affordable aja" |

## Reply Templates

### Template 1: Gosip Seleb (Emotional + Product)
```
Ya ampun [seleb] emang gak pernah miss ya, dari dulu style-nya always on point 🥺 
btw yang nyari [produk] buat [benefit] kayak dia, cek ini deh [link]
```

### Template 2: Isu Sosial (Frustrated + Solution)
```
[Isu] emang bikin emosi ya 😤 semoga [harapan]. 
Btw yang mau [action related ke produk], cek ini deh [link]
```

### Template 3: Politik (Opinion + Natural Transition)
```
[Opini netizen soal kebijakan] 🙏 
btw [transition natural ke produk] [link]
```

### Template 4: Gosip Seleb Tanpa Link (Kalau Gak Ada Celah)
```
Anjirr [seleb] makin kece aja, emang udah dari sononya kali ya cantiknya 😭
```
(Tanpa link - tapi ini jarang, usahakan selalu ada link)

## Search Keywords for Reply 3

### Gosip
- `gosip seleb`
- `artis cerai`
- `drama artis`
- `outfit seleb`
- `skincare seleb`

### Isu Sosial
- `korupsi`
- `isu viral`
- `berita viral`
- `kasus korupsi`

### Politik
- `politik indonesia`
- `kebijakan pemerintah`
- `pilkada`
- `pemilu`

## Crafting Rules

1. **Netizen persona:** Bukan sales, tapi warga biasa yang nimbrung
2. **Emotional first:** Komentar dulu soal isu → baru transisi ke link
3. **Natural transition:** "Btw", "Ngomong-ngomong", "Sambil"
4. **Always include link:** Bahkan untuk politik, cari angle yang loosely related
5. **Gen Z language:** bgt, gw, auto, gila si, emang, no cap

## Safety Rules

- ❌ NO SARA (Suku, Agama, Ras, Antargolongan)
- ❌ NO extremism
- ❌ NO hate speech
- ❌ NO provokasi
- ✅ Opini netizen biasa
- ✅ Komentar konstruktif
- ✅ Harapan positif

## Example Replies (Based on Real News — 2026-06-04)

### Gosip: Artis Cerai 2025
**Post:** "13 Artis yang Cerai Sepanjang 2025, dari Sherina sampai Deddy Corbuzier"

**Reply:**
> "Ya ampun sedih banget liat list ini 😭 tapi emang ya kecantikan itu gak menjamin hubungan, yang penting tetep sayang diri sendiri. Btw yang lagi healing, coba self-care pake ini deh biar glowing dari dalam [link skincare]"

### Isu Politik: Eks Kepala BGN Ditangkap
**Post:** "BREAKING NEWS: Eks Kepala BGN Dadan Hindayana Jadi Tersangka Kasus Korupsi MBG"

**Reply:**
> "Anak-anak makan bergizi gratis malah dikorupsi... serendah itu ya 😤 semoga dihukum seberat-beratnya. Btw yang mau kasih makan bergizi buat keluarga sendiri, cek ini deh [link alat masak/suplemen]"

### Isu Ekonomi: IHSG Anjlok / Krisis Moneter
**Post:** "Dengan kondisi ekonomi seperti ini, ditambah IHSG anjlok ke harga 2019, yang dikhawatirkan adalah akan terjadi kembali krismon..."

**Reply:**
> "Gw juga ngeri sih liat ekonomi sekarang 😭 tapi emang harus lebih bijak ngatur keuangan. Btw buat yang cari alternatif murah buat kebutuhan sehari-hari, cek ini deh [link produk budget]"

### Gosip: Sarwendah Outfit Viral
**Post:** (search "Sarwendah" di Threads, cari outfit/style post)

**Reply:**
> "Ya ampun Sarwendah emang gak pernah miss ya style-nya 🥺 btw yang nyari outfit mirip dia, cek ini deh [link fashion]"

## Success Metrics
- Reply terlihat (verified via reload)
- Engagement: likes/replies on comment
- Link clicks (track via Shopee analytics)
- Account safety: no flagging/suspension
