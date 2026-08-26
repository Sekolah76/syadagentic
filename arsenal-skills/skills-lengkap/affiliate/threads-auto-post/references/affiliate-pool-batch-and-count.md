# Affiliate Pool Batch + Count Hygiene (2026-07-13)

## Auto-advance batch (when pool empty)
When a channel's effective UNUSED stock hits 0:
1. Archive current pool copy → `~/.hermes/skills/affiliate/batches/archive/<channel>-batch-NNN-<ts>.md`
2. Load next template: `~/.hermes/skills/affiliate/batches/batch-00N.md` (reject scaffold/placeholder URLs)
3. Advance only that channel's state in `batches/state.json` (no cross-channel steal)

Manager script: `~/.hermes/scripts/affiliate_batch_manager.py`  
Generator scaffold: `python3 ~/.hermes/scripts/generate_affiliate_batch.py --batch N --target 100`  
→ produces `batch-00N.scaffold.md`; SYADAGENTIC fills real `s.shopee.co.id` links → rename to `batch-00N.md`.

## Isolated pools (1 channel = 1 DB copy)
| Channel | Active pool |
|---|---|
| Threads Post | `~/.hermes/skills/affiliate/threads-auto-post/references/affiliate-link-database.md` |
| Threads Reply | `~/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md` |
| Pinterest | `~/.hermes/skills/pinterest-auto-post/references/affiliate-link-database.md` |
| Shared batch template | `~/.hermes/skills/affiliate/batches/batch-003.md` (current) |

Permanent used-sets (no recycle):
- `~/.hermes/scripts/threads_post_used_links.json`
- `~/.hermes/scripts/threads_reply_used_links.json`
- `~/.hermes/scripts/pinterest` history / used set (channel-local)

## Count claim vs unique-link reality
- Header `Total Links: 100` can **lie**. Always count unique `https://s.shopee.co.id/[A-Za-z0-9]+`.
- Session 2026-07-13: all active pools claimed 100, actual unique = **97**.
  - Missing row `#87` (number jump 86→88 in scripts copy)
  - Empty link cell: Kelaya Hair Revitalizer Mist
  - 2 raw dups in scripts copy (`9Kf8dWRnV1`, `20sXuPAkFf`)
- SYADAGENTIC re-pasted partial list (50 links) → diff found **exactly 3 NEW**:
  1. `https://s.shopee.co.id/7pqKrK7PLf` (Retinol)
  2. `https://s.shopee.co.id/6L1X4sIi9N` (Acne)
  3. `https://s.shopee.co.id/6feOqTv4Yr` (Hair spray)
- Injected into all channel copies + `batch-003.md` → **100 unique** verified.

## Diff workflow when SYADAGENTIC re-sends link list
```python
import re
from pathlib import Path
pat = re.compile(r'https?://s\.shopee\.co\.id/[A-Za-z0-9]+')
existing = set(pat.findall(Path(ACTIVE_POOL).read_text()))
new = set(pat.findall(BOZ_PASTE))
print('NEW only:', sorted(new - existing))
print('already:', len(new & existing))
```
- Inject only `new - existing`
- Sync **all** channel copies + shared `batches/batch-00N.md`
- Re-verify: unique count must match claim; fix header if not

## Pitfalls
- Do **not** trust markdown row numbers or "Total Links" without unique regex count.
- Placeholder / scaffold links (`XXXX`, `TODO`, `/BATCH04...`) must be rejected by auto-advance.
- Cross-channel share of one pool is forbidden (pool split 2026-07-13).
- Pinterest skill historically allowed USED→UNUSED recycle; Threads path is permanent used-set. Prefer permanent + batch advance over recycle.
