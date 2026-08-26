# Story Mode + Dedup + no_agent (2026-07-12)

## Canonical scripts (runtime)
| Role | Path |
|---|---|
| Story engine | `~/.hermes/scripts/threads_story_engine.py` |
| Pipeline | `~/.hermes/scripts/cron_post.py` (main guarded `if __name__`) |
| Publisher | `~/.hermes/scripts/threads_post_v6.py` |
| Wrapper cron | `~/.hermes/scripts/run_threads_post.sh` (Hermes venv) |
| Dry-run | `~/.hermes/scripts/threads_story_dry_run.py` |
| History | `~/.hermes/scripts/threads_post_history.json` **ONLY** |

Skill `scripts/` = backup/canonical copy. Runtime missing `threads_post_v6.py` → copy from skill.

## Cron (all no_agent)
| Job | ID | Script | State rule |
|---|---|---|---|
| Post | `23199a7b2d5b` | `run_threads_post.sh` | pause until auth+story tests pass |
| Reply | `67a687f2978a` | `run_threads_reply_v11.sh` | same |
| Cookie | `f1902736896e` | `extract_threads_cookies.py` | same |

Never unpause post/reply without SYADAGENTIC command after live preflight.

## Anti-duplicate stack (hard)
1. DB row must be `❌ UNUSED`
2. Link ∉ history `affiliate_link` set (forever in window)
3. Category LRU across last ~8 posts
4. Story type ≠ last **3** (`story_type` / `hook_category`)
5. Hook phrasing: word overlap ≤ **55%** vs last **8** hooks (60-char window)
6. Executor `check_dedup` hard-fails before browser send
7. `mark_link_used()` + `sync_all_db_copies()` **only if** publisher returncode == 0
8. Auto-reset USED→UNUSED when pool empty, still respect history link set

## Dry-run before unpause
```bash
/Users/user/.hermes/hermes-agent/venv/bin/python3 \
  ~/.hermes/scripts/threads_story_dry_run.py 12
```
Pass criteria: unique links 12/12, unique hooks 12/12, adjacent same story = 0, no URL in post1/2, link in post3.

## Story content asserts
- post_1 / post_2: no `http`
- post_3: contains `s.shopee.co.id/...`
- `content_mode=story_v1`, `hook_category` = story type

## Pitfalls fixed 2026-07-12
- History path under skill dir → empty/diverged; force `~/.hermes/scripts/threads_post_history.json`
- `cron_post.py` top-level main ran on import → broke dry-run; wrap `main()`
- Missing runtime publisher → restore from skill scripts
- DB not marked USED after success → double-pick risk; mark only on success
- Content layer PASS ≠ live publish PASS — auth preflight separate (`references/auth-preflight-jagonya.md`)
