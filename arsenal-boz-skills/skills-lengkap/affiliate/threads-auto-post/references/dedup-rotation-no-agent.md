# Dedup · Rotation · no_agent (Threads Post)

Verified 2026-07-13: permanent used-set + heal 41 stale UNUSED → USED · 1 post = 1 link forever.

## Anti-duplicate stack (MUST all run)
1. DB row must be `❌ UNUSED`
2. Link NOT in permanent set `~/.hermes/scripts/threads_used_links.json`
3. Link NOT in `~/.hermes/scripts/threads_post_history.json` (`affiliate_link` set)
4. Link NOT already marked `✅ USED` in affiliate DB (load_history injects these)
5. Product **category** LRU rotation across skincare/parfum/haircare/makeup
6. **story_type** ≠ any of last 3 posts
7. Hook phrasing overlap ≤55% vs last 8 hooks (word set)
8. `check_dedup()` hard-fail before browser/publish
9. Mark DB `✅ USED` **only** after executor returncode == 0
10. Append link to `threads_used_links.json` on success
11. Sync all DB copies after mark

## Hard rule: 1 post = 1 affiliate link forever
- **NO recycle** of previously used links
- `auto_reset_db_if_empty()` is **DISABLED** — never flip `✅ USED` → `❌ UNUSED`
- If stock empty → fail with "refill DB", do not re-post old links
- History file caps at last ~50 posts → **cannot** be the sole dedup source

### Permanent used-set
Path: `~/.hermes/scripts/threads_used_links.json`
```json
{
  "version": 1,
  "rule": "1 post = 1 affiliate link forever",
  "links": ["https://s.shopee.co.id/...", "..."],
  "count": N
}
```
- Written by `cron_post.mark_link_used()`
- Read by `cron_post.main()` into `used_links` before pick

### load_history() must merge
1. `threads_post_history.json` posts
2. All affiliate links with `✅ USED` in primary DB (inject dummy entries if missing from history)

## Canonical paths (CRITICAL)
| Asset | Path |
|---|---|
| History | `~/.hermes/scripts/threads_post_history.json` **ONLY** |
| Permanent used | `~/.hermes/scripts/threads_used_links.json` |
| Scraper | `~/.hermes/scripts/shopee_scraper.py` |
| Executor HTTP | `~/.hermes/scripts/threads_post_http.py` |
| Cron pipeline | `~/.hermes/scripts/cron_post.py` |
| Wrapper (no_agent) | `~/.hermes/scripts/run_threads_post.sh` |
| Primary DB | `~/.hermes/skills/affiliate/threads-auto-post/references/affiliate-link-database.md` |

### Pitfall: history 50-cap recycle
`save_history` keeps `posts[-50:]`. Old links drop out of history → can be re-picked if DB still says UNUSED.
**Fix:** permanent `threads_used_links.json` + DB USED merge + heal unused-but-posted rows.

### Pitfall: auto-reset USED→UNUSED
Old `auto_reset_db_if_empty` recycled all used links when unused hit 0. **Forbidden.** Disabled 2026-07-13.

### Pitfall: history path
`threads_post_*.py` MUST use:
```python
HISTORY_FILE = Path.home() / ".hermes/scripts/threads_post_history.json"
```
Not `Path(__file__).parent / ...` (skill-dir history diverges → duplicates).

### Pitfall: DB not marked USED
History-only dedup is not enough. After success:
- line-safe replace `❌ UNUSED` → `✅ USED (YYYY-MM-DD) — original post: [story] product`
- never regex-replace across pipe table rows (row-merge bug)
- append permanent used-set
- `sync_all_db_copies()`

### Pitfall: UNUSED still in history (heal)
2026-07-13 audit: 41 DB UNUSED rows were already in history. Healed → USED. Re-audit if stock looks inflated.

## no_agent cron shape
| Job | script | no_agent |
|---|---|---|
| Post `23199a7b2d5b` | `run_threads_post.sh` | true |
| Reply `67a687f2978a` | `run_threads_reply_v11.sh` | true |
| Cookie `f1902736896e` | `extract_threads_cookies.py` | true |

Wrapper: Hermes venv python + log `/tmp/threads_post_cron_run.log`.

## Live stock snapshot (2026-07-13 post-heal)
- Permanent used: ~59 unique affiliate links
- Fresh UNUSED: ~39
- UNUSED ∩ permanent: **0**

## Pre-unpause / sanity
```bash
# permanent set present
python3 -c "import json;from pathlib import Path;p=Path.home()/'.hermes/scripts/threads_used_links.json';print(json.loads(p.read_text())['count'])"
# no UNUSED that is already permanent
# cron_post load_history should return history + DB USED inject
python3 -c "import sys;sys.path.insert(0,str(__import__('pathlib').Path.home()/'.hermes/scripts'));from cron_post import load_history;print(len(load_history()))"
```
