# DB Sync Between Reply & Post Automation

## Problem
`threads-auto-reply` and `threads-auto-post` read from **different copies** of `affiliate-link-database.md`:

| Consumer | DB Path |
|----------|---------|
| Reply script (`threads_reply_v6.py`) | `~/.hermes/skills/affiliate/threads-auto-reply/references/` |
| Post script (`cron_post.py`) | `~/.hermes/skills/affiliate/threads-auto-post/references/` |
| Website builder | `~/.hermes/skills/affiliate-website/references/` |
| Legacy reply skill | `~/.hermes/skills/threads-auto-reply/references/` |

## Consequence
- Reply marks link ✅ USED in its copy → post script sees it as ❌ UNUSED in its copy
- Post picks already-used link → duplicate post → dedup may catch it (via history) but wastes an attempt
- Stats drift: each copy shows different Used/Available counts

## Fix: Sync After Any Write
After either reply or post updates a DB copy, sync ALL 4:

```bash
SRC=~/.hermes/skills/affiliate/threads-auto-post/references/affiliate-link-database.md
for dst in \
  ~/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md \
  ~/.hermes/skills/affiliate-website/references/affiliate-link-database.md \
  ~/.hermes/skills/threads-auto-reply/references/affiliate-link-database.md; do
  cp "$SRC" "$dst"
done
```

## Verification
```bash
for f in $(find ~/.hermes/skills -name "affiliate-link-database.md"); do
  echo "$f: $(grep -c '✅ USED' $f) USED, $(grep -c '❌ UNUSED' $f) UNUSED"
done
```
All 4 should show identical counts.

## Lesson (2026-06-15)
Post cron test picked `40dcI3evMO` — already USED by reply 2 hours earlier. Reply had marked it ✅ USED in its DB copy, but post's copy wasn't synced. Now fixed: sync after every write operation.
