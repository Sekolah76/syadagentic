# Threads Auto-Reply Intent Router v12 (Nimbrung/Sok Asik)

## 1. Dual Funnel Search
- **Reco (40%)**: Kueri eksplisit meminta rekomendasi (misal: "rekomendasi skincare jerawat", "parfum tahan lama").
- **Nimbrung (60%)**: Kueri bercerita/curhat/random (misal: "muka kusam banget hari ini", "wangi seharian", "skincare journey").

## 2. Intent Classifier & Link Policy
Analisis isi postingan OP untuk menentukan mode dan penempelan link:
- **reco**: OP meminta rekomendasi produk → **Link ALWAYS (100%)**.
- **relate**: OP sedang mengeluh/curhat masalah kulit/rambut/parfum → **Link SOFT (50%)**.
- **story**: OP berbagi journey / before-after → **Link SOFT (45%)**.
- **banter**: OP sedang bercanda/meme/flexing wangi → **Link OFF (25% / default no-link)**.
- **light**: Postingan random → **Link OFF (15% / no-link)**.

## 3. Safe Ratio & Anti-Spam
- **≥50% No-Link Floor**: Jika rasio reply ber-link di history 20 putaran terakhir melebihi 50%, non-reco reply berikutnya dipaksa **tanpa link** demi menjaga akun terlihat natural (sok asik, bukan spam bot).
- **Anti-Spam Skip**: Jika postingan OP sudah berisi link affiliate lain, link di bio, atau bernada spam seller, lewati (`skip`).
- **Generasi Content**: `threads_content_gen.py` membagi tone generator sesuai mode di atas. Jika LLM gagal/body terlalu pendek (<8 karakter), gunakan fallback templates spesifik per mode.

## 4. Isolated Pool + Auto-Advance (v19)
- DB: `~/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md`
- Used-set: `~/.hermes/scripts/threads_reply_used_links.json`
- **No cross-sync** with Threads Post or Pinterest.
- On cron start: `affiliate_batch_manager.ensure_pool_has_unused("threads_reply")`.
- When effective UNUSED=0 → archive → load next `batches/batch-NNN.md` with fresh links only.
- Mark USED only after successful reply via `mark_reply_link_used()`.
