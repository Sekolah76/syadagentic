# CHANGELOG

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.1.0/) dan
[Semantic Versioning](https://semver.org/lang/id/).

## [Unreleased]

### Akan datang
- Contoh workflow end-to-end per divisi (`examples/`).
- Drill scoreboard otomatis dari CI.

## [9.0.0] — 2026-11-25

Rilis ini isinya kebenaran struktural: semua klaim di README sekarang punya
barang, dan CI tidak lagi merah permanen.

### Ditambah
- `VERSION` sebagai satu-satunya sumber versi (dibaca `install.sh`, dicek test
  dan verifier). Badge README tidak bisa lagi beda dari kode.
- `arsenal-skills/MANIFEST.sha256` + `tools/build_manifest.py` — manifest
  SHA256 1.124 file skill, bisa diverifikasi (`--check`).
- `tools/verify_repo.py` — audit klaim README vs isi direktori, placeholder,
  secret, link relatif, installer, dan CI.
- `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, issue template, PR
  template, `.editorconfig`.
- `install.sh`: flag `--no-agent`, `--dry-run`, `--version`, `--help`; banner
  membaca `VERSION`; URL clone yang benar.
- Test suite naik dari 10 ke 21 test: framework-core, semua `.py` compile,
  semua `.sh` lolos `bash -n`, JSON/YAML valid, konsistensi versi, tidak ada
  placeholder/secret, link relatif, manifest.

### Diperbaiki
- **CI merah permanen**: test `camoufox` gagal di runner padahal dependency itu
  opsional dan tidak pernah di-install. Sekarang dependency opsional
  (`z3`, `camoufox`, `pyyaml`, API env) di-skip, bukan digagalkan; `--strict`
  tersedia kalau mau ketat.
- README: versi 7.3 → sesuai `VERSION`, angka skill diralat ke angka nyata
  (1.124 file / 84 `SKILL.md` / 40 template), URL clone placeholder diganti,
  link `t.me/<...>` mati dihapus, TOC + badge CI ditambah.
- Klaim palsu `SKILLS.lock 8137 skill` di README/SOUL/AGENTS diganti manifest
  yang benar-benar ada.
- Landing page `docs/index.html` disinkronkan (versi + angka + link).

### Keamanan
- `IDENTITY.md` tidak lagi memuat alamat email operator.
- `PROVENANCE.md` tidak lagi memuat path home pengguna lain (diganti
  `$HOME/.hermes/...`).
- `test_no_secret` + `c_secrets` mencegah token masuk lagi ke file core.

## [8.2]
- Fix node 9router (`cx`/`ag`), perbaiki `farm_scripts` (nama file).

## [8.1]
- Bersihkan data pribadi dari repo (path, nama operator, SSH key, IP GCP).

## [8.0]
- Rebrand total: README, `installer.sh`, rename `arsenal-skills`, perbaikan
  bagian SECURITY di `AGENTS.md`.

## [7.3] dan sebelumnya
- Lihat riwayat commit. Sebelum 9.0.0 tidak ada changelog terpelihara.
