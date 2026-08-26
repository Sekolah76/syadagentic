# Story Mode / Jual Cerita (2026-07-12)

SYADAGENTIC redesign: Threads **original posts** = jual cerita, bukan review/value tip polos.

## Engine
- Runtime: `~/.hermes/scripts/threads_story_engine.py`
- Wired by: `~/.hermes/scripts/cron_post.py` (v5+)
- Executor: `~/.hermes/scripts/threads_post_v6.py`
- Dry-run (no browser): `~/.hermes/scripts/threads_story_dry_run.py 12`

## 3-beat formula (HARD platform max 3 posts)
| Post | Role | Allowed | Forbidden |
|---|---|---|---|
| 1 | Scene + konflik | curhat, open loop | product, brand, CTA, URL |
| 2 | Twist / insight | soft product ~40% max | hard CTA, URL |
| 3 | Close | soft CTA + save + `s.shopee.co.id` | hard sell / FOMO palsu |

## 6 story types (rotate; no repeat last 3)
`keresahan_malam` · `malu_sosial` · `salah_beli` · `teman_bukti` · `open_loop` · `regret`

Mapped per product category: skincare / parfum / haircare / makeup.

## Soft CTA bank
- yang mau coba, link ada di bawah 🫶
- yang penasaran, gw taro link-nya 👇
- save dulu aja, nanti kalo butuh tinggal klik 📌
- buat yang mau coba, cek di bawah ya 🤍

## History fields (required)
```json
{
  "hook_category": "<story_type>",
  "story_type": "<story_type>",
  "category": "skincare|parfum|haircare|makeup",
  "hook_text": "<first 80 of post_1>",
  "affiliate_link": "https://s.shopee.co.id/...",
  "content_mode": "story_v1",
  "status": "posted"
}
```

## SYADAGENTIC rules (session)
- Riset dulu before redesign — then implement.
- Test content rotation **before** unpause cron.
- All Threads crons: `no_agent:true` + shell/python script only.
- No duplicate post hooks, no duplicate affiliate links.
