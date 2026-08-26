# Contact Discovery — Nyari Kontak Dev/Owner

Referensi Fase 3 di `workflow.md`. Tujuan: nemuin pihak yang benar buat dikirimi laporan, lewat kanal paling resmi. Semua ini OSINT dari sumber publik untuk keperluan disclosure — bukan buat nyerang.

## Prioritas kanal (dari paling resmi)

1. **Kanal security khusus** — selalu cek duluan.
2. **Program bug bounty / VDP** — walau nemunya di luar platform.
3. **Kontak maintainer/owner langsung** — kalau ga ada kanal security.
4. **Koordinator pihak ketiga** — kalau owner ga responsif/ga ketemu.

---

## Umum (web / software / infra)

- **`/.well-known/security.txt`** (RFC 9116) — field `Contact`, `Encryption` (PGP), `Policy`, `Acknowledgments`. Sumber paling otoritatif.
- **`SECURITY.md`** — di root repo atau `.github/`. Berisi kebijakan & kontak disclosure.
- **Website**: halaman `/security`, `/contact`, footer, About, Imprint/Legal.
- **GitHub/GitLab**:
  - Org → tab Security / Advisories (bisa buka private advisory).
  - Maintainer aktif dari commit history & `CODEOWNERS`.
  - Email dari `git log` (hati-hati: email publik commit, pakai buat kontak profesional saja).
  - `CONTRIBUTING.md`, `MAINTAINERS`.
- **WHOIS domain** — kontak registrant/abuse (sering ter-redact, tapi abuse@ registrar bisa relay).
- **DNS**: record `SOA` → RNAME = email admin zona (format `admin.domain.com` → `admin@domain.com`).
- **Package registry**: maintainer di npm/PyPI/crates; `authors` di `Cargo.toml`/`package.json`/`pyproject.toml`.
- **Program terdaftar**: HackerOne, Bugcrowd, Intigriti — cek apakah aset in-scope.

## Web3 / crypto

- **Docs & website resmi** projek → halaman security/bug bounty.
- **Immunefi / HackenProof** — banyak protokol listing di sini; cek walau nemunya di luar.
- **GitHub** protokol (kontrak sering open-source) → maintainer, `SECURITY.md`.
- **Komunitas resmi**: admin Discord/Telegram, Twitter/X terverifikasi projek (DM/kontak tim). Pakai buat minta kanal privat, jangan bocorin detail di channel publik.
- **On-chain**:
  - Deployer address kontrak → cari identitas publik / label di explorer (Etherscan/Blockscout).
  - **Multisig signers** (Safe) → sering ada anggota tim yang teridentifikasi.
  - ENS / label publik.
  - Kontak di verified contract metadata / explorer "Info" tab.
- **Auditor** — kalau kontrak pernah diaudit, firma auditor (mis. yang tertera di report) bisa jadi relay tepercaya ke tim.
- **Governance forum** (Commonwealth/Discourse) — tim inti biasanya aktif.

## Kalau owner ga ketemu / diam

- **CERT/CC** (cert.org) atau **CERT nasional** (mis. ID-SIRTII/CSIRT) — koordinator disclosure netral.
- **disclose.io** — direktori kebijakan disclosure & safe-harbor.
- Untuk web3: platform seperti Immunefi juga bisa bantu koordinasi ke tim.

---

## Verifikasi & higiene disclosure

- **Pastikan pihak benar** sebelum kirim: cocokkan kontak dengan domain/repo/kanal resmi. Waspada akun/alamat palsu (impersonation umum di crypto).
- **Kanal security > DM pribadi.** Kalau terpaksa DM, minta pindah ke email/kanal resmi.
- **Enkripsi detail sensitif** dengan PGP dari `security.txt`/`SECURITY.md`, terutama bug unpatched berdampak besar atau dana at-risk.
- **Jangan blast** ke banyak alamat sekaligus — pilih satu kanal paling resmi; broadcast malah nurunin kepercayaan & risiko bocor.
- **Minimalkan data** di kontak awal: cukup "ada isu security, minta kanal aman" kalau belum yakin kanalnya privat.
