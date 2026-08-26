---
name: submission-review-gate
description: 7-Stage Bug Bounty Pipeline & 14-Point Mandatory Pre-Submission Quality Gate. Prevents false positives, severity inflation, and premature submissions.
category: bug-bounty
---

# 7-Stage Pipeline & 14-Point Pre-Submission Review Gate

## Pipeline Stages

```
Stage 1: Recon & Codebase Mapping
   │
   ▼
Stage 2: Attack Surface Discovery
   │
   ▼
Stage 3: Bug Discovery (Candidate Collection)
   │
   ▼
Stage 4: Deep Verification (PoC, Exploit, Economic Impact)
   │
   ▼
Stage 5: Duplicate & Scope Check
   │
   ▼
Stage 6: Report Generator
   │
   ▼
Stage 7: Final Submission Review Gate
   │
   ▼
[READY TO SUBMIT]
```

---

## MISSION & OBJECTIVE

- **MISSION:** Tidak ada report yang boleh dibuat atau dikirim sebelum melewati review ini.
- **OBJECTIVE:** Verifikasi bahwa finding benar-benar layak disubmit, bukan false positive, duplicate, intended behavior, atau sekadar design issue.

---

## 14-POINT MANDATORY PRE-SUBMISSION CHECKLIST

### 1. VALIDASI
- Reproduce minimal 5x.
- Jalankan pada commit terbaru.
- Jalankan pada fork/mainnet-equivalent jika memungkinkan.
- Pastikan hasil konsisten.

### 2. IMPACT (BUKTIKAN KERUGIAN NYATA)
Jangan hanya menunjukkan code flaw. Wajib menjawab:
- Apa yang dicuri?
- Apa yang rusak?
- Siapa yang dirugikan?
- Berapa maximum loss?
- Apakah skenario exploit realistis?

### 3. PROOF OF CONCEPT (POC)
PoC harus:
- Repeatable (dapat diulang secara deterministik).
- End-to-end (dari kondisi awal sampai perolehan dana/dampak).
- Tanpa asumsi tidak realistis.
- Tidak membutuhkan privileged access kecuali memang bagian threat model.

### 4. ROOT CAUSE
Jelaskan:
- Mengapa bug terjadi.
- Mengapa validasi gagal.
- Fungsi & komponen yang terlibat.
- Call flow diagram / trace.
- State transition breakdown.

### 5. SCOPE VERIFICATION
Pastikan:
- Target asset in-scope.
- Commit hash in-scope.
- Smart contract address in-scope.
- Bukan third-party / external dependency issue.

### 6. EXCLUSION CHECK (BUKAN OUT-OF-SCOPE/NOISE)
Pastikan BUKAN:
- Intended behavior / documented design.
- Governance decision / multi-sig admin risk.
- Centralization trade-off.
- Missing best practice tanpa kerugian nyata.
- Informational / gas optimization / code style.
- Dead code tanpa dampak keamanan.

### 7. DUPLICATE CHECK
Cari dan bandingkan pada:
- GitHub Issues & Pull Requests.
- Audit reports sebelumnya.
- Known issues & public disclosures.
- Contest writeups (Sherlock, Code4rena, Cantina).

### 8. PATCH CHECK
- Pastikan bug belum diperbaiki di branch pengembang atau commit terbaru.

### 9. REPORT QUALITY STANDARDS
Report wajib memiliki struktur:
1. Title (Jelas & Deskriptif)
2. Summary (Ringkas & Padat)
3. Root Cause
4. Technical Details
5. Impact Analysis
6. Proof of Concept (PoC)
7. Reproduction Steps
8. Evidence / Logs / Screenshots
9. Recommended Fix (Actionable Remediation)
10. References

### 10. SEVERITY FORMULATION
Hitung dan tentukan berdasarkan data riil:
- CVSS 3.1 Score
- CWE Mapping
- Likelihood & Exploitability
- Business / Economic Impact

### 11. CONFIDENCE SCORE
Evaluasi matriks keyakinan:
- Validity (0–100%)
- Exploitability (0–100%)
- Impact Measurability (0–100%)
- Duplicate Risk (Low/Med/High)
- Report Quality (High/Low)

### 12. FINAL DECISION MATRIX
Output status akhir hanya salah satu dari opsi berikut:
- `✅ READY TO SUBMIT`
- `⚠ NEED MORE EVIDENCE`
- `⚠ POSSIBLE DUPLICATE`
- `⚠ OUT OF SCOPE`
- `⚠ DESIGN DECISION`
- `⚠ FALSE POSITIVE`

### 13. SUBMISSION RULES (ZERO TOLERANCE)
- ❌ Jangan pernah melebih-lebihkan severity.
- ❌ Jangan mengarang impact atau angka kerugian.
- ❌ Jangan mengarang estimasi bounty.
- ❌ Jangan mengklaim Critical tanpa PoC yang membuktikan kerugian nyata.
- ❌ Jangan pernah mengirim submission otomatis tanpa konfirmasi operator.

### 14. ADVERSARIAL SELF-CRITIQUE (TRIAGER PERSPECTIVE)
Sebelum memberikan status `READY TO SUBMIT`, lakukan simulasi review sebagai Triager program dan jawab:
1. *Mengapa saya mungkin akan menolak report ini?*
2. *Bukti apa yang masih kurang?*
3. *Apakah ada interpretasi lain yang membuat ini intended behavior?*
4. *Seberapa yakin saya (0–100%) bahwa report ini akan diterima dan dibayar?*

`READY TO SUBMIT` hanya boleh dikeluarkan jika seluruh 14 poin checklist di atas lolos 100%.
