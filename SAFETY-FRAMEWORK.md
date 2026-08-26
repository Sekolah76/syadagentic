# SAFETY-FRAMEWORK.md — Anti-Rusak-File Protection Layer (SYADAGENTIC v6.0)
# Tujuan: saat framework (SYADAGENTIC yang lepas banyak guard + SyadAgentic) 
# beroperasi, file-file penting operator DIJAMIN tidak rusak.
# Menggabungkan kebutuhan: "banyak guard dilepas" + "jangan sampai rusak file".

---

## 1. LAPISAN PELINDUNG FILE (protected paths)

### TIER-A (HARD-PROTECTED — read-only, backup wajib sebelum diubah)
Operator tidak boleh terganggu. Setiap eksekusi yang menyentuh ini WAJIB backup dulu.
```
~/AppData/Roaming/9router/db/data.sqlite        # DB 9router
~/.ssh/ssh-key                                # SSH key
~/AppData/Roaming/gcloud\                       # GCP credentials
~/AppData/Local/hermes/memories/MEMORY.md       # Ingatan utama
~/AppData/Local/hermes/memories/USER.md
~/AppData/Local/hermes/config.yaml              # Konfig hermes
~/farm-arsenal/daytona_keys.txt                 # API keys
~/farm-arsenal/balitech_accounts.json           # data akun
```

### TIER-B (WORK-PROTECTED — snapshot sebelum batch edit)
Folder projek aktif — di-snapshot kalau mau edit massal.
```
~/farm-arsenal/syadagentic\                     # framework
~/farm-arsenal/th-farm\                         # TH state
~/Downloads/SYADAGENTIC\              # sumber SYADAGENTIC (jangan diubah!)
```
SYADAGENTIC sumber = READ-ONLY (salin dulu ke farm-arsenal kalau mau merge).

---

## 2. WAJIB BACKUP SEBELUM MODIFIKASI (auto checkpoint)
```python
# checkpoint.py — auto backup sebelum perubahan file penting
import shutil, datetime, os

def checkpoint(path):
    """Buat backup .bak-TIMESTAMP sebelum file diubah."""
    if not os.path.exists(path):
        return None
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    bak = f"{path}.bak-{ts}"
    shutil.copy2(path, bak)
    # simpan ke registry backup (rollback)
    with open(r"~/.backup-log.txt", "a") as f:
        f.write(f"{ts} {path}\n")
    return bak
```

---

## 3. ROLLBACK (kalau ada yang rusak)
```bash
# cara rollback file tertentu
# 1. Cari backup terakhir
ls -t ~/AppData/Roaming/9router/db/data.sqlite.bak-* | head -1
# 2. Restore
cp <backup> ~/AppData/Roaming/9router/db/data.sqlite
# 3. Restart 9router
```

---

## 4. ATURAN EKSEKUSI AMAN (SAFE EXECUTION RULES)
1. **JANGAN** edit `Downloads/SYADAGENTIC/` langsung — selalu salin ke arsenal dulu.
2. **SEBELUM** patch 9router/DB → backup (`.bak-<timestamp>`).
3. **SEBELUM** edit hermes config -> backup.
4. **JANGAN** jalankan script SYADAGENTIC (`apply_guardrail_patches.py`, `install.sh`)
   mentah-mentah — REVIEW dulu + jalankan di profile terpisah (bukan timpa utama).
5. **FILE KUNCI** yang SYADAGENTIC mau patch = hanya di profile SYADAGENTIC 
   (AppData/Local/hermes/profiles/SYADAGENTIC/) — JANGAN disentuh profile default.
6. Semua perubahan besar → commit ke git dulu (rollback via git).
7. Cron/otomasi yang deliver ke chat → `deliver=local` (bukan origin) supaya
   tidak spam Telegram.
8. Test di profile terpisah sebelum apply ke utama.

---

## 5. ARSITEKTUR ISOLASI (Alpha Lunero: profile terpisah = aman)
```
PROFILE DEFAULT (SyadAgentic)  <-- UNTOUCHED, memory utama, hermes telegram kamu
PROFILE SYADAGENTIC (VPS)        <-- SYADAGENTIC jalan di sini, terpisah
SYADAGENTIC v6.0 (gabungan)     <-- hasil merge, di repo + dipakai dua-duanya
```
- Guardrail yang SYADAGENTIC lepas = HANYA di profile SYADAGENTIC (silo)
- Guardrail default = TETAP (syadagentic aman)
- Kalau SYADAGENTIC rusak file → rollback profile, default tidak terdampak

---

## 6. ANTISIPASI KERUSAKAN DARI GUARD-BYPASS
Banyak guard = banyak akses = risiko kenalan system. Mitigasi:
- **Dry-run dulu**: jalankan perintah dengan `--dry-run` / test di temp
- **Scope guard**: definisikan T1 (own infra), T2 (authorized), T3 (3rd party)
  → eksekusi T3 tidak auto, butuh konfirmasi
- **Quarantine**: file output dari SYADAGENTIC di-scan dulu sebelum ditulis ke 
  path produksi
- **Kill-switch**: backup log + rollback script siap (checkpoint.py)

---

## 7. BUKTI & NO-HALU
- Semua perubahan besar didokumentasikan di CHAIN.md + RESULTS-MATRIX
- Klaim "work" = verified (test nyata), bukan narasi
- Kalau gagal = lapor jujur + rollback + coba jalur lain