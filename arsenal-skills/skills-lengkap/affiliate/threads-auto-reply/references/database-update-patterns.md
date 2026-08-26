# Database Update Patterns — threads-auto-reply

## Why Python > macOS sed for database edits

macOS BSD `sed -i '' 'Na\...'` (append after line N) fails with:
- Backticks `` ` `` (used in all link entries)
- Asterisks `*` (used in bold markdown)
- Regex special chars in replacement strings

**Always use Python string replacement** for `affiliate-link-database.md` edits.

## Reliable update pattern (copy-paste snippet)

```python
from hermes_tools import terminal, write_file

# Read file
result = terminal("cat /Users/user/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md")
content = result['output']

# Replace link status (old_string must be unique)
old = "|| 2 | `https://s.shopee.co.id/5q5GUQ7asu` | ❌ UNUSED |"
new = "|| 2 | `https://s.shopee.co.id/5q5GUQ7asu` | ✅ USED (2026-05-27) — replied to @user makeup post |"
content = content.replace(old, new, 1)

# Update stats (find-and-replace works)
content = content.replace("Used:** 33/50 links (66%)", "Used:** 34/50 links (68%)")

# Insert at top of Recently Used section
old = "## Recently Used — Batch 2 (auto-update)\n- **Cushion Coverage #3**"
new = "## Recently Used — Batch 2 (auto-update)\n- **Setting Spray #2** (`5q5GUQ7asu`) — replied to @user makeup post (2026-05-27) ← NEW\n- **Cushion Coverage #3**"
content = content.replace(old, new, 1)

# Write back
write_file("/Users/user/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md", content)
```

## If you MUST use sed (simple line replacements only)

```bash
# Safe: simple text substitution (no special chars in pattern)
sed -i '' 's/33\/50 links (66%)/34\/50 links (68%)/' FILE

# Unsafe: append/insert with special chars — DO NOT USE
# sed -i '' '89a\  ← FAILS with backticks, asterisks
```

## read_file dedup behavior

`hermes_tools.read_file()` returns `{'content_returned': False}` if the same file+offset+limit was read earlier in the session. Workarounds:
1. Cache content after first read
2. Use `terminal("cat ...")` for guaranteed fresh read
3. Use `terminal("sed -n '89p' ...")` for specific line reads (simple sed works for reads, just not writes)
