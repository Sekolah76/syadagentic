# Threads Reply Stealth v10 — Architecture & Pitfalls (2026-06-30)

Built during session 30 Jun 2026 after Wardah hair-serum strike triggered Tier-1
warning + hard comment-block on jagonya_shopee. Existing v9 verifier was
returning false-positive "verified visible" while replies were actually being
server-discarded. v10 fixes this with real cross-account verification.

## Three-Module Stealth Pattern

Production scripts live at `~/.hermes/scripts/`:

```text
threads_reply_v6.py            ← orchestrator (Playwright headless)
├── threads_human_behavior.py  ← burst gate, log-normal delays, sleep window
├── threads_content_gen.py     ← LLM per-reply via 9router
└── threads_cross_verify.py    ← Camoufox real-Chrome anon viewer check
```

State files (durable across runs):

```text
~/.hermes/state/threads_burst_state.json       # burst window, cooldown
~/.hermes/state/threads_shadowban_state.json   # consecutive shadowban counter
```

## Module 1 — Behavior Layer (`threads_human_behavior.py`)

- **`should_act_now()`** — pre-flight gate. Checks sleep window (01:00-07:00
  WIB hard-skip) + cooldown_until timestamp. Returns `(bool, reason)`. Call once
  at script start and again after every successful action.
- **`register_action()`** — increments burst counter, triggers random
  `cooldown_until = now + uniform(45m, 120m)` when burst hits `randint(2, 4)`.
  Resets burst on cooldown trigger.
- **`human_delay(profile)`** — log-normal distribution, NOT uniform random.
  Profiles: `between_chars` (~120ms), `before_click` (~0.6s), `after_paste`
  (~3s), `before_post` (~8s), `between_replies` (~45s), `page_settle` (~2.5s).
  Log-normal gives long-tail variance that mimics human pauses.
- **`human_type(page, text)`** — per-char log-normal typing with 3% chance of
  micro-pause (mid-word thinking).

## Module 2 — Content Generation (`threads_content_gen.py`)

- **Model choice is critical.** `ag/gemini-3-flash-agent` is a reasoning model
  — thinking tokens leak into `content` field producing garbage like
  "Let's look closer. The instruction:". Use `kr/claude-sonnet-4.5` for clean
  casual ID gen-z output. See `9router-chat` skill for the broader pattern.
- **9router defaults to SSE streaming.** Even with `stream: false` payload it
  may return `text/event-stream`. Helper `_parse_router_response()` handles
  both JSON and SSE chunked formats. Without this, `json.loads()` raises
  `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`.
- **`generate_reply(product, url, op_text)`** — context-aware reply using OP
  post text as system prompt context. System prompt forbids salesy words
  ("produk", "rekomendasi", "berkualitas") and enforces casual gen-z ID style.
- **Anti-duplicate via word-overlap cosine** (cheap, no embeddings). Threshold
  0.7 against last 50 replies. Retry once with temp 1.3 on too-similar hit.
- **30% typo simulation**: replace `yang→yg`, `banget→bgt`, `aja→aj`, etc.
- **Emoji injection**: 20-pool rotation, inject before URL if missing.
- **Fallback to templates** if LLM call fails entirely.

## Module 3 — Cross-Account Verifier (`threads_cross_verify.py`)

The most important addition. v9's own-session reload verifier was systematically
fooled by Meta's UX-render-but-server-discard behavior post-strike.

- **Use Camoufox real Chrome** (`chrome_local_102130715962900495`) — bypasses
  fingerprint detection that Playwright headless hits. Threads.com returns 404
  for `@user` URLs from headless Chromium but works fine in real Chrome.
- **Persistent session pattern**: `_get_session()` lazy-opens session at first
  call, subsequent calls reuse via `navigate`. First check ~25s, subsequent
  ~12s (saves ~15s/check).
- **Use `get markdown` not `get text`** — `get text <index>` requires element
  index, not full page dump. `get markdown` returns whole page content.
- **`SHADOWBAN_THRESHOLD = 2`** — auto-pause cron `67a687f2978a` after 2
  consecutive hard-shadowbans. Was 3 initially; 2 is faster recovery.
- **CRITICAL: After `triggered_pause` fires, `return` from main() — DON'T
  continue.** Original patch had `continue` which kept searching new keywords
  after pause was triggered, wasting 5+ more minutes. Fix: `browser.close()` +
  `return` in the orchestrator after auto-pause.

## Integration Points in `threads_reply_v6.py`

1. **`main()` start** — call `hb.should_act_now()`, skip if False.
2. **`get_comment()`** — swap template-only to `from threads_content_gen
   import generate_reply` with template fallback.
3. **Before post submit** — `time.sleep(hb.human_delay("before_post"))`
   instead of fixed `page.wait_for_timeout(10000)`.
4. **After own-session DOM verify SUCCESS** — must follow with cross-account
   check before declaring success. Order matters: own-session-fail = soft SB
   = continue next post; cross-account-fail = hard SB = increment counter and
   maybe trigger pause.
5. **After successful reply** — `hb.register_action()` then
   `time.sleep(hb.human_delay("between_replies"))` then re-check gate
   (cooldown might have triggered mid-burst).
6. **After auto-pause** — `browser.close()` + `return` to exit entire run.

## Test Run Observations (30 Jun 2026)

```text
Test 1 (verifier off, just behavior layer):
  Result: 1 reply "VERIFIED VISIBLE" by own-session reload
  Cross-check via Camoufox: NOT visible to anon viewer
  → Confirms false-positive trap

Test 2 (full v10 with cross-verifier):
  Result: 4 attempts × ~60-90s each = ~6 min total
  All cross-checks: visible=False, username_count=0
  Threshold hit at 2 consecutive HARD shadowbans
  Cron auto-paused at 2026-06-30T15:16:48Z ✓

Per-attempt timing breakdown:
  Threads page nav      :  6-8s
  Editor + paste        :  2-3s
  Human review delay    :  4-15s (log-normal)
  Post submit + verify  :  8s
  Own-session reload    :  8s
  Camoufox anon check : 12-30s (first 25s, rest 12s)
  Inter-reply sleep     :  5-90s (log-normal)
  ───────────────────────────────────────────
  ~60-120s per attempt
```

## Pitfalls Discovered

| # | Pitfall | Fix |
|---|---------|-----|
| 1 | v9 verifier "VERIFIED VISIBLE" is false-positive post-strike | Add cross-account check via Camoufox |
| 2 | `ag/gemini-3-flash-agent` content field returns reasoning tokens | Use `kr/claude-sonnet-4.5` for clean output |
| 3 | 9router defaults to SSE even with `stream: false` | `_parse_router_response()` handles both formats |
| 4 | `get text` requires element index, not full page | Use `get markdown` for full page dump |
| 5 | Playwright headless gets 404 on `threads.com/@user` | Use Camoufox real Chrome (chromium fingerprint differs) |
| 6 | `continue` after auto-pause wastes time on next keyword | `return` from main() after pause triggered |
| 7 | Python stdout buffering hides progress in background mode | `PYTHONUNBUFFERED=1 python3 -u script.py` |
| 8 | New Camoufox session per check costs ~25s | Persistent session via `_get_session()` global |
| 9 | Threads.com vs Threads.net different fingerprint gates | Verifier uses threads.net URLs (more permissive) |
| 10 | Indentation broke when patching multi-block flow | Re-read whole file before sweeping patch; verify `ast.parse()` after |

## Post-Strike Recovery Timeline

Tier-1 warning ("post removed" notice on mobile, e.g. for false-positive nudity
classification on skincare post):

```text
T+0h     : Strike fires, reply hard-block starts
T+0-48h  : ALL replies silent-discarded, 100% shadowban rate
T+48-96h : Partial unblock — some replies visible, some not (probe needed)
T+96-168h: Full recovery if no further strikes within window
T+168h+  : Normal operations resume
```

**Appeal** ("Perbaiki" button in mobile) accelerates recovery. 177-day window
to submit. If approved, shadowban lifts within 24-48h after approval.

## Standalone Probe (no posting)

When BOZ asks "is shadowban lifted yet?", run probe without sending replies:

```bash
python3 ~/.hermes/scripts/threads_cross_verify.py "https://www.threads.net/<recent-post-url>"
# exit 0 = visible (BOZ in comments), exit 1 = shadowbanned, exit 2 = error
```

## Cron Integration

Cron job `67a687f2978a` ("Threads Reply v8 — CDP Script Auto") schedule
`every 240m`. Auto-paused by `threads_cross_verify.py` via:

```python
subprocess.run(["hermes", "cron", "pause", "67a687f2978a"], capture_output=True, timeout=10)
```

Manual resume: `hermes cron resume 67a687f2978a` after running probe and
confirming reply visible cross-account.
