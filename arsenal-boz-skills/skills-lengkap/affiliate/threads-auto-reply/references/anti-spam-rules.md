# Threads Auto-Reply Safety Rules & Anti-Spam (v9.0)

Due to aggressive spam filters on Threads (verified 2026-06-23: account received community standards moderation notice for high-volume automated actions/spam), the following rules are MANDATORY for the auto-reply system:

## 1. Safety & Posting Delay
- **Action:** Before hitting "Post" or "Kirim", simulate a realistic typing pause.
- **Implementation:** `time.sleep(random.randint(15, 30))` after entering the text inside the editor dialog.
- **Goal:** Avoid instant automation triggers.

## 2. Cron Schedule Constraints
- **Action:** Stagger cron runs to prevent high-volume warnings.
- **Rule:** Set the cron schedule to a minimum of 4 hours (`every 4h`) or up to 24 hours (`every 24h`).
- **Trigger Limit:** Maximum 1 target post reply per run.

## 3. Post Selection (Keywords)
- Avoid robotic terms like `"butuh rekomendasi skincare"`.
- Use problem-focused organic keywords:
  - Skincare: `"jerawat parah banget"`, `"muka break out"`, `"skin barrier rusak"`
  - Makeup: `"makeup crack banget"`, `"cushion buat pemula"`, `"rekomendasi lip tint"`
  - Haircare: `"rambut rontok parah"`, `"ketombe ga ilang ilang"`
  - Parfum: `"parfum tahan lama murah"`, `"rekomendasi parfum cowok"`
