# Reply Dedup System (v6.1, 2026-06-15)

## Problem
`mark_link_used()` crashed silently for weeks — `'str' object has no attribute 'read_text'`. Links NEVER got marked USED → 48 same links recycled every 120m → comments looked spammy.

## Root Cause
```python
DATABASE_PATH = os.path.expanduser("...")  # returns str
content = DATABASE_PATH.read_text()  # CRASH: str has no read_text
```

## Fix
```python
dbp = Path(DATABASE_PATH)  # wrap in Path
content = dbp.read_text()  # works
```

## 3-Layer Dedup Architecture

### Layer 1: Database Mark (primary)
- `mark_link_used(link_url)` → `❌ UNUSED` → `✅ USED`
- Uses `Path(DATABASE_PATH)` wrapper
- Also handles backtick-wrapped URLs in DB

### Layer 2: Reply History JSON (backup)
- File: `~/.hermes/scripts/reply_history.json`
- Format: `[{link, product, post, comment, result, timestamp}, ...]`
- Auto-created on first write
- `is_link_used_before(link_url)` — checks entire history
- `is_comment_duplicate(comment_text)` — checks last 50 entries

### Layer 3: Comment Dedup (prevent identical comments)
- Generate comment → `is_comment_duplicate()` → regenerate up to 5x
- Only checks against last 50 replies (not full history)

## Pending Handling
- PENDING replies do NOT mark link as USED
- PENDING replies do NOT save to history
- PENDING replies do NOT increment reply count
- Only SUCCESS triggers mark + save
- Rationale: if API didn't confirm, link might be wasted

## Verification Test Pattern
After script changes, run 1 manual test and verify:
1. `mark_link_used()` works (no crash)
2. `reply_history.json` created/updated
3. DB status changed to `✅ USED`
4. Comment visible on Threads app (manual check)
