# Story-Mode Reply (2026-07-12)

Post system = **jual cerita** → reply must match tone.

## Engine
- `~/.hermes/scripts/threads_content_gen.py`
- `~/.hermes/scripts/threads_story_engine.py` → `build_story_reply_prompt`, `story_reply_fallback`

## Rules
| Do | Don't |
|---|---|
| Empati / lanjut cerita / nanya balik | Hard sell ("cek sekarang", flash sale) |
| 8–18 kata, 1 baris | Paragraf / list |
| Soft product max 1x (or skip) | "rekomendasi terbaik" |
| URL plain di akhir | CTA agresif |

## Fallback templates
- `ih iya bgt, gw juga gitu… belakangan nemu {product} yang nyambung {url}`
- `relate banget. dulu overthinking mulu, skrg lebih tenang {url}`
- `sama, gw jg pernah. soft aja ya: {product} {url}`

## Hard-sell filter
If LLM emits: cek sekarang / beli di sini / flash sale / terbaik / rekomendasi / wajib coba / order sekarang → regenerate or fallback.

## Ops note (2026-07-12)
- Cron reply stays **paused** with post until BOZ unpause after auth+story preflight.
- Job `67a687f2978a` → `run_threads_reply_v11.sh` · `no_agent=true`.
- Post auth blocker (wrong/expired `@jagonya_shopee` session) also blocks reply SSO — see post skill `references/auth-preflight-jagonya.md`.
- Soft reply still uses affiliate link when relevant, but tone = continue story / empati, never hard product dump.
