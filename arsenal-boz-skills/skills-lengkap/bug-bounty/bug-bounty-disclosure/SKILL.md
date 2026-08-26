---
name: bug-bounty-disclosure
description: Skill end-to-end buat authorized/good-faith bug bounty & coordinated vulnerability disclosure ke developer atau pemilik projek — untuk SEMUA jenis bug (web, API, infra, mobile, cloud, smart contract/web3, agent/LLM), crypto maupun non-crypto. Pakai skill ini setiap kali user mau triase & verifikasi temuan, bikin PoC, NYARI kontak dev/owner (security.txt, SECURITY.md, GitHub, WHOIS, on-chain, sosmed), dan KIRIM laporan via email — baik target punya program bug bounty terdaftar (HackerOne/Immunefi/dll) maupun proyek tanpa program resmi. Trigger juga kalau user nyebut "report bug ke dev", "disclosure", "lapor kerentanan", "cari kontak owner projek", "kirim report email", "responsible disclosure", "bug bounty" — walau ga eksplisit bilang "skill". Sisi disclosure jalan buat proyek apapun; dasar pengetesan harus sah/good-faith.
---

# Bug Bounty & Coordinated Disclosure

Skill buat ngerapihin seluruh alur dari **temuan → verifikasi → cari kontak → lapor ke dev via email → koordinasi fix**. Serba-guna: crypto & non-crypto, target dengan program resmi maupun tanpa program. Fokusnya bikin laporan yang **valid, reproducible, dan diterima dev** — bukan AI-slop yang di-ignore.

## ⚠️ Dasar good-faith (baca dulu, singkat)

Skill ini buat **good-faith security research + coordinated disclosure**. Lapor kerentanan ke pemilik projek itu sah & etis **entah mereka punya program resmi atau enggak** — justru itu tujuannya.

Yang harus dijaga: **dasar pengetesan harus sah.** Bug ditemukan lewat cara legit:
- Sistem/infra milik sendiri, akun sendiri, atau testnet.
- Review kode open-source / artefak publik (repo, package, image).
- Analisis smart contract on-chain (bytecode/source publik).
- Target yang punya program bug bounty / VDP / `security.txt` yang mengundang laporan.
- Ada izin tertulis dari owner.

Jangan pakai skill ini buat **membenarkan intrusi tanpa izin** ke sistem produksi pihak ketiga (mancing kredensial, nembus akses yang bukan hak lo, lanjut nge-drill setelah dapat akses). Kalau ragu apakah suatu langkah pengetesan sah: **stop, jangan eskalasi akses**, laporkan hanya yang lo temukan lewat cara legit. Untuk bug crypto yang dananya live & exploitable: **jangan exploit, jangan publikasikan dulu** — disclosure privat ke tim adalah langkah yang benar.

## Prinsip inti

Sebuah temuan layak dikirim ke dev kalau: **(1) valid & reproducible dengan PoC**, **(2) impact-nya nyata**, **(3) dikirim ke pihak yang benar lewat kanal yang tepat**, dengan **(4) nada good-faith, tanpa ancaman/ransom.**

## Alur pakai skill

1. **Jalanin `workflow.md`** — pipeline 6 fase: Triase → Verifikasi/PoC → Impact → Cari Kontak → Kirim Email → Koordinasi & Follow-up.
2. **Fase Cari Kontak** → buka `references/contact-discovery.md` (metode nyari dev/owner, crypto & non-crypto, + verifikasi pihak & enkripsi).
3. **Fase Kirim Email** → buka `references/report-templates.md` (template email disclosure + laporan teknis, ID/EN).
4. **Butuh klasifikasi bug** (fase Triase/Impact) → `references/vuln-classes.md` (recognition cepat: web/API/infra/cloud, smart contract/web3, agent/LLM info-flow).

## Aturan anti-slop (non-negotiable)

1. **No PoC, no report.** Tiap klaim reproducible dengan bukti (log/screenshot/tx hash).
2. **Impact ditunjukin, bukan diklaim.** Demokan minimal & non-destruktif; jangan bikin kerusakan buat "ngebuktiin".
3. **Ulang ≥3×**, isolasi variabel, minimize payload/PoC.
4. **Ga bisa reproduce → buang.** Jangan overclaim severity, jangan filler.
5. **Satu report = satu bug** yang jelas. Jangan gabung 10 "temuan" variasi teks.
6. **Kirim ke pihak & kanal yang benar.** Verifikasi dulu, pakai kanal security khusus, enkripsi detail sensitif.

## Output

Deliverable: temuan tervalidasi → kontak dev/owner terverifikasi → email disclosure + laporan teknis (bahasa ngikutin target, ID/EN, nada natural & teknis) → catatan koordinasi/timeline.
