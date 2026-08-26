# Threads Publish Hard Gate & LIVE BLOCK (2026-07-12 → 2026-07-13)

## Status snapshot (audit 2026-07-13)
| Layer | Status |
|-------|--------|
| Content / Story Mode | SIAP (dry-run 12/12) |
| DB unused | ~85 links |
| History | `~/.hermes/scripts/threads_post_history.json` only |
| Cookie | `ds_user_id=3310347890` (@jagonya_shopee) |
| Cron post `23199a7b2d5b` | **PAUSED** since 2026-07-05 |
| Cookie cron `f1902736896e` | **PAUSED** |
| Publish layer | **BLOCKED** — Create GraphQL mutation = 0 |

Last **trusted** cron success: `2026-07-04 20:02` (Charis Touch Parfum).  
Manual debug 2026-07-12: type/paste OK, **Kirim no-op**, mutation false.

## Root cause class
```text
Composer fill OK (3-beat + link)
  → click Kirim / Post
  → Barcelona Create mutation NOT fired
  → profile may still show old text → false "verified"
```

Evidence files (session):
- `/tmp/threads_cdp_post_result.json` → `create.mutation=false`, `verified=false`
- `/tmp/threads_applescript_result.json` → `res=""`, hook/link hits false on profile
- `/tmp/threads_post_pospath_test.log` → Kirim scored y=835 x=1195, still no mutation
- Memory lock: *LIVE BLOCK 2026-07-12: type/paste OK, Create/Publish mutation=0*

## Hard success gate (LAW)
Success **only** if **one** of:
1. **Create GraphQL mutation** captured (name/status present), **OR**
2. Profile hard verify: **hook snip AND product snip AND link_tail** all true on **fresh** profile post (not soft partial match)

**Do NOT**:
- Mark `USED` / append history on soft profile-only match
- Trust product-name alone (can match old UI / prior posts)
- Unpause cron until **1 live hard-success** with mutation or triple snip

## Kirim click preference (AppleScript / CDP)
From SYADAGENTIC memory + pos-path tests:
- Prefer **Kirim** with **y>300 and x>700** (composer bottom-right)
- Never click top-bar Post/Kirim first (low score, often no-op)
- Headless + CDP both hit mutation=0 historically — headed / Profile 16 path may still be required for real publish

## Cron plumbing
```text
run_threads_post.sh
  → cron_post.py v5 (story + unused pick + review photo)
    → threads_post_v6.py (Playwright cookies)
```
- Account: **jagonya_shopee** ds `3310347890` (not olivia `46398254032`)
- History ONLY: `~/.hermes/scripts/threads_post_history.json`
- Wrapper success grep must not accept soft `✅` without hard proof

## Fix order (when SYADAGENTIC resumes)
1. Resume / refresh cookies (`extract_threads_cookies.py`) — login valid
2. Harden gate in `threads_post_v6.py` (mutation OR triple snip)
3. Fix publish path (headed / correct Kirim coords / non-no-op send)
4. One manual live hard-success
5. Only then unpause `23199a7b2d5b` (+ cookie cron)

## Content layer still good
- Story engine + category rotation + anti-dup OK
- Do not rebuild content while publish is the blocker
