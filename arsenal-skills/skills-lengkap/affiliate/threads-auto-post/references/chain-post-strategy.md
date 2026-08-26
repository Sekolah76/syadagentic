# Chain Post / Series Content Strategy (v5 — Planned 2026-06-23)

## Concept
Instead of standalone 3-post threads, create **connected series** where multiple threads tell a continuing story.

## Constraints
- **Threads hard limit: 3 posts per thread** (verified 2026-06-11)
- So "chain" = multiple separate threads that connect thematically

## Chain Structure (3 threads = 9 posts total)
```
Thread 1 (Series Part 1):
  [1] Hook — masalah/keresahan (pure story, no product)
  [2] Deepening — detail masalah, relatable experience
  [3] Cliffhanger — "dan ternyata solusinya simpel banget..." (NO link)

Thread 2 (Series Part 2):
  [1] Continuation — "lanjutan dari kemarin..."
  [2] Value/insight — tips, edukasi, discovery
  [3] Teaser — "yang gw pake ada di post selanjutnya ya 🫣" (NO link)

Thread 3 (Series Part 3 — FINAL):
  [1] Reveal — "akhirnya gw share..."
  [2] Honest review — 2-3 sentences, no brand push
  [3] Soft CTA + affiliate link — "yang mau coba, link di bawah 🫶"
```

## Series Tracker (needed for v5)
```json
{
  "series_id": "skincare_jerawat_2026-06-23",
  "part": 1,
  "total_parts": 3,
  "category": "skincare",
  "hook_theme": "struggle jerawat 3 tahun",
  "threads_urls": [],
  "status": "in_progress"
}
```

## Implementation Notes
- Store series state in `~/.hermes/scripts/threads_series_tracker.json`
- Cron needs to check: is there an ongoing series? If yes, continue it.
- If no series active, start a new one (pick category + theme)
- Series completes after part 3 → start fresh series
- Each part = separate cron run (3x/day schedule handles this naturally)

## Soft Selling in Chain Posts
- Parts 1-2: ZERO product mention. Pure value/story/education.
- Part 3: Minimal reveal + soft CTA. Friend sharing, not seller pushing.
- "yang mau coba, link ada di bawah 🫶" style — NOT "BELI SEKARANG"

## Pending Confirmation (2026-06-23)
Awaiting SYADAGENTIC clarification on:
- Option A: 3 separate threads (9 posts) per series
- Option B: Just better-connected standalone 3-post threads
- Image generation: per thread or per series?
