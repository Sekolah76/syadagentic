# Keyword Rotation System (v6.3 — 2026-06-15)

## Problem
Old keyword list had skincare first (17 keywords), then parfum (10), haircare (8), makeup (7). Script iterated sequentially → skincare ALWAYS tried first every run. Result: skincare monopolized replies, other categories rarely got traffic.

## Fix: Shuffle + Natural Keywords

### Natural Keywords (42 total, balanced)
Replaced rigid "butuh rekomendasi skincare jerawat" with conversational Indonesian:
- **Skincare (12):** `skincare yang bagus apa ya`, `mending skincare apa ya`, `rekomendasiin dong skincare`, etc.
- **Parfum (12):** `parfum yang bagus apa ya`, `parfum budget 50rb`, `rekomendasi parfum murah tapi enak`, etc.
- **Haircare (10):** `shampoo yang bagus apa ya`, `rambut rontok solusinya apa`, `haircare buat rambut rusak`, etc.
- **Makeup (10):** `makeup yang bagus apa ya`, `mending makeup apa buat sehari-hari`, `rekomendasi makeup natural`, etc.

Full list sync'd with `threads_reply_v6.py` KEYWORDS constant.

### Shuffle Implementation
```python
# In main():
shuffled_keywords = KEYWORDS.copy()
random.shuffle(shuffled_keywords)
for keyword in shuffled_keywords:
    # ... search, filter, reply ...
```

Each cron run gets a different random order → categories rotate naturally. No config needed.

## Why Natural Keywords

| Old | New | Why |
|-----|-----|-----|
| `butuh rekomendasi skincare jerawat` | `skincare yang bagus apa ya` | Sounds like real person asking |
| `butuh rekomendasi skincare berminyak` | `mending skincare apa ya` | Conversational, common phrasing |
| `rekomendasi skincare untuk remaja` | `rekomendasiin dong skincare` | Casual request, high volume |
| `butuh rekomendasi parfum tahan lama` | `parfum tahan lama rekomendasi` | Natural word order |
| `butuh rekomendasi haircare ketombe` | `mending shampoo apa buat ketombe` | Specific + conversational |

Threads search is fuzzy → conversational keywords match more real posts than rigid templates.

## Category Balance
| Category | v6.2 (old) | v6.3 (new) |
|----------|-----------|-----------|
| Skincare | 17 (41%) | 12 (29%) |
| Parfum | 10 (24%) | 12 (29%) |
| Haircare | 8 (19%) | 10 (24%) |
| Makeup | 7 (17%) | 10 (24%) |
| **Total** | **42** | **42** |

Skincare reduced from 41% to 29%. All categories within 24-29% range.
