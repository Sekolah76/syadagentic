# Threads Post Caption Style — Viewbait v4 (2026-07-16)

## SYADAGENTIC preferences (hard)
- Call operator **SYADAGENTIC** only.
- Post 1 must be **long**: target **160–230+ chars** (multi-sentence). Short hooks ~80–120 = too short, rewrite.
- **Partial ALL CAPS** on opening clause of post 1 (stop-scroll), body continues normal case.
- Tone: Gen-Z **sarkas / ragebait tipis / validasi emosi** — not soft lempeng.
- Emoji: sinis/stres (`💀` `🫠` `😭` `🤯` `🔥`) sparingly, not cute spam.

## Structure (3-beat hard max)
1. **Post 1 (hook):** CAPS open + pain/myth/regret/story setup, **no URL**, no hard product name on pure cerita mode.
2. **Post 2 (body):** detail timeframe / texture / result / comparison + soft product bridge optional.
3. **Post 3:** soft CTA + save + affiliate link + engage Q (debat/kubu better than bland "tim A atau B?").

## Engine file
- `~/.hermes/scripts/threads_content_engine.py` — `CERITA_P1` / `TIPS_P1` banks.
- `hook_text` for history/dedup stores **first 160 chars** of post1 (not 80).
- Assert in self-test: `len(post_1) >= 160` preferred; never ship templates under ~150 if avoidable.

## Example good post1 (skincare myth)
```
MYTH: SKINCARE HARUS 10 STEP BIAR GLOWING. realitanya kulit lo malah stres,
kemerahan, bruntusan. perbaiki barrier dulu baru mimpi glowing. 3–4 step pas
+ rutin sering lebih ngena daripada rak penuh botol 💀
```

## Anti-patterns
- One short sentence + emoji as entire post1.
- Soft seller voice ("coba deh… underrated banget…").
- Product name + link on post1.
- Recycling near-identical hooks (overlap >0.55 vs last 12 history hooks).
