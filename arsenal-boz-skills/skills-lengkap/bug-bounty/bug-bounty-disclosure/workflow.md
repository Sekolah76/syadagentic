# Workflow — Bug Bounty & Coordinated Disclosure

Pipeline 6 fase dari temuan sampai fix. Sebelum mulai, pastikan **dasar pengetesan sah** (lihat guardrail di SKILL.md).

---

## Fase 0 — Triase temuan

Tujuan: mastiin ini beneran isu keamanan, bukan noise.

- Klasifikasi kelas bug → `references/vuln-classes.md` (web/API/infra/cloud, smart contract/web3, agent/LLM).
- Tentuin **security boundary** apa yang dilanggar: siapa harusnya ga bisa ngapain, tapi bisa.
- Buang yang bukan bug: behavior by-design, out-of-scope, duplikat known-issue, self-XSS tanpa impact, dsb.

Output: satu kalimat jelas — "X bisa Y padahal harusnya nggak, karena Z".

---

## Fase 1 — Verifikasi & PoC

Ini yang misahin report beneran vs AI-slop.

- **Reproduksi ≥3×.** Kalau non-deterministik, catat rate-nya.
- **PoC minimal & non-destruktif.** Buktikan cukup buat nunjukin bug, JANGAN nyebabin kerusakan nyata (jangan drain dana, jangan hapus data, jangan ganggu user lain). Untuk web3: pakai fork/simulasi (mis. mainnet fork) buat demo, bukan exploit on-chain beneran.
- **Isolasi variabel**, minimize payload, tentuin komponen mana yang bener-bener memicu.
- Kumpulin bukti: log request/response, screenshot, tx hash (kalau web3), video kalau perlu.

Output: PoC yang bisa diulang orang lain persis.

---

## Fase 2 — Impact & severity

- Petakan apa yang bisa dilakukan attacker: exfil data, ambil alih akun, RCE, drain dana, cross-user/cross-tenant, DoS, dsb.
- Skala: single-user vs semua user vs seluruh protokol.
- Prasyarat: butuh privilege/interaksi korban apa? makin sedikit prasyarat → makin tinggi.
- Skor pakai kerangka yang dikenal (CVSS buat umum; buat web3 tambahin "dana at-risk" & likelihood eksploitasi). Jujur — over-claim ngerusak kredibilitas.

Output: severity + rasional 2–3 kalimat.

---

## Fase 3 — Cari kontak dev/owner

Detail metode → `references/contact-discovery.md`. Ringkasan prioritas:

1. **Kanal security resmi dulu**: `/.well-known/security.txt`, `SECURITY.md`, halaman `/security`, program di HackerOne/Bugcrowd/Immunefi/HackenProof (walau lo nemunya di luar platform, banyak yang tetap nerima laporan).
2. **Kalau ga ada program**: kontak maintainer/owner langsung — GitHub org/maintainer, email di repo/website, WHOIS, DNS SOA, package registry maintainer.
3. **Web3**: docs projek, GitHub, admin Discord/Telegram, Twitter/X resmi, ENS, deployer/multisig signer on-chain, auditor (bisa jadi relay), governance forum.
4. **Buntu / tim ga responsif**: koordinator pihak ketiga (CERT/CC, CERT nasional, disclose.io) buat mediasi.

**Verifikasi pihak** sebelum ngirim: pastiin itu owner/maintainer sah, bukan akun palsu. Prioritaskan kontak security khusus di atas DM pribadi.

Output: 1–2 kontak terverifikasi + kanalnya.

---

## Fase 4 — Kirim laporan via email

Template lengkap → `references/report-templates.md`.

- **Subject jelas**: `[Security] Vulnerability disclosure — <projek/aset>`.
- **Body**: identitas singkat + niat good-faith → apa & di mana → impact → PoC minimal → tawaran koordinasi → timeline disclosure (default 90 hari, bisa disesuaikan; percepat kalau dana live at-risk) → tanpa ancaman/ransom.
- **Detail sensitif dienkripsi** (PGP dari security.txt) — wajib buat bug unpatched yang berdampak besar / dana at-risk.
- Lampirkan laporan teknis terpisah kalau panjang.
- Kalau agent yang ngirim: pakai tool email yang tersedia; kirim ke kontak terverifikasi dari Fase 3; jangan blast ke banyak alamat sekaligus (pilih kanal paling resmi).

Output: email terkirim + arsip laporan.

---

## Fase 5 — Koordinasi & follow-up

- Catat tanggal kirim & tenggat respons (mis. follow-up sopan setelah 7–14 hari kalau senyap).
- Bantu tim reproduce/verify kalau mereka minta.
- **Jangan publikasikan** sebelum fix ter-deploy atau timeline disepakati habis. Untuk web3 dengan dana at-risk: tunda publikasi sampai aman.
- Kalau owner ga bisa dihubungi / diam total setelah usaha wajar → eskalasi ke koordinator (CERT/CC) daripada full-disclosure sepihak.
- Tutup dengan ringkasan: bug, timeline, status fix, kredit (kalau diberikan).

Output: catatan koordinasi + status akhir.
