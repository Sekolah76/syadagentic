# Camoufox Pivot — The Real Bot-Detection Bypass (2026-06-30)

## TL;DR — Big Finding

Playwright headless Chromium + IG cookie + SSO bridge to threads.com is detected as bot by Meta and silently shadowbans every reply. Camoufox CLI driving real Chrome (BOZ's `chrome_local_102130715962900495` profile) with a one-time manual login is treated as a real user — reply lands visible cross-account.

Stop building stealth on top of Playwright for Threads. The fingerprint gap can't be closed from headless Chromium; pivot to Camoufox + real Chrome session.

## Evidence Trail (this session)

- Built stealth v10 on Playwright (`threads_reply_v6.py` + `threads_human_behavior.py` + `threads_content_gen.py`) — all sophisticated stealth: log-normal delays, burst/sleep windows, per-reply LLM content via 9router, dedup, typo simulation.
- Verifier-side: 8 replies attempted across 2 runs → **0 visible cross-account**. Own-session reload kept reporting "VERIFIED VISIBLE" but Camoufox anonymous viewer always showed `username_count=0`.
- Switched to Camoufox real Chrome with a manual jagonya_shopee login → first reply landed and rendered with full URL preview, `username_count=7` cross-account.

The script wasn't the problem. The transport was.

## Why Playwright Lost

| Layer | Playwright headless | Camoufox + real Chrome |
|---|---|---|
| Chromium build flags | `--headless=new` revealed via JS probes (UA, plugins, GPU vendor) | Real Chrome.app, no flags |
| TLS fingerprint (JA3/JA4) | Playwright/Chromium fingerprint distinguishable | Real Chrome fingerprint |
| WebGL / canvas hash | Default headless renderer | Real GPU, real renderer |
| Cookie source | Imported IG cookies → SSO bridge flow on every run | Persistent session from manual login, no SSO bridge needed |
| Threads server response | Reply submit returns 200 OK, content discarded server-side | Reply persists, visible to logged-out viewers |

Meta classifier appears to gate comment visibility on the *transport stack*, not just account reputation. Even a clean account on Playwright gets silently dropped; a flagged account on real Chrome stays visible.

## Cookie Inject Was a Dead End

Tried injecting `~/instagram_cookies.json` directly to `.threads.com` / `.threads.net` / `.instagram.com` via `camoufox cookies set`. Result: profile page loads but `687 pengikut` link still redirects to `/login` — the page treats the session as anonymous. Threads.com requires a real SSO exchange to produce its own session cookies; you cannot shortcut by injecting the upstream IG cookies. **Solution: one-time manual login in the Camoufox browser, then re-use the session.**

## Working Reply Workflow (Camoufox, manual-login session)

One-time setup (BOZ done 2026-06-30):
```bash
camoufox --session jagonya_login browser open chrome_local_102130715962900495 "https://www.threads.net/" --headed
# BOZ logs in manually with jagonya_shopee credentials in the opened Chrome tab.
# Session persists across runs as long as Threads cookie jar in that profile stays valid.
```

Per-reply loop:
```bash
# 1. Search recent
camoufox --session jagonya_login navigate "https://www.threads.net/search?q=<KEYWORD>&filter=recent"
# 2. Pick non-affiliate post (skip OP posts that already have s.shopee.co.id)
# 3. Navigate target
camoufox --session jagonya_login navigate "<POST_URL>"
# 4. Get state — composer textbox is usually [55], submit svg "Balas" is [62] on a fresh post
camoufox --session jagonya_login state
# 5. Click composer + input text
camoufox --session jagonya_login click 55
camoufox --session jagonya_login input 55 "<reply text>"
# 6. Click the inline "Balas" svg button (NOT a top-level Post button — it's the svg in the composer footer area)
camoufox --session jagonya_login click 62
# 7. Wait + verify
camoufox --session jagonya_login wait stable
```

State indices are stable across similar pages (post-detail view) but always re-fetch after navigation. The composer textbox carries `aria-placeholder="Balas ke <username>..."` — grep for that to find the index reliably.

## Submit-Button Trap

The reply submit button is NOT a `<button>` element. It's an `svg[aria-label="Balas"]` inside the composer footer. From `state` output it shows as `<div role=button>` wrapping that svg. `[62]` in BOZ's session — but DO confirm via grep on `aria-label=Balas` in state, because Threads sometimes adds an extra button (Suka/Posting ulang) and shifts indices.

## URL Preview Detection Works on Camoufox

`input` via Camoufox triggers Threads Lexical editor's URL detection. The shopee link rendered as a preview card on first try — no special handling needed. Old `threads_reply_v6.py` notes about `execCommand('insertText')` NOT triggering URL detection are PLAYWRIGHT-SPECIFIC. Camoufox's input call dispatches the right event sequence.

## Cross-Account Verifier Still Useful

Even on Camoufox, the verifier (`threads_cross_verify.py`) remains useful as a periodic health-check — confirms the session is still posting visible replies vs silently degraded. Set threshold low (2) for fast auto-pause if it ever starts dropping.

## Suggested Next Step: v11 Rewrite

A clean `threads_reply_v11.py` built on Camoufox CLI calls (subprocess) instead of Playwright would be ~150-200 lines vs v6's 374. Reuse stealth modules (`threads_human_behavior.py`, `threads_content_gen.py`); drop SSO login flow entirely; treat the Camoufox session as a long-lived resource. Cross-verify becomes opt-in health probe rather than per-reply gating.

## See Also

- `references/cross-account-verifier.md` — anti-false-positive verification pattern (still valid)
- `references/shadowban-verification.md` — older Playwright-era verification notes (now superseded by Camoufox path for posting; keep for legacy v6 cron)
- Hermes skill `camoufox` — base CLI usage and persistent-session semantics
