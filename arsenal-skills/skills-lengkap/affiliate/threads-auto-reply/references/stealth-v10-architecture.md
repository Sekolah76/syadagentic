# Stealth v10 Architecture (2026-06-30)

Threads reply auto-bot upgraded to v10 with 3-module split, LLM per-reply content, cross-account verifier, and auto-pause-cron on consecutive shadowban. Built and tested same session as the post-strike shadowban on jagonya_shopee — every technical layer works; account-level block is what stopped real-world replies.

## Module split

```
~/.hermes/scripts/
├── threads_reply_v6.py            # orchestrator (Playwright headless, SSO flow)
├── threads_human_behavior.py      # burst gate, log-normal delay, sleep window
├── threads_content_gen.py         # LLM via 9router (Claude Sonnet 4.5)
└── threads_cross_verify.py        # Camoufox anonymous-viewer shadowban check

~/.hermes/state/
├── threads_burst_state.json       # burst/cooldown counter, persists across runs
└── threads_shadowban_state.json   # consecutive-shadowban counter, history list
```

## Module 1 — `threads_human_behavior.py`

- `should_act_now()` → (allowed, reason). Gates on:
  - Sleep window 01:00–07:00 WIB (timezone-aware `datetime`)
  - Active cooldown (45–120 min random after burst limit hit)
- `register_action()` — call after every successful reply:
  - Increments burst counter (2–4 random cap)
  - When cap reached, sets `cooldown_until = now + uniform(45m, 120m)` and resets counter
- `human_delay(profile)` — log-normal distribution, NOT uniform random:
  - 6 named profiles: `between_chars` (~0.12s), `before_click` (~0.6s), `after_paste` (~3s), `before_post` (~8s), `between_replies` (~45s), `page_settle` (~2.5s)
  - `mean` + `sigma=0.4–0.7`, clamped to `[0.05, mean*6]`
- Default state file path: `~/.hermes/state/threads_burst_state.json`

## Module 2 — `threads_content_gen.py`

- `generate_reply(product, url, op_text="")` calls 9router `/v1/chat/completions`
- **MODEL = `kr/claude-sonnet-4.5`** — non-reasoning. Tested `ag/gemini-3-flash-agent` first: think-tokens leaked into content (`"Let's look at the instruction..."`) because gemini-3-flash-agent is a reasoning model and `max_tokens=100` got consumed by hidden reasoning budget. Sonnet 4.5 outputs clean casual-ID first try.
- 9router returns **SSE by default** even when `stream: false` is sent. `_parse_router_response()` handles both JSON and `data: ...` chunked SSE — DON'T assume `json.loads(r.read())` works.
- Per-reply pipeline:
  1. LLM gen with `temperature=1.1`, `max_tokens=400` (must be generous for non-streaming SSE)
  2. Strip wrapper quotes, ensure URL present, add emoji from 20-pool if missing
  3. 30% chance: substitute one common Indo full word with its shortform (`yang→yg`, `banget→bgt`, `enggak→gak`, etc.)
  4. Cosine-style word-overlap dedup vs last 50 replies (`reply_history.json`), threshold 0.7
  5. If too similar, retry once with `temperature=1.3`
  6. Fallback to template randomization if LLM fails
- Reads history from `~/.hermes/scripts/reply_history.json` (orchestrator owns the write side)

## Module 3 — `threads_cross_verify.py`

Solves the v9 false-positive verifier: post-strike Threads/Meta render reply in own session DOM (so reload check passes) but discard server-side (invisible to public).

- `verify_reply_visible(post_url, username="jagonya_shopee")`:
  - Uses Camoufox CLI subprocess against `chrome_local_102130715962900495` (syadagentic-main)
  - Real Chrome bypasses Playwright fingerprint detection — `threads.com` returns 404 to Playwright headless but 200 to real Chrome
  - **`get text` requires an element index** — use `get markdown` to dump the whole page
  - Returns `{visible: bool, method: "browseract", details: "username_count=N, text_len=M"}`
- `register_check(post_url, visible)`:
  - Increments `consecutive_shadowbans` on `visible=False`, resets to 0 on `True`
  - When counter reaches `SHADOWBAN_THRESHOLD = 2`, runs `hermes cron pause 67a687f2978a` automatically and resets counter
- Persistent Camoufox session pattern: `_get_session()` opens once per orchestrator run and reuses for every cross-check, saving ~15s per verify after the first call. Call `close_session()` at orchestrator exit.

## Orchestrator integration (threads_reply_v6.py)

Patch points:
1. `main()` opens with `should_act_now()` gate — exits immediately if sleep/cooldown
2. `get_comment(product, url, op_text="")` imports `threads_content_gen.generate_reply` with template fallback
3. After paste, delay is `hb.human_delay("before_post")` (was fixed 10s)
4. Verification sequence: own-session reload → cross-account Camoufox → only THEN count as replied
5. On hard shadowban + `triggered_pause=True`: call `browser.close()` and `return` to exit the entire run (NOT `continue` — that wastes 60–90s per follow-up attempt)
6. After successful reply: `hb.register_action()` + `hb.human_delay("between_replies")` + re-check gate

## Camoufox profile is ANONYMOUS for Threads (durable fact)

`chrome_local_102130715962900495` profile does NOT have a Threads session by default. It can BROWSE threads.com/threads.net (real Chrome bypasses anti-bot), but Threads renders it as logged-out — only public explore feed visible, target accounts (jagonya_shopee feed) inaccessible from this profile.

Direct cookie injection from `~/instagram_cookies.json` does NOT establish a Threads session: Threads requires the SSO bridge flow (`instagram.com` → "Continue with Instagram" button → token exchange → `threads.com` session cookies set server-side). Injecting only Instagram `sessionid`/`csrftoken`/`ds_user_id` to `.threads.net` / `.threads.com` domain leaves the page in anonymous-viewer state.

**Implication**: Camoufox is excellent as the ANONYMOUS cross-account verifier (exactly its job in v10) but cannot be used as the REPLY-SENDING client. Playwright headless with the SSO bridge stays the canonical reply-sender for now.

## Auto-pause behaviour (verified 2026-06-30)

`SHADOWBAN_THRESHOLD = 2` produces this pattern when account is hard-blocked:
- Reply 1 → 200 OK → own-reload visible → cross-check `visible=False` → counter=1
- Reply 2 → 200 OK → own-reload visible → cross-check `visible=False` → counter=2 → trigger `hermes cron pause 67a687f2978a` → counter reset → orchestrator `return`
- Total wasted time: ~3–5 min before auto-shutdown
- Next cron tick: still paused, skipped

Threshold was 3 in initial build, reduced to 2 because each verify costs ~25–30s (first call) + ~12s (subsequent). 2-strike threshold cuts total wasted run from 9+ min to 3–5 min.

## Run-time budget per attempt (SYADAGENTIC context, 2026-06-30)

| Phase | Time |
|-------|------|
| Threads page navigate | 6–8s |
| Editor open + paste | 2–3s |
| Human review delay (log-normal `before_post`) | 4–15s |
| Post submit + API watch | 8s |
| DOM reload verify | 8s |
| Camoufox cross-check (first) | 25–30s |
| Camoufox cross-check (subsequent) | 10–15s |
| Inter-reply sleep (log-normal `between_replies`) | 5–90s |
| **Total per attempt** | **60–120s** |

Don't waste a user's attention polling a background run every 60s. Either redirect output (`> /tmp/threads_reply_live.log 2>&1`) and tail on demand, or use a single longer wait. Five `process(wait, timeout=60)` calls in a row reading "still running" is exactly what SYADAGENTIC calls out as "kok lama".

## Strike → shadowban timeline (jagonya_shopee, 2026-06-30)

- T+0  (28 Jun ~21:00 WIB): post removed for "nudity/sexual activity" (false-positive on Wardah Hair Serum caption)
- T+0  to T+48h: every reply hard-discarded server-side. Account profile itself remains public (own posts continue to render), but comments to OTHER users' posts never appear cross-account.
- T+72h: typical earliest visibility return per past observations
- T+96h–168h: safe full resume

Verify recovery before resuming cron:
```bash
python3 ~/.hermes/scripts/threads_cross_verify.py "https://www.threads.net/@<some_random_user>/post/<id>"
```
Run after manually leaving a real reply from SYADAGENTIC's phone — if the standalone verifier reports `visible=True` for that post, shadowban has lifted; safe to `hermes cron resume 67a687f2978a`.

## Cron job

- ID: `67a687f2978a` ("Threads Reply v8 — CDP Script Auto")
- Schedule: `every 240m`
- State managed by `register_check()` — script auto-pauses; resume is manual after SYADAGENTIC confirms shadowban lifted via `threads_cross_verify.py` probe.

## Common pitfalls (this build)

1. **Playwright `_get_session` global without cleanup** — first build leaked Chrome sessions across runs. Always call `close_session()` in finally / on exit, OR open a fresh session per run for orchestrator stability. (Persistent within-run is fine; persistent across-runs leaks.)
2. **`camoufox get text` requires element index** — use `get markdown` for full page dumps.
3. **Reasoning models in 9router** (`ag/gemini-3-flash-agent`, `ag/gpt-oss-120b-medium`, anything with `-thinking` suffix) leak think tokens into output AND consume the `max_tokens` budget on hidden reasoning. Stick to `kr/claude-sonnet-4.5` or `kr/claude-opus-4.7` for content generation. Use `ag/gemini-3-flash-agent` only for fast agentic flow control with structured output, not raw text gen.
4. **9router returns SSE even when `stream: false`** — write a parser that handles both JSON and `data: …` chunked stream from the start.
5. **Camoufox profile anonymous viewer** — see section above. Don't try to "fix" by injecting Instagram cookies to `.threads.com`; the SSO exchange has to happen via the bridge flow.
