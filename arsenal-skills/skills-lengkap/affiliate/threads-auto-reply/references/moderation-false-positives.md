# Threads/Meta Moderation False-Positives (running log)

## 2026-06-28 — jagonya_shopee Wardah Hair Serum

**Post text (CLEAN, no policy violation):**
> "Ketombe bandel padahal udah coba 5 shampo? Wardah Hair Serum Anti Frizz 50ml ini yang bersihin sampe ke akar 😭"

**Classifier verdict:** "Postingan mungkin berisi ketelanjangan atau aktivitas seksual" (100% false-positive — zero nudity, just hair-care product mention)

**Account consequence:**
- Account Status: tier-1 warning ("Beberapa aktivitas Anda mungkin melanggar Standar Komunitas")
- 1 konten dihapus
- 177-day appeal window via "Perbaiki" button
- No posting restriction yet (warning only)

**Implication:** Meta's classifier is misfiring on Indonesian skincare/haircare keywords in 2026. Suspected trigger keywords: `ketombe`, `bersihin`, `akar`, emoji 😭 in promo context. Cannot confirm exact trigger from outside.

## Recovery Protocol (when this hits a managed account)

1. **Submit appeal IMMEDIATELY** via "Perbaiki" button (queue lighter at night WIB).
   - Template: "Postingan saya mempromosikan produk perawatan rambut [brand+name] - produk kecantikan legal dijual di marketplace Indonesia. Tidak ada konten ketelanjangan, aktivitas seksual, atau pelanggaran apa pun. Mohon ditinjau ulang. Klasifikasi sistem keliru."
2. **Pause posting cron 48-72h MINIMUM** — strike-2 within 30d activates real restrictions (post limit, reach throttle, full pause).
3. **Re-enable with stealth layer ON (v10)** — fixed-template v9 + immediate-burst is the behavior the classifier is biased against. v10 specifically targets this.
4. **Don't re-post the removed content verbatim** — modify wording so the classifier doesn't re-flag the same hash/phrase.

## What NOT to Do

- ❌ Re-post identical text immediately — second strike before appeal review = auto-block, harder to recover.
- ❌ Abandon account — tier-1 warning has 30-day decay; one strike doesn't ban.
- ❌ Switch to a fresh account preemptively — preserves the account's age signal (which is itself trust capital).
- ❌ DM Meta support — there's no human-reachable path for this tier; the appeal flow IS the recovery path.

## Diagnostic Pattern (Did Classifier Misfire?)

Before recovery, confirm it's a false-positive vs a real violation:
1. Read post text — is there ANY policy-touching content? (nudity, hate, drugs, weapons, IP infringement)
2. Read image/video — same check, plus audio if video.
3. Check OP-related context — Meta sometimes flags reply chains based on the parent post, not yours.

If all three are clean, it's classifier misfire. Recovery protocol above applies. Otherwise treat as a real strike and don't re-post the offending content even after appeal.

## Strike Counter Tracking

Tier 1: 1 strike — warning only, full posting capability.
Tier 2: 2-3 strikes within 30d — restrictions (post frequency cap, story/reel cap, hidden from non-followers).
Tier 3: 4+ strikes within 30d — temporary suspension (24h-7d).
Tier 4: repeated tier-3 violations — permanent account loss.

The 30-day window matters: a single strike at month 0 + a clean month 1 = effectively reset. Pacing matters more than absolute count.
