# Hook Engine v1 — Conversion Content (2026-07-13)

Canonical content generator for original Threads posts after browserless publish landed.

## Script
`~/.hermes/scripts/threads_hook_engine.py`

Wired by `cron_post.py`:
```text
CONTENT_MODE_WEIGHTS = { hook: 0.70, tips: 0.15, story: 0.15 }
THREADS_CONTENT_MODE=hook|tips|story|auto
```

## Why
Skill refs already defined conversion hooks (`original-post-templates.md`) but runtime engines only had:
- story: 6 types (`keresahan_malam`…)
- tips: 6 types (`how_to`…)

Hook engine adds full **10 hook categories** with soft-sell rules.

## 10 hook types (rotate; no repeat last 3)
`regret` · `validasi_mental` · `storytelling` · `social_proof` · `myth_buster` · `comparison` · `transformasi` · `pain_point` · `seasonal` · `expert_tip`

## 3-beat rules (hard)
| Post | Role | Allowed | Forbidden |
|---|---|---|---|
| 1 | Hook / scroll-stop | scene, myth, pain, open loop | product name, brand dump, CTA, URL |
| 2 | Value / story | tips, result, soft product ~50% | hard sell, URL |
| 3 | Close | soft CTA + save + `s.shopee.co.id` | hard FOMO / BELI SEKARANG |

## Soft CTA / save banks
Reuse soft sell lines only (skill-aligned):
- “yang mau coba, link ada di bawah 🫶”
- “Save biar ga ilang 🫶”
- no hard-sell uppercase spam

## Output schema (compat)
```json
{
  "post_1": "...",
  "post_2": "...",
  "post_3": "...\nSave...\nhttps://s.shopee.co.id/...",
  "affiliate_link": "https://s.shopee.co.id/...",
  "product_name": "...",
  "hook_category": "<hook_type>",
  "story_type": "<hook_type>",
  "category": "skincare|parfum|haircare|makeup",
  "hook_text": "<first 80 of post_1>",
  "content_mode": "hook_v1"
}
```

## Dedup
Same stack as publisher:
- link forever (history window)
- story/hook type not in last 3
- hook phrasing overlap ≤55% last 8

## Relation to other engines
| Mode | Engine | When |
|---|---|---|
| **hook_v1** | `threads_hook_engine.py` | default 70% |
| tips_v1 | `threads_tips_engine.py` | 15% / fallback |
| story_v1 | `threads_story_engine.py` | 15% / fallback |

## Pitfalls
1. Do **not** put product in post_1 even if product string is long/unique.
2. Do **not** invent hard prices — use range language only if needed.
3. Image-first posts still use same content JSON; image attaches on root only via HTTP engine.
4. After content change, dry-run rotation before unpausing cron.
