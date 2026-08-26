# Content: Cerita vs Tips (SYADAGENTIC correction 2026-07-13)

## Rule
**Pahami dulu mode konten** sebelum generate copy:
1. **Cerita** — jual lewat narasi / relatable experience
2. **Tips** — jual lewat value / how-to / myth-bust

Jangan generate hook generik pendek dulu baru mikir framing. Mode dulu → hook family → 3-beat panjang.

## Engine
`~/.hermes/scripts/threads_content_engine.py`
- `force_mode="cerita"|"tips"|None`
- `content_mode`: `cerita_v3` / `tips_v3`
- Cron mix default: cerita ~55% / tips ~45%
- Env override: `THREADS_CONTENT_MODE=cerita|tips|auto`

## Hook families
### Cerita
`regret` · `validasi_mental` · `storytelling` · `social_proof` · `transformasi` · `pain_point`

### Tips
`myth_buster` · `comparison` · `expert_tip` · `how_to` · `checklist` · `mistake`

## 3-beat length (HARD)
| Beat | Role | Length | Forbidden |
|---|---|---|---|
| P1 | Hook | 1–2 kalimat, panjang cukup | URL; product dump di mode cerita |
| P2 | Value/body | 2–3 kalimat + timeframe/texture/result | hard CTA / URL |
| P3 | Close | soft CTA + save + affiliate + engagement Q | hard sell / "BELI SEKARANG" |

Soft product bridge di P2 (~45% cerita, ~70% tips).

## SYADAGENTIC rejection signals
- "Masih kurang itu teks postingan nya" → P1/P2 terlalu pendek
- "Pertama harus pahami dulu mau bikin konten cerita atau tips" → mode decision missing
- Ultra-short comparison one-liners without body detail → rewrite with longer P2

## Success checklist
- [ ] Mode decided first (cerita/tips)
- [ ] Hook family rotated (no repeat last 3)
- [ ] P1 long enough (not one tiny clause)
- [ ] P2 has detail (timeframe / texture / result)
- [ ] P3 has `s.shopee.co.id` + save + question
- [ ] Real product image attached when available (HTTP rupload)

## Related refs
- `original-post-templates.md` — conversion triggers + sample full posts
- `story-mode-jual-cerita.md` — soft-sell rules
- `browserless-http-engine.md` — publish path
