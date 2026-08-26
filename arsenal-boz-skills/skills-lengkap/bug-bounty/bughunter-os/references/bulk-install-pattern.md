# Bulk Skill Install — Indexer + Router Pattern

When a user delivers a skill as multiple zips (e.g. 8 phase packs + 3 attack pattern libraries = 11 zips, 222+ files), naive installation creates a "library dump" the agent can't navigate. The INDEX + auto-router pattern makes it queryable without loading 347 files into context.

## When this matters

- Total file count > 50 — too many to load into context even partially
- Files are organized in batches (Pack A/B/C/D, phase 1-8, etc.) with overlap and hierarchy
- User's question is "I want to start an audit" not "I want file X"
- Skill is reference material, not a single-execution tool

## The pattern (3 components)

### 1. **Consolidated `SKILL.md`** — class-level entry point

Tells the agent what's inside (5 pillars / 8 phases / 142 patterns, etc.) and when to use it. Should fit the standard peer-matched shape (Overview, When to Use, body, Pitfalls, Verification).

### 2. **`INDEX.md`** — hand-curated question → file path map

```markdown
## "I'm starting a new audit"
1. → orchestrator-batch1/repository_classifier.md
2. → orchestrator-batch1/protocol_detector.md
...

## "I'm hunting reentrancy"
- attack-patterns-batch1-common/reentrancy.md
- exploit-kb-batch1/curve.md (real-world example)
- bughunter-phase5/reentrancy.md
```

Why hand-curated, not auto-generated? Because the natural question a user asks ("how do I audit an AMM?") is not the same as the directory layout. INDEX.md bridges that gap.

### 3. **`_router.py`** — fuzzy free-text query CLI

```python
KEYWORD_MAP = {
    'reentrancy': ['reentrancy', 'curve.md', '...'],
    'oracle': ['oracle', 'Oracle/'],
    # 50+ entries
}

def route_query(query, files_data):
    matches = []
    for kw, patterns in KEYWORD_MAP.items():
        if kw in query.lower():
            for f in files_data:
                # score: 10 (match) + 5 (title) + 3 (path)
                ...
    return sorted(matches, reverse=True)[:15]
```

Usage:
```bash
python3 _router.py "reentrancy"   # → 11 files, top hits: reentrancy.md
python3 _router.py "build PoC"    # → exploit_builder, poc_builder
python3 _router.py --interactive
```

## Generation recipe

When you receive N zips and need to assemble one mega-skill:

1. **Extract all to a staging dir** (`/tmp/skillpack/`)
2. **Normalize names** — strip hash prefixes, lower-case, kebab-case the subdirs
3. **Copy to `~/.hermes/skills/<name>/<normalized-subdir>/`**
4. **Generate INDEX.md** — scan all files, group by category, surface common questions
5. **Generate _router.py** — keyword → file path map based on common bug/protocol/exploit terms
6. **Patch SKILL.md** to add a "Navigation" section pointing to both

## When NOT to use this pattern

- Skill has <30 files — direct grep through SKILL.md is faster
- Skill is procedural (one workflow, one file) — no need for navigation
- Files are flat with no subdirs — INDEX.md can be in SKILL.md itself

## Lessons from bughunter-os install (2026-07-18)

- The user delivered 11 zips, then 10 more, then 2 duplicates for v1.0 final. Build to handle N zips with idempotent install (dedup by content, not name).
- User explicitly asked for INDEX + auto-router as optimization step AFTER the install. This is the right ordering — install first, then optimize, not over-engineer upfront.
- The `bughunter-os` skill at 347 files was the trigger. Below 100 files, INDEX.md alone is enough. Above 100, the auto-router earns its keep.
- Generated INDEX.md should be at most ~30k chars (584 lines worked well). Going past 50k means the index is becoming its own problem.
- The router's keyword map is the highest-leverage artifact — 50 keywords mapped to file globs covers ~90% of natural queries. Expand only when a query fails to route.
- Don't try to make the router exhaustive. It supplements INDEX.md, not replaces it.

## Pitfalls

- **Don't auto-generate INDEX.md from filenames only** — the structure is directories, but the natural questions are cross-cutting (e.g. "reentrancy" appears in 3 categories). Hand-curate the question → file map.
- **Don't put all 50+ keywords inline in SKILL.md** — they rot. Keep them in the router's `KEYWORD_MAP` and let the script be the source of truth.
- **Don't make the router "smart" with NLP** — keyword match + path match is enough. LLMs in the calling agent do the semantic lifting; the router just disambiguates paths.
- **Forgetting the `SKILL.md` patch** — if you only generate INDEX.md and _router.py, the agent still loads the bare SKILL.md and doesn't know navigation exists. Always patch the umbrella's SKILL.md to point at both.

## Sandbox state-loss gotcha in `execute_code`

`execute_code` runs the whole script in a fresh sandbox each call — **module-level variables don't persist between calls**. If you build INDEX.md in two passes (e.g. one `execute_code` to scan files, another to write the index), variables like `index_path`, `files_data`, `category_groups` will be `NameError` in the second call even though they were defined in the first.

Symptom you hit it:

```
NameError: name 'index_path' is not defined
```

But you literally defined it in the previous call. It's not gone — it was thrown away when the previous sandbox exited.

**Fix**: do scan + build + write in a single `execute_code` call. Example skeleton:

```python
import os, re
from collections import defaultdict

skill_dir = "/home/ubuntu/.hermes/skills/<name>"
index_path = os.path.join(skill_dir, "INDEX.md")

# 1. Scan (collect everything in memory)
files_data = []
for root, dirs, files in os.walk(skill_dir):
    ...

# 2. Build content (pure string assembly, no external I/O)
lines = ["---\nname: ...\n---\n", ...]

# 3. Write (single I/O at the end)
with open(index_path, "w") as f:
    f.write("\n".join(lines))
```

If you must split work across calls, **persist intermediate state to disk** (write a JSON or tmp file), then load it in the next call. But for any single artifact < 50k chars, doing it in one call is simpler.

**Same gotcha applies to**: `_router.py` generation, the sherlock submission script, the SWEEP tool, and any other multi-step build. Whenever you write code, ask: "am I relying on a variable defined in a previous `execute_code` call?" If yes, combine the calls or persist to disk.

## Auto-Router's keyword-map heuristic

When you can't think of all 50+ keywords upfront, here's the priority order to grow the map:

1. **Vulnerability class names** (reentrancy, oracle, sandwich, signature_replay) — 10-15 entries
2. **Protocol type names** (amm, lending, bridge, liquid_staking, vault) — 10-15 entries
3. **Process verbs** (audit, phase N, report, poc, severity) — 5-10 entries
4. **Real exploit names** (wormhole, ronin, nomad, curve, beanstalk) — 10-15 entries
5. **Specific token standards** (erc20, erc4626, erc721) — 5 entries

Each entry's value is a list of path-globs and substring patterns. Use `in` substring match (not regex) — fast, predictable, debuggable.

Don't optimize for coverage. Optimize for the natural questions a beginner hunter would ask. Anything fancier is over-engineering.

## When the user asks for the file (not a gist, not a paste)

When delivering a `.md` PoC or report file, you have three channels:

1. **Save to local file** + tell user the path (best if same machine)
2. **`MEDIA:/path/to/file.md`** annotation (best for Telegram-style delivery, gets attached as a file)
3. **Paste full content inline** in chat (best for short files, <200 lines)

User has explicitly rejected:
- GitHub Gist as a download mechanism ("ngapain bikin gist, kan udah lu kirim tadi filenya")
- Repeatedly pasting the same content in chat after they've already seen it
- Generated IPFS / 0x0.st links when local file works

The principle: **deliver the file through whatever channel they're already using**. Don't introduce new infrastructure mid-conversation.
