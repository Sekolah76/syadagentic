# Threads Post Viewbait v5 + Cron Timeout Fix (2026-07-20)

## HARD RULES (operator SYADAGENTIC)

1. **Image (mandatory):** scrape Shopee **buyer review 5★ + media HD only** (not product gallery/catalog). If Shopee returns 0 media → **Pinterest fallback** (`download_pinterest_review_photo`). Text-only only after both fail.
2. **Post 1 caption:**
   - **Baris 1 = ALL CAPS** (hook stop-scroll)
   - **Total length ≥ 210 chars** (`MIN_P1_LEN = 210` in `threads_content_engine.py`)
   - Enforced by `_format_post1()` (split first sentence → upper hook → pad with category fragments)
3. **Tone:** ragebait/sarkas Gen-Z (not soft honest lempeng). Soft product drop on post 2; CTA+link+engage Q on post 3.
4. **Dedup:** 1 affiliate link = 1 post forever. Mark USED only after real publish success.

## Key files

| File | Role |
|------|------|
| `~/.hermes/scripts/cron_post.py` | Orchestrator: pick link → content → image → publish |
| `~/.hermes/scripts/threads_content_engine.py` | CERITA/TIPS templates + `_format_post1` (CAPS + ≥210) |
| `~/.hermes/scripts/shopee_scraper.py` | 5★ + media review scrape (aggressive selectors/scroll) |
| `~/.hermes/scripts/threads_post_http.py` | Browserless HTTP primary (rupload + `configure_text_post_app_feed`) |
| `~/.hermes/scripts/run_threads_post.sh` | Cron wrapper (`no_agent`), `THREADS_ALLOW_UI_FALLBACK=0` |

## Cron job

- **ID:** `23199a7b2d5b` · name Threads Auto-Post
- **script:** `run_threads_post.sh` · **no_agent: true**
- **schedule:** every 240m
- **deliver:** telegram topic affiliate

## Root cause: "provider timeout" on Threads post (2026-07-20)

**Not** a model/provider timeout. Job is `no_agent: true`.

| Layer | What happened |
|-------|----------------|
| Cron config | `cron.script_timeout_seconds: 300` (too tight) |
| Runtime | Shopee 0 reviews → Pinterest OK → **HTTP failed once** → AppleScript → Playwright P16 → **>300s** |
| Error string | `Script timed out after 300s: run_threads_post.sh` |
| Alert wording | Hermes may surface as "provider timeout" even for script timeout |

**Fix applied:**

1. `hermes config set cron.script_timeout_seconds 900`
2. `cron_post.py` publish path: **HTTP primary + 1 cookie-refresh retry**; UI AS/P16 **OFF unless** `THREADS_ALLOW_UI_FALLBACK=1`
3. `run_threads_post.sh` exports `THREADS_ALLOW_UI_FALLBACK=0`; parse summary without `grep -P` (macOS)
4. Recovery: re-run `threads_post_http.py` on last content → success with image; mark link USED

## Publish engine order (cron-safe)

```
1. threads_post_http.py  (timeout 180s)
2. extract_threads_cookies.py + HTTP retry once
3. UI (AppleScript / P16) ONLY if THREADS_ALLOW_UI_FALLBACK=1
```

Never chain HTTP fail → AS 360s → P16 360s under 300s cron budget.

## Content contract (post-1)

```python
MIN_P1_LEN = 210
post1 = _format_post1(raw, category)  # first line ALL CAPS + pad ≥210
assert len(post1) >= 210
# first sentence upper_ratio >= 0.85
```

History `hook_text` store ≥160 chars for dedup (full post1 longer).

## Image contract

```
get_real_review_photo(link, product)
  → shopee_scraper.scrape_review_image  # 5★ + media, HD strip thumb
  → if empty/invalid: download_pinterest_review_photo
  → else ""
```

HTTP success signal: `create_name=configure_text_post_app_feed` + `has_image: true` + `media_type=1`.

## Pitfalls

- **macOS:** no `grep -P` in wrapper — use python3 parse.
- **Shopee API ratings 403** — camoufox/DOM only for reviews.
- **sessionid POST-ok ≠ follow-list** (unrelated unfollow path).
- **Stale job prompt** may still mention `threads_post_v6` — ignore; executor is `run_threads_post.sh` + `no_agent`.
- **Link USED only after success** — if manual recovery posts, call `mark_link_used` + `sync_all_db_copies`.
- **Alert "provider timeout"** on this job → check `last_error` for `Script timed out` + `/tmp/threads_post_cron_run.log`, not 9Router model chain.

## Verify

```bash
# content rules
python3 -c "from threads_content_engine import build_content_posts, MIN_P1_LEN; ..."
# image
python3 -c "from cron_post import get_real_review_photo; print(get_real_review_photo(link, name))"
# publish
python3 threads_post_http.py /tmp/threads_post_content.json
# cron timeout
grep script_timeout ~/.hermes/config.yaml   # expect 900
```
