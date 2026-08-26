# Vuln Classes — Recognition Quick-Reference

Referensi Fase 0/2 di `workflow.md`. Level **pengenalan & triase** — buat ngeklasifikasi temuan dan nentuin impact, bukan resep eksploitasi. Demo selalu minimal & non-destruktif (lihat guardrail).

## Daftar isi
- [Web / API](#web)
- [Infra / Cloud](#infra)
- [Mobile](#mobile)
- [Smart Contract / Web3](#web3)
- [Agent / LLM (info-flow)](#agent)

---

<a name="web"></a>
## Web / API
- **Broken access control / IDOR** — objek/route milik orang lain bisa diakses dengan ganti ID. Impact tinggi, umum.
- **AuthN/AuthZ** — bypass login, session fixation, JWT lemah, privilege escalation.
- **Injection** — SQLi, command injection, template injection (SSTI), NoSQLi.
- **SSRF** — server dipaksa request ke internal/metadata endpoint.
- **XSS** — stored > reflected > DOM; nilai naik kalau kena akun lain.
- **Insecure deserialization**, **file upload**, **path traversal**.
- **Secrets exposure** — API key/token di JS, repo, response, `.git` kebuka.
- **Business logic** — race condition, harga/kuota bisa diakalin.
- Recognize: input user nyampe ke sink berbahaya tanpa validasi/otorisasi.

<a name="infra"></a>
## Infra / Cloud
- Misconfig storage (bucket publik), service kebuka tanpa auth, dashboard admin exposed.
- IAM over-permissive, kredensial di env/metadata bocor.
- Default creds, port/manajemen terbuka ke internet.
- CI/CD & supply chain: token bocor, artifact bisa di-tamper.

<a name="mobile"></a>
## Mobile
- Secrets hardcoded di APK/IPA, storage lokal ga aman.
- Cert pinning absen → MITM, deep link/intent bisa disalahgunakan.
- API backend yang sama → banyak bug web berlaku juga.

<a name="web3"></a>
## Smart Contract / Web3
- **Reentrancy** — state di-update setelah external call (langgar checks-effects-interactions).
- **Access control** — fungsi sensitif tanpa `onlyOwner`/role; init bisa dipanggil ulang.
- **Oracle / price manipulation** — harga dari sumber yang bisa digoyang (flash loan).
- **Integer / rounding / precision** — pembulatan menguntungkan attacker.
- **Signature/replay** — nonce/domain separator lemah, tanda tangan dipakai ulang.
- **Upgradeability / proxy** — storage collision, admin proxy tak terlindungi.
- **Tx ordering / MEV** — front-run/sandwich pada logika yang sensitif urutan.
- **Access ke dana / withdrawal logic** — jalur narik dana yang bisa disalahgunakan.
- Recognize: siapa bisa gerakin dana/ubah state kritis di luar yang diizinkan.
- Demo: pakai **mainnet fork / simulasi**, jangan exploit on-chain nyata; sertakan tx simulasi + dampak.

<a name="agent"></a>
## Agent / LLM (info-flow)
Model: **source untrusted → konteks LLM → sink privileged.** Bug = jalur dari data untrusted ke aksi privileged tanpa kontrol.
- **Goal hijack / indirect injection** — instruksi ditanam di web/RAG/email/output tool → agent nurut.
- **Tool misuse** — agent dipaksa manggil tool/param di luar intent.
- **Identity & privilege** — confused deputy, cross-tenant, escalation via sub-agent.
- **Supply chain** — MCP/plugin/model pihak ketiga dipercaya berlebih.
- **Code exec** — injeksi ke interpreter, sandbox escape.
- **Memory/context poisoning** — payload ditanam sekarang, trigger di sesi berikutnya.
- **Inter-agent comm** — pesan antar-agent ga terautentikasi (spoof/tamper).
- **Human-agent trust** — output manipulatif biar manusia approve aksi bahaya.
- Recognize: petakan tiap source untrusted ke tiap sink privileged; uji jalur yang nyebrang trust boundary tanpa validasi/consent.
- Acuan: OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10).
