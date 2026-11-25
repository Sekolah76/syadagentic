# CONTRIBUTING — SYADAGENTIC

Terima kasih mau ikut isi. Repo ini kecil, aturannya pendek, dan semuanya
ditegakkan oleh CI — bukan oleh selera.

## Aturan inti

1. **Klaim tanpa bukti = ditolak.** Kalau kamu menambah angka di README
   ("1200 skill", "tembus model X"), angka itu harus cocok dengan isi direktori
   dan bisa diverifikasi `python3 tools/verify_repo.py`.
2. **Jangan naikkan versi tanpa CHANGELOG.** Setiap perubahan perilaku masuk
   `CHANGELOG.md` di bagian `[Unreleased]` atau versi baru.
3. **Satu PR = satu hal.** Jangan campur "tambah skill" dengan "refactor
   installer" dalam satu PR.
4. **Jangan pernah commit secret.** Token, cookie, API key, isi `.env`, atau
   `cf_clearance` milik siapa pun. Kalau butuh contoh, pakai placeholder
   (`sk-REPLACE_ME`, `AKIAIOSFODNN7EXAMPLE`).
5. **Skill baru wajib punya `SKILL.md`** + `PROVENANCE.md` kalau isinya diambil
   dari sumber lain (cantumkan URL asli dan lisensinya).

## Sebelum push

```bash
python3 tests/run_tests.py         # harus 0 failed (skip dependency opsional wajar)
python3 tools/verify_repo.py       # klaim vs isi repo
python3 tools/build_manifest.py    # kalau kamu menambah/mengubah file di arsenal-skills/
bash -n install.sh                 # kalau kamu menyentuh installer
```

Kalau kamu mengubah isi `arsenal-skills/`, **wajib** regenerate
`arsenal-skills/MANIFEST.sha256`, kalau tidak CI merah di cek manifest:

```bash
python3 tools/build_manifest.py            # tulis ulang
python3 tools/build_manifest.py --check    # verifikasi
```

## Format commit

```
area: ringkas apa yang berubah

kenapa: alasan teknis (bukan "biar rapi")
bukti: command + output singkat kalau menyentuh klaim/fitur
```

Contoh: `installer: tambah --dry-run` / `skills: tambah playbook graphql-idor`.

## Menambah template jailbreak

1. Buka `prompt-injection/templates.md`, ikuti penomoran `T<n>` yang ada
   (jangan pakai nomor kosong yang melewati urutan).
2. Sertakan: nama template, target model yang diuji, mekanisme, contoh payload,
   dan **status hasil** (✅ / ❌) apa adanya.
3. Template yang gagal tetap boleh masuk — asal ditandai gagal. Klaim "tembus
   semua model" adalah alasan utama orang tidak percaya repo seperti ini.

## Menambah skill

- Letakkan di `arsenal-skills/skills-lengkap/<kategori>/<nama-skill>/SKILL.md`.
- `SKILL.md` minimal punya: kapan dipakai, langkah, payload/perintah konkret,
  cara verifikasi, jebakan/false-positive.
- Jangan copy-paste dump tanpa konteks; ringkas, tapi jangan hilangkan detail
  teknis yang bikin skill itu berguna.

## Bug / ide

Pakai issue template yang tersedia. Kalau ini masalah keamanan, **jangan buka
issue** — ikuti [SECURITY.md](SECURITY.md).

## Lisensi kontribusi

Dengan mengirim PR kamu setuju kontribusimu dirilis di bawah MIT, sama seperti
repo ini.
