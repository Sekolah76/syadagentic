# Isolated Affiliate Pools + Auto Batch Advance (2026-07-13)

## Why
Shared single `affiliate-link-database.md` was drained by concurrent Threads Post + Reply + Pinterest crons. Cross-sync (`DB_COPIES` copying post USED → reply DB) made it worse.

## Paths
| Channel | Runtime DB | Used-set JSON | Manager channel key |
|---|---|---|---|
| Threads Post | `skills/affiliate/threads-auto-post/references/affiliate-link-database.md` | `scripts/threads_post_used_links.json` | `threads_post` |
| Threads Reply | `skills/affiliate/threads-auto-reply/references/affiliate-link-database.md` | `scripts/threads_reply_used_links.json` | `threads_reply` |
| Pinterest | `skills/pinterest-auto-post/references/affiliate-link-database.md` | `scripts/pinterest_used_links.json` | `pinterest` |

## Hard rules
1. **No cross-sync.** Post success must not rewrite reply/pinterest DB.
2. **1 action = 1 link forever** per channel (used-set survives history 50-cap).
3. Same product URL may exist in all 3 pools with **independent** USED state.
4. Recycle USED→UNUSED is **disabled** on all three runners.

## Auto-advance (`scripts/affiliate_batch_manager.py`)
On each cron start: `ensure_pool_has_unused(channel)`.
1. Count **effective UNUSED** = rows `❌ UNUSED` whose link ∉ channel used-set.
2. If 0: archive DB → `skills/affiliate/batches/archive/` → load next `batches/batch-NNN.md` with fresh links only → rewrite channel DB all UNUSED → bump `batches/state.json`.
3. Scaffold placeholders (`/BATCH04…`) are rejected at parse time.
4. Missing next batch → log path to add `batch-004.md` (real shortlinks only).

## Add next batch
```bash
python3 ~/.hermes/scripts/generate_affiliate_batch.py --batch 4 --target 100
# edit batch-004.scaffold.md → real s.shopee.co.id links
# save as batches/batch-004.md
```

## Scripts
- Manager: `~/.hermes/scripts/affiliate_batch_manager.py`
- Scaffold: `~/.hermes/scripts/generate_affiliate_batch.py`
- Post wires manager in `cron_post.main()` before pick.
- Reply wires manager in `threads_reply_v11.main()` before parse_database.
- Pinterest wires manager in `cron_pinterest.main()` + force-advance when all 4 cats empty.

## Shopee Review Image Pitfalls (2026-07-13 live)
| Symptom | Cause | Fix |
|---|---|---|
| Found 0 review imgs | Stopped scroll on title "Penilaian" | Require `.product-rating-overview__filter` chips |
| Images ~5KB | Used `currentSrc` thumb | Use original `src` + strip `@resize_w*_nl` |
| Catalog photos | Landed on shop page | Product-ID hard gate `/product/{shop}/{item}` |
| Case miss "Bintang" | `includes('bintang')` case-sensitive | `toLowerCase()` |
| Cookie extract empty | P16 SQLite sparse | `camoufox cookies get` after headed open |
