# Comment Template System v6.0 — CONVERSION OPTIMIZED

**Updated:** 2026-06-03 based on 30-day Shopee Affiliate data (389 clicks, 4.37% CR, Rp 124.6K)

---

## Architecture

Script: `scripts/threads_reply_db_reader.py`

### Template Selection Flow
```
1. Parse post text → detect_post_context(post_text) → (context_type, keyword)
2. Pick context-aware templates from POST_CONTEXT_PATTERNS[context_type]["templates"]
3. Fill placeholders: {product}, {keyword}, {link}
4. Add conversion trigger: price anchor OR social proof OR specific result
5. Output: contextual comment matching post content WITH conversion psychology
```

### Post Context Detection (Priority Order)
1. **skin_problem** — "jerawat", "rontok", "berminyak", "bruntusan", "kusam", "kering", "kemerahan", "beruntusan", "kulit gelap", "mata panda"
2. **seeking_recommendation** — "rekomendasi", "ada yang tau", "bagus ga", "suggest", "mana nih", "kasih tau dong", "yang bagus", "minta rekomendasi"
3. **sharing_experience** — "gw pake", "review", "holy grail", "hasilnya", "teksturnya", "wanginya", "coverage-nya"
4. **comparing_products** — "lebih bagus mana", "vs", "dibanding", "bedanya", "prefer mana", "tim mana"
5. **price_conscious** — "murah", "affordable", "budget", "hemat", "kantong", "mahal", "diskon"
6. **general** — fallback

---

## 🔥 CONTEXT-AWARE TEMPLATES (v6.0 — 15 Patterns)

### Pattern 1: Relatability → Solution
```python
"skin_problem": [
    "gw juga dulu {keyword} parah, nyoba {product} ini emang beda sih 🤌 {link}",
    "sama banget 😭 {product} ini yang gw pake buat {keyword} dan hasilnya [specific] 🥹 {link}",
    "yang {keyword} coba deh {product} ini, gw udah [X] minggu pake dan ngefek bgt 🔥 {link}",
    "gw juga pernah {keyword}, {product} ini yang pertama kali works buat gw 💀 {link}",
    "ini buat {keyword} emang the best sih, gw udah repurchase [X] kali {product} 🤌 {link}",
],
```

### Pattern 2: Recommendation Delivery
```python
"seeking_recommendation": [
    "sini gw rekomendasiin {product}, gw udah pake [X] dan emang bagus bgt 🤌 {link}",
    "{product} ini jawabannya, [X] sold di shopee dan reviewnya bagus2 semua 🔥 {link}",
    "coba deh {product} ini, gw juga pake dan hasilnya [specific result] 🥹 {link}",
    "{product}! gw udah [X] kali beli, ganti skincare gak pernah. holy grail 💅 {link}",
    "yang lagi nyari {keyword}, {product} ini yang gw pake dan no cap worth it 🔥 {link}",
],
```

### Pattern 3: Affirmation + Upgrade
```python
"sharing_experience": [
    "sama! gw juga pake {product} ini, emang best sih. repurchase terus 😭 {link}",
    "ini emang holy grail bgt, gw juga udah [X] kali beli {product} 💅 {link}",
    "betul bgt! gw juga pake {product}, hasilnya [specific detail]. gak ada duanya 🤌 {link}",
    "sama bestie 🥹 gw juga pake {product} dan [specific benefit]. worth it bgt 🔥 {link}",
    "gw juga team {product}! emang yang paling works sih ini 💀 {link}",
],
```

### Pattern 4: Comparison (NEW — Price Anchor)
```python
"comparing_products": [
    "gw udah coba dua2nya. {product} ini lebih worth it sih, harga [range] tapi hasilnya 🤌 {link}",
    "{product} menang menurut gw. lebih [benefit] dan harganya [range]. no cap 🔥 {link}",
    "dulu gw team [alternative], sekarang pindah ke {product} dan gak bakal balik 💀 {link}",
    "kalau soal [criteria], {product} ini emang juara. gw udah buktiin sendiri 🥹 {link}",
],
```

### Pattern 5: Budget Friendly (NEW — Value Focus)
```python
"price_conscious": [
    "murah meriah tapi hasilnya gila, {product} ini. under 50rb lagi 🤌 {link}",
    "yang nyari {keyword} budget friendly, {product} ini jawabannya. gw udah 3x beli 🔥 {link}",
    "harga kaki lima kualitas mall emang {product} ini. gak bakal nyesel 💀 {link}",
    "budget skincare gw turun drastis setelah nemu {product} ini. hasilnya? tetep bagus 🥹 {link}",
],
```

### Pattern 6: General Fallback (v6.0 Enhanced)
```python
"general": [
    "gw pake {product} ini juga, [specific result]. under 50rb 🤌 {link}",
    "{product} ini bagus bgt sih, gw udah repurchase [X] kali. coba deh 🔥 {link}",
    "no cap {product} ini underrated, coba sebelum sold out 💀 {link}",
    "honest review: {product} ini emang the best buat [category]. link 👇 {link}",
    "auto checkout sih ini, {product} emang worth it banget 🫠 {link}",
],
```

---

## 📐 TEMPLATE PLACEHOLDERS

- `{product}` — Product name from database (e.g. "Moisturizer Glowing")
- `{keyword}` — Matched post keyword (e.g. "jerawat", "rekomendasi")
- `{link}` — Affiliate link (e.g. "https://s.shopee.co.id/AAEFek5Rk0")
- `[X]` — Placeholder for numbers (user must randomize)
- `[specific result]` — Placeholder for result text

### Note for Cron Agent:
The cron agent (when running the reply) must:
1. Randomize [X] numbers (2, 3, 4, etc.)
2. Fill [specific result] with category-appropriate result
3. NEVER leave [X] or [specific result] as raw placeholder in actual comment

---

## 🎯 CONVERSION TRIGGER INJECTION

Every reply must include at least ONE of these:
1. **Price anchor** — "under 50rb", "murah meriah", "affordable"
2. **Specific result** — "dalam 2 minggu", "udah 3x repurchase", "hari ke-7"
3. **Social proof** — "500+ sold", "viral", "rame banget"
4. **Scarcity** — "sering sold out", "restock terus", "limited"
5. **Personal experience** — "gw pake", "hasilnya", "no cap"

### How to Inject:
After selecting template, ADD conversion trigger:
```
Original: "gw juga dulu jerawat parah, nyoba {product} ini emang beda sih 🤌 {link}"
Enhanced: "gw juga dulu jerawat parah, nyoba {product} ini emang beda sih. under 50rb 🤌 {link}"
          (added price anchor)
```

---

## 🔑 OPENER DIVERSITY RULES (CRITICAL)

### Must Use Different Openers Each Time
Track last 10 openers in reply session. NO repeat within 10.

### Good Openers (15+):
1. "gw pake ini juga..."
2. "no cap, [product]..."
3. "udah [X] kali gw beli..."
4. "coba deh..."
5. "murah meriah..."
6. "auto checkout..."
7. "holy grail gw..."
8. "gw juga struggle dulu..."
9. "[product] ini emang..."
10. "honest review:..."
11. "yang ini works bgt..."
12. "alhamdulillah nemu..."
13. "hidden gem sih ini..."
14. "unpopular opinion:..."
15. "gw telat tau..."

### Banned Openers (NEVER):
- ❌ "SLAY" (max 1/500, never opener)
- ❌ "BESTIE" (max 1/200, never opener)
- ❌ "Bestie coba deh"
- ❌ "wah keren banget"
- ❌ "mantap!"
- ❌ "bagus banget!"

---

## 📊 TEMPLATE PERFORMANCE TRACKING

After each reply success, log:
```python
{
    "pattern_used": "relatability_solution",  # Which pattern
    "context_type": "skin_problem",           # Detected context
    "opener": "gw juga dulu",                 # Opener text
    "conversion_trigger": "price_anchor",     # Which trigger
    "product": "Implora Jelly Tint",          # Product
    "link": "s.shopee.co.id/...",             # Link
    "result": "success/pending/hard_blocked", # Result
}
```

This data can be used later to:
- Identify highest-converting patterns
- Track which context types get most clicks
- Optimize opener diversity
- A/B test conversion triggers

---

## ❌ ANTI-PATTERNS (NEVER DO)

- ❌ Too formal: "Produk ini sangat bagus"
- ❌ Too salesy: "BELI SEKARANG DISKON 50%"
- ❌ Too long: > 2 sentences + link
- ❌ Forced slang: "Wah bestie, sungguh luar biasa sekali"
- ❌ Same comment twice: ROTATE patterns!
- ❌ Newline before link: Threads breaks inline link
- ❌ Copy-paste exact same across threads
- ❌ Parenthetical: "(mantap ya)"
- ❌ Multiple exclamation: "BAGUSSS!!!"
- ❌ No affiliate link: MANDATORY
- ❌ Mention "shopee/affiliate": sounds scammy
- ❌ Generic: "bagus banget" without detail
