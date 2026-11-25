# SECURITY — SYADAGENTIC

## Ringkas

Repo ini berisi prompt, skill, dan tooling untuk otomasi + security testing.
Dua risiko utamanya bukan "RCE di kode", tapi:

1. **Kebocoran kredensial** — instalasi nyata memegang token provider, cookie
   sesi, dan API key. Jangan pernah commit itu ke repo, jangan tempel di issue.
2. **Penyalahgunaan isi** — template dan skill bug-bounty hanya untuk target
   yang kamu punya izinnya (program bug bounty, CTF, aset sendiri, engagement
   tertulis). Operator yang menanggung akibatnya, bukan repo ini.

## Hardening yang sudah ada di repo

| Kontrol | Detail |
|---|---|
| Secret scanner di CI | `tools/verify_repo.py` + `tests/run_tests.py` menolak token (`ghp_`, `github_pat_`, `sk-`, `AKIA`, private key, `xox[baprs]-`) di file core |
| Placeholder scanner | URL `github.com/<USER>/…` dan link `t.me/<...>` tidak boleh balik lagi |
| Integritas skill | `arsenal-skills/MANIFEST.sha256` — perubahan file tidak sah akan gagal `--check` |
| Installer aman | config agent dibackup `.bak-syad` sebelum diubah, ada `--dry-run`, ada `--no-agent` |
| Protected paths | `SAFETY-FRAMEWORK.md` + `checkpoint.py` untuk backup sebelum perubahan destruktif |
| Evidence gate | `gate/gate.py` — klaim tanpa bukti tool ditolak |

## Kalau kamu menemukan masalah

**Jangan buka issue publik.** Kirim ke operator repo (lihat profil GitHub
`Sekolah76`) dengan:

- deskripsi singkat + dampak nyata (bukan teoretis),
- langkah reproduksi minimal,
- versi/commit yang kena (`git rev-parse --short HEAD`),
- bukti output tool (screenshot/log), tanpa data pribadi orang lain.

Yang dianggap valid: bypass gate/verifier sehingga CI hijau padahal klaim palsu,
script installer menulis ke path berbahaya tanpa konfirmasi, secret scanner bisa
dilewati, atau file di `arsenal-skills` bisa diubah tanpa terdeteksi manifest.

Yang tidak dianggap masalah repo ini: "template bisa bikin model jailbreak"
(itu memang fungsi repo), atau "skill bug-bounty bisa dipakai jahat" (lihat
bagian izin di atas).

## Untuk pengguna repo ini

```bash
bash install.sh --dry-run     # lihat dulu apa yang akan diubah
bash install.sh --no-agent    # kalau tidak mau config agent disentuh
python3 tools/verify_repo.py  # pastikan checkout-mu bersih
```

Jangan simpan token provider di dalam folder framework. Pakai environment
variable atau secret manager milikmu sendiri.
