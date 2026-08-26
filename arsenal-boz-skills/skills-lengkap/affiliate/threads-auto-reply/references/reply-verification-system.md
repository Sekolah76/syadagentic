# Reply Verification System (v6.3 — 2026-06-15)

## Problem
Old verification checked `"s.shopee.co.id" in document.body.innerText` after reload — this ALWAYS returns `True` because our own comment (with the link) is always visible to the account that posted it, even when shadowbanned to other users. Result: false positive "✅ REPLY VISIBLE" for invisible comments.

## v6.2+ Fix: Two-Layer Verification + Relevance + Rotation

### Layer 1: API Response Check (PRIMARY)
After clicking "Kirim"/"Post", intercept the `configure_text_only_post` API response:
- **Explicit OK required**: `"status":"ok"` MUST appear in response body
- **Fail = hard blocked**: `"status":"fail"` or `"Media blocked due to integrity"` → return `"hard_blocked"`
- **No API log captured**: return `"pending"` (can't verify)
- **Ambiguous (no explicit ok)**: return `"pending"`

```python
if '"status":"ok"' not in body_resp:
    log("⚠️ API response ambiguous — no explicit ok")
    return "pending"
```

### Layer 2: Page Reload Verification (SECONDARY)
After API OK, reload page and check BOTH:
1. `"s.shopee.co.id"` in body (link visible)
2. Comment snippet (first 30 chars) in body

```python
comment_snippet = comment_text[:50]
link_visible = "s.shopee.co.id" in verify_body
comment_visible = comment_snippet[:30] in verify_body

if link_visible and comment_visible:
    return "success"  # ✅ Both visible
elif link_visible:
    return "pending"  # ⚠️ Link visible but comment not — likely shadowbanned
else:
    return "pending"  # ⚠️ Nothing visible
```

## Relevance Filter (v6.2)
Prevents replying skincare to home-decor posts (Threads search is fuzzy).

`is_post_relevant(post_text, category)` checks post content for category-specific keywords:

| Category | Keywords checked |
|----------|-----------------|
| skincare | skincare, jerawat, berminyak, kering, glowing, kusam, bruntusan, flek, komedo, moisturizer, sunscreen, serum, toner, face wash, cuci muka, skin barrier, niacinamide, retinol |
| parfum | parfum, wangi, fragrance, tahan lama, enak, bau, semprot, mist |
| haircare | haircare, rambut, rontok, ketombe, shampoo, conditioner, hair tonic, vitamin rambut |
| makeup | makeup, foundation, lip tint, lipstik, cushion, bedak, blush, eyeshadow, mascara, eyeliner, setting spray |

Called inside `reply_to_post()` AFTER extracting post text, BEFORE MUA/shopee filters.
Returns `"skipped_irrelevant"` → main loop continues to next post (does NOT mark link as used).

## Dedup System (v6.1)
See `reply-dedup-system.md` for full details. Summary:
- `mark_link_used()` — DB-based (primary)
- `is_link_used_before()` — history-based (backup)
- `is_comment_duplicate()` — last 50 reply check
- `save_history()` — append after each SUCCESS only (NOT pending)

## PENDING Handling (v6.3)

**Critical rule: PENDING does NOT count as success.** When `reply_to_post()` returns `"pending"`:
- ❌ Do NOT call `mark_link_used()` — link stays UNUSED
- ❌ Do NOT call `save_history()` — no history entry
- ❌ Do NOT increment `replies_done` — try next post/keyword
- ✅ Continue to next post (same keyword) or next keyword

**Rationale:** Old behavior wasted links on unverified comments. PENDING might mean shadowban, API ambiguity, or temporary glitch — the link is still usable for a future attempt.
