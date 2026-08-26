# Cronjob Setup Reference

## Provider Configuration (CRITICAL)

User's config ONLY has provider `9router`. No openrouter, no openai configured.

### Correct Model Setting
```python
model={"provider": "9router", "model": "SYADAGENTIC"}
```

### Failed Attempts (DO NOT REPEAT)
| Model | Provider | Result | Error |
|-------|----------|--------|-------|
| `Bozdrop` | 9router | ❌ FAIL | "No active credentials for provider: openai" — Bozdrop routes to OpenAI in 9router |
| `openrouter` | openrouter | ❌ FAIL | "No active credentials" — openrouter not configured |
| `SYADAGENTIC` | 9router | ✅ WORKS | Same as session model, routes correctly |

### Cronjob Timeout Issue
- `execute_code` = 300s (5 min) timeout
- Full CDP flow = 5-8 min → often times out
- Fix: Use `terminal` tool instead (no timeout limit)
- OR: Simple cronjob + manual execution when triggered

---

## ⚠️ One-Shot Cron Jobs — KNOWN UNRELIABLE (2026-05-25)

**Issue:** `cronjob(action='create', schedule='ISO-TIMESTAMP', repeat=1)` sets `next_run_at` correctly but the scheduler **does NOT trigger at the scheduled time**. Even manually running via `cronjob(action='run')` keeps the job in `status: 'scheduled'` without executing.

**Symptoms:**
- Job shows `next_run_at: <correct ISO time>`, `last_run_at: null` past the scheduled time
- Manual `cronjob(action='run')` returns success but `status` stays `scheduled`, `run_count: 0`
- Job appears in `cronjob(action='list')` but never fires

**Root cause:** Unknown scheduler issue with one-shot (repeat=1) ISO timestamp jobs. Recurring interval jobs (e.g., `schedule='30m'`) work fine.

### Workaround: delegate_task Fallback (VERIFIED 2026-05-25)

For time-sensitive CDP operations (e.g., posting at specific golden hours), use `delegate_task` instead of cron:

```python
delegate_task(
    goal="Post to Threads at golden hour [HH:MM] WIB",
    context="""Account: @jagonya_shopee (ID: 3310347890)
Chrome: Profile 16, port 9222, ~/.config/google-chrome

POST CONTENT:
[full post content here]

AFFILIATE LINK: [s.shopee.co.id/XXXXX]

CDP Flow:
1. Launch Chrome: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=$HOME/.config/google-chrome
2. Connect WebSocket, navigate to threads.com (triggers SSO)
3. Navigate to threads.com to post
4. Click 'Buat' button, wait for Lexical editor
5. Focus contenteditable div → Input.insertText(POST_CONTENT) — NO newlines
6. Click 'Kirim' via React __reactProps.onClick dispatch
7. Wait 5s, verify on profile page
8. Close Chrome: osascript -e 'tell application "Google Chrome" to quit'""",
    toolsets=["terminal", "file"]
)
```

**When to use delegate_task vs recurring cron:**
- **Recurring cron** (every 30m): Scanning home feed + commenting = OK, no time pressure
- **delegate_task**: Specific golden hour posts (11:30, 13:00, 20:00 WIB) = MUST USE this, one-shot cron won't fire
- **Manual post via execute_code**: Same as delegate_task but runs in parent session — use when you want to post immediately

### For recurring affiliate comment jobs:
Use interval-based schedule (`'30m'`, `'45m'`, `'1h'`) which works reliably:
```python
cronjob(
    action='create',
    schedule='30m',
    prompt='Scans Threads home feed for fresh beauty posts, comments with Gen Z slang + affiliate link...',
    model={"provider": "9router", "model": "SYADAGENTIC"},
    deliver='origin'
)
```

---

## Alert Format
```
🟢 THREADS POST SUCCESS!
👤 @jagonya_shopee
🔗 [affiliate link] (s.shopee.co.id/XXXX)
💬 Post: [threads URL]
```
