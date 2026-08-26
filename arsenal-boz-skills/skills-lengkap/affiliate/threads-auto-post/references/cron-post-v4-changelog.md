# Threads Auto-Post — Cron Post Script v4 (2026-06-15)

## Changelog

### v2 → v4 (2026-06-15)
1. **Multi-category hooks** — 4 categories × 4-6 hook categories × 2-3 variations each
2. **Category auto-detection** — `detect_category(product_name)` from product name
3. **Perfect rotation** — `pick_category_and_product()` tracks last 8 categories, prefers LRU
4. **POST_2 value templates** — Per-category insight/review (not just CTA)
5. **DB sync after post** — `sync_all_db_copies()` updates all 4 copies
6. **Stock reporting** — Prints remaining links per category

### Bug Fixes
- **LRU rotation bug** — Was tracking first occurrence instead of last → skincare always picked
- **"other" category detection** — 9 products missed (setting spray, jelly tint, bb cream, edt, etc)
- **DB copy sync** — Reply marks USED in `threads-auto-reply/` DB, post reads from `threads-auto-post/` DB

## Category Detection Keywords
```python
"parfum": ["parfum", "fragrance", "edt", "edp", "eau de toilette", "perfume"]
"haircare": ["hair", "shampoo", "conditioner", "rambut", "tonic", "ketombe", "rontok"]
"makeup": ["lip", "makeup", "foundation", "cushion", "powder", "blush", "mascara",
           "eyeliner", "setting spray", "jelly", "tint", "gloss", "melting balm",
           "two way cake", "bb cream", "lipstik", "lipstick", "brows", "concealer",
           "contour", "highlighter", "eyeshadow"]
"skincare": [default fallback]
```

## Rotation Algorithm
1. Parse all UNUSED links from DB
2. Group by category (detect_category)
3. Get last 8 categories from history
4. Priority 1: categories NOT in last 4 (full rotation)
5. Priority 2: least recently used (ascending sort by last-seen index)
6. Pick random product from chosen category

## DB Sync (4 copies)
```
threads-auto-post/references/affiliate-link-database.md   ← PRIMARY
threads-auto-reply/references/affiliate-link-database.md
affiliate-website/references/affiliate-link-database.md
threads-auto-reply/references/affiliate-link-database.md (legacy)
```
