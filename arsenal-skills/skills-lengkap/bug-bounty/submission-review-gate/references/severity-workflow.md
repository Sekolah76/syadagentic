# Bug Bounty Severity Workflow (VRT / CVSS v3.1)

> Quick reference untuk penentuan tingkat keparahan P1–P5 (Bugcrowd VRT, HackerOne, YesWeHack, Immunefi).

---

## 1. Workflow 3 Langkah Penentuan Severity

### Langkah 1 — Analisis Impact Riil
- RCE / Account Takeover (ATO) / Dump Database / Kerugian Finansial Langsung = **Critical**
- Kebocoran Data Sensitif Pengguna Lain (IDOR / SSRF Internal) = **High**
- Memerlukan Interaksi Pengguna (XSS / CSRF / Open Redirect) = **Medium**
- Info Leak Minor tanpa Data Sensitif = **Low / Informational**

### Langkah 2 — Kompleksitas Eksploitasi
- Tanpa Autentikasi + Tanpa Interaksi Korban → **Naik 1 Tingkat**
- Memerlukan Akun Autentikasi + Butuh Interaksi Korban → **Turun 1 Tingkat**
- Memerlukan Kondisi Edge-Case Super Spesifik → **Turun 1–2 Tingkat**

### Langkah 3 — Pemetaan Priority, CVSS & Estimasi Bounty

| Priority | Rentang CVSS v3.1 | Klasifikasi Severity | Rentang Reward (Contoh) | Karakteristik Finding |
|---|---|---|---|---|
| **P1** | **9.0 – 10.0** | **Critical** | $1,200 – $5,000+ | RCE, Mass SQLi Dump, Global Account Takeover, Payment Logic Bypass. |
| **P2** | **7.0 – 8.9** | **High** | $500 – $1,200 | Auth Bypass, SSRF Internal Cloud, IDOR Akun Tertarget, Stored XSS Curi Session. |
| **P3** | **4.0 – 6.9** | **Medium** | $250 – $500 | Reflected XSS, CSRF Ganti Data, Wildcard CORS + Data Sensitif. |
| **P4** | **2.0 – 3.9** | **Low** | $50 – $150 / Hall of Fame | Verbose Error Stacktrace, Version Disclosure, Path Disclosure. |
| **P5** | **0.0 – 1.9** | **Informational** | $0 (N/A) | Missing Header, DMARC/SPF Tanpa Bukti Spoofing, Clickjacking Tanpa Aksi Kritis. |

---

## 2. Quick Decision Tree

```
Bisa RCE / ATO tanpa login? ──YES──> P1 Critical
        │
        NO
        ▼
Bisa ambil/ubah data ORANG LAIN? ──YES──> P2 High
        │
        NO
        ▼
Butuh user klik + impact cuma diri sendiri? ──YES──> P3 Medium
        │
        NO
        ▼
Cuma bocorin versi / error / header? ──YES──> P4/P5 Low/Info
```

---

## 3. Catatan Program & Edge-Cases

- **XSS Capping:** Sebagian program membatasi severity XSS maksimal di **Medium** meskipun CVSS kalkulator menunjukkan High. Jangan memaksakan High jika aturan program menyatakan cap.
- **Out of Scope (OOS) Otomatis:** Rate limiting tanpa dampak finansial, missing captcha, DMARC/SPF teoritis, dan open redirect standalone sering diklasifikasikan sebagai auto N/A.
- **Validitas PoC:** Wajib menyertakan PoC non-destruktif yang konsisten (screenshot, cURL command, atau HAR request replay).

---

## 4. Checklist Pra-Submit

- [ ] PoC berhasil di-reproduce minimal 5x berturut-turut.
- [ ] Dampak keamanan riil terhadap pengguna lain atau finansial terbukti nyata.
- [ ] Parameter autentikasi dan kompleksitas penyerangan telah diperhitungkan.
- [ ] Daftar Out of Scope (OOS) program sasaran telah diperiksa.
- [ ] Parameter dan endpoint telah dikelompokkan untuk mencegah laporan duplikat.
