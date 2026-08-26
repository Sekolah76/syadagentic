# open-kritt Default Seeded Workflows & Post-Scripts (verified 2026-08-03)

Observed on a fresh `./kritt setup && ./kritt start` — the stack seeds two
workflows and six post-scripts out of the box, no manual creation needed.
Use this map to pick the right `--workflow-id` / `--post-script-id` on first scan.

## Workflows (`GET /api/workflows`)

| id | name | focus | steps |
|----|------|-------|-------|
| 1  | `external-flow-analysis` | Generic web/app/any-lang: map external entrypoints → trace production flows → investigate vulnerabilities | 3 (d0 entrypoint map, d1 flow trace, d2 vuln) |
| 2  | `Cosmos ABCI Panic Halt Review` | Go/Cosmos/CometBFT chains only: enumerate production-reachable ABCI methods → classify panic halts (explicit / arithmetic / nil-pointer / bounds+type) | 5 |

Both are marked `isDefault: true`. `external-flow-analysis` is the safe
default for non-Cosmos targets; workflow 2 is ONLY meaningful for Cosmos SDK
chain codebases (it literally ignores non-ABCI methods).

## Post-scripts (`GET /api/post-scripts`)

| id | name | purpose |
|----|------|---------|
| 1 | Resource exhaustion | classifies memory/resource-exhaustion findings (`_chip_resource_exhaustion`, reliability/scale/impact scores) |
| 2 | Patched since | checks the finding against live origin/main — is it already fixed (`_chip_patched`) |
| 3 | Ease of exploitability | 0–10 practical exploitability score (`_chip_ease_of_exploitability`) |
| 4 | PoC Creator | builds+validates a runnable PoC, emits `git diff` in `_reserved_poc` (runs the PoC, iterates until works) |
| 5 | Report Creator | turns each finding into structured Markdown bug-bounty report in `_reserved_report` |
| 6 | Is Malicious Actor in scope | revalidates finding + checks actor against `extra.bug_bounty_url` program (`_chip_is_in_scope`, `is_valid`) |

Good default combo for a bounty scan: **post-scripts 4 (PoC) + 5 (report) + 2
(patched) + 6 (scope)**. `_reserved_*` fields are the keys to extract from
findings.

Repos are scanned via `repo.kind` = `remote` (GitHub `org/repo`) or `local`
(a folder registered in the UI first — list empty until then; `kind:local`
fails if nothing is registered).
