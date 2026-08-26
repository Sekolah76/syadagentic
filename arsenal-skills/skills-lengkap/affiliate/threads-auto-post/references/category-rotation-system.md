# Category Rotation System (v4 — 2026-06-15)

## Overview
All 4 product categories rotate evenly. No more skincare monopolizing posts.

## Categories

| Category | Hook Variations | POST2 Templates | Stock (UNUSED) |
|----------|----------------|-----------------|----------------|
| skincare | 6 categories × 2-3 hooks = 13 total | 4 templates | ~5 |
| parfum | 5 categories × 2 hooks = 10 total | 4 templates | ~12 |
| haircare | 4 categories × 2 hooks = 8 total | 4 templates | ~9 |
| makeup | 4 categories × 2 hooks = 8 total | 4 templates | ~11 |

## Detection Keywords

```python
def detect_category(product_name):
    p = product_name.lower()
    # Parfum
    if any(w in p for w in ["parfum", "fragrance", "edt", "edp", "eau de toilette", "perfume"]):
        return "parfum"
    if "mist" in p and "setting" not in p and "spray" not in p:
        return "parfum"
    # Haircare
    if any(w in p for w in ["hair", "shampoo", "conditioner", "rambut", "tonic", "ketombe", "rontok"]):
        return "haircare"
    # Makeup (comprehensive)
    if any(w in p for w in [
        "lip", "makeup", "foundation", "cushion", "powder", "blush", "mascara",
        "eyeliner", "setting spray", "jelly", "tint", "gloss", "melting balm",
        "two way cake", "bb cream", "lipstik", "lipstick", "brows", "concealer",
        "contour", "highlighter", "eyeshadow",
    ]):
        return "makeup"
    # Skincare: default fallback
    return "skincare"
```

## Rotation Algorithm

```python
def pick_category_and_product(unused_by_cat, recent_cats):
    available_cats = [c for c in ALL_CATEGORIES if unused_by_cat.get(c)]
    
    # Priority 1: categories NOT in last 4 posts (full rotation)
    recent_unique = list(dict.fromkeys(recent_cats))
    fresh_cats = [c for c in available_cats if c not in recent_unique]
    if fresh_cats:
        return random.choice(fresh_cats), random.choice(unused_by_cat[cat])
    
    # Priority 2: least recently used (LRU)
    cat_last_idx = {}
    for i, c in enumerate(reversed(recent_cats)):
        cat_last_idx[c] = i  # overwrite = keep last (newest) index
    for c in available_cats:
        if c not in cat_last_idx:
            cat_last_idx[c] = 999
    available_cats.sort(key=lambda c: cat_last_idx.get(c, 999))
    return available_cats[0], random.choice(unused_by_cat[cat])
```

## Verified Distribution (16-run test)
```
1. skincare   → SOMETHINC Level 1% Encapsulated Retinol Serum
2. haircare   → Garnier Ultra Blends Shampoo Biryani
3. makeup     → Luxcrime Blur & Cover Two Way Cake
4. parfum     → HEURA Scandal Body Mist 100ml
5. skincare   → Ultra Light Daily Sunscreen SPF 50+ PA++++
6. haircare   → Dove Hair Therapy Nourishing Oil Care
7. makeup     → Make Over Velvet Lip Cream
8. parfum     → Elegant Secret Parfum Women EDP
9. skincare   → SKINTIFIC Retinol 2pcs Set Skin Renewal
10. haircare  → Sunsilk Black Shine Shampoo 160ml
11. makeup    → Implora Jelly Tint with Omega & Vit E
12. parfum    → SLAVINA Body Mist Red Opium by Nagita
13. skincare  → BREYLEE Tea Tree Acne Gel Perawatan Jerawat
14. haircare  → HazelOile Shampoo Non SLS Professional Therapy
15. makeup    → Carven & Co Lioplus Lip Tint Matte
16. parfum    → RSW Perfume Amber Noir EDP 35ml

📊 Distribution: {'skincare': 4, 'parfum': 4, 'haircare': 4, 'makeup': 4}
✅ Perfect 25% each
```

## 3-Post Content Format

```
POST_1: Hook emosional spesifik kategori
  - edukasi (kontenhustle style)
  - validasi_mental (akangsyauqi style)
  - storytelling (notesofmira style)
  - problem_solving (yowezz style)
  - hook_pancingan (mamakvisioner style)
  - transformasi (before/after)

POST_2: Value/insight detail (NOT just CTA!)
  - Review jujur 2-3 kalimat
  - Tips/tricks spesifik produk
  - Comparison dengan produk lain
  - Personal experience + data

POST_3: CTA + save line + affiliate link
  - CTA: "Cek rekomendasi gw di bawah 👇"
  - Save: "Save biar ga ilang 🫶"
  - Link: https://s.shopee.co.id/XXXX
```

## DB Sync After Post

```python
DB_COPIES = [
    Path.home() / ".hermes/skills/affiliate/threads-auto-post/references/affiliate-link-database.md",
    Path.home() / ".hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md",
    Path.home() / ".hermes/skills/affiliate-website/references/affiliate-link-database.md",
    Path.home() / ".hermes/skills/threads-auto-reply/references/affiliate-link-database.md",
]

def sync_all_db_copies():
    src = DB_COPIES[0]
    for dst in DB_COPIES[1:]:
        dst.write_text(src.read_text())
```

## Cron Config

```python
cronjob(
    action='update',
    job_id='23199a7b2d5b',
    name='Threads Post v11 — Rotasi 4 Kategori + DB Sync',
    schedule='0 8,13,20 * * *',
    no_agent=True,
    script='cron_post.py'
)
```
