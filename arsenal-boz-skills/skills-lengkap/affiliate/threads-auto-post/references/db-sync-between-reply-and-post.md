# DB Sync Between Reply & Post Automation

## Problem
`threads-auto-reply` and `threads-auto-post` read from **different copies** of `affiliate-link-database.md`:

| Consumer | DB Path |
|----------|---------|
| Reply script (`threads_reply_v6.py`) | `~/.hermes/skills/affiliate/threads-auto-reply/references/` |
| Post script (`cron_post.py`) | `~/.hermes/skills/affiliate/threads-auto-post/references/` |
| Website builder | `~/.hermes/skills/affiliate-website/references/` |
| Legacy reply skill | `~/.hermes/skills/threads-auto-reply/references/` |

## Fix: Sync After Any Write
```bash
SRC=~/.hermes/skills/affiliate/threads-auto-post/references/affiliate-link-database.md
for dst in \
  ~/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md \
  ~/.hermes/skills/affiliate-website/references/affiliate-link-database.md \
  ~/.hermes/skills/threads-auto-reply/references/affiliate-link-database.md; do
  cp "$SRC" "$dst"
done
```

## Lesson (2026-06-15)
Post cron picked USED link because its DB copy wasn't synced after reply run.
