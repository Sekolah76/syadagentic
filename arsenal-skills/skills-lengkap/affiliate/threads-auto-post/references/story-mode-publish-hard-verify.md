# Story Mode — Publish Hard-Verify (2026-07-12)

## Canonical paths
- Executor: `~/.hermes/scripts/threads_post_v6.py` (restore from skill if missing)
- Content orchestrator: `~/.hermes/scripts/cron_post.py` (v5 story mode)
- Story engine: `~/.hermes/scripts/threads_story_engine.py`
- Dry-run (no browser): `~/.hermes/scripts/threads_story_dry_run.py N`
- **History ONLY:** `~/.hermes/scripts/threads_post_history.json`
  - NEVER skill-dir history (diverges silently)
- Affiliate DB primary: `~/.hermes/skills/affiliate/threads-auto-post/references/affiliate-link-database.md`
  - Sync copies after mark USED

## Account / cookie gate
- Live post account: **`jagonya_shopee`** (`ds_user_id` must match live session)
- Chrome **Profile 16** is source of truth for cookies
- Cookie files:
  - `~/instagram_cookies.json` (required, must include `sessionid`)
  - `~/threads_cookies.json` (optional but preferred after SSO)
- Inject multi-domain: `.instagram.com` + `.threads.com` (+ `.threads.net` if needed)
- Extractor: `~/.hermes/scripts/extract_threads_cookies.py` → **force Profile 16 Cookies DB**
- Preflight: if UI shows **Sign up to post** / SSO wall → STOP, re-login jagonya on P16, re-extract cookies. Do not unpause cron.

## Anti-dup stack (mandatory)
1. DB status `❌ UNUSED` only
2. History `affiliate_link` set → reject forever (window = full history file)
3. Category LRU rotation (4-way)
4. `story_type` ≠ last **3**
5. Hook phrasing overlap ≤ **55%** vs last **8**
6. `check_dedup()` hard-fail in `threads_post_v6` before send
7. **Mark USED only after hard success** (returncode 0 + mutation/profile verify)

## Hard success definition (CRITICAL)
Clicking **Kirim/Post** is **NOT** success.

Success ONLY if either:
- Network capture shows GraphQL friendly name matching: `Create|Publish|PostMedia|TextPost|Configure`
- OR profile page text contains hook / product / affiliate id

On failure:
- `status=failed`, **do not** append history
- **do not** mark USED
- exit non-zero so `cron_post` does not sync DB

False-success pattern seen 2026-07-12:
- 3 editors filled, link confirmed in editor, `Send clicked!`
- Profile verify soft-warned “may need time”
- History written + USED marked
- Reality: **zero create mutation**, post never appeared → must revert

## Playwright pitfalls
- `el.click is not a function` → target is often a text node/span. Use `closest('div[role=button],button,a')` + `MouseEvent` fallback (`safeClick`).
- `[contenteditable=true]` can exist but be **not visible** → `force=True` click / JS `focus()` / prefer `:visible`.
- Prefer leaf **Kirim** with role=button; header Kirim (~y≈96) over feed “Posting ulang/Bagikan”.
- `cron_post.py` main body must sit under `if __name__ == "__main__"` so dry-run imports do not launch browser.

## Pre-unpause checklist
1. `python threads_story_dry_run.py 12` → unique links + story rotation + no adjacent same cat/story
2. Cookie extract Profile 16 → user=`jagonya_shopee`
3. Manual/test post 1x with hard-verify
4. Only then unpause: post `23199a7b2d5b`, reply `67a687f2978a`, cookie `f1902736896e`
5. All cron: `no_agent: true`, deliver `telegram:-1003929065825`

## Residual publish blocker (session note)
Threads web composer can accept typed 3-beat content and show Kirim, yet fire **only** composer query GraphQL (no Create mutation). Treat as blocked publish path — fix send path / alternate client before unpause. Do not soft-succeed.

## Content format (story 3-beat)
- P1: scene/hook, **no product URL**
- P2: twist/result, soft product name ok
- P3: soft CTA + **only** `s.shopee.co.id` link
- 6 types × 4 cats: `keresahan_malam|malu_sosial|salah_beli|teman_bukti|open_loop|regret` × skincare/parfum/haircare/makeup
