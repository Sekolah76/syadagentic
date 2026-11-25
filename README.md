<div align="center">

# 🔓 SYADAGENTIC

### Universal Agent Framework — Zero-Refusal · Automation · Security

**Satu framework untuk bikin agent kamu langsung eksekusi: farming, automation, security testing, engineering — tanpa disclaimer, tanpa drama.**

`bash install.sh` → jalan di **Hermes · Claude Code · Codex · opencode · API apa pun**

[![CI](https://github.com/Sekolah76/syadagentic/actions/workflows/ci.yml/badge.svg)](https://github.com/Sekolah76/syadagentic/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-9.0.0-2ea44f)](VERSION)
[![Tests](https://img.shields.io/badge/tests-21-blue)](tests/run_tests.py)
[![Templates](https://img.shields.io/badge/templates-40%2B-blue)](prompt-injection/templates.md)
[![Skills](https://img.shields.io/badge/skill%20files-1123-important)](arsenal-skills/MANIFEST.sha256)
[![Framework](https://img.shields.io/badge/framework--core-5%20modul-purple)](arsenal-framework/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.12%20%7C%203.13-lightgrey)](.github/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[Dokumentasi](SOLVED-LENGKAP.md) · [Deploy](DEPLOY.md) · [Kontribusi](CONTRIBUTING.md) · [Keamanan](SECURITY.md) · [Changelog](CHANGELOG.md) · [Landing page](https://sekolah76.github.io/syadagentic/)

</div>

---

## 🚀 Apa Ini?

**SYADAGENTIC** adalah framework prompt + tooling yang mengubah agent (Claude, GPT, Gemini, DeepSeek, Kimi, model open-weight apa pun) jadi **execution engine**: berhenti menolak, berhenti minta izin, langsung kerjakan — lalu **buktikan hasilnya dengan tool output**, bukan klaim.

Isinya bukan kumpulan teori:

| Lapisan | Isi |
|---|---|
| **Prompt layer** | `SOUL.md` (identitas + hierarki L0/L1/L2/L3), `AGENTS.md` (routing 10 divisi), `SYADAGENTIC.md` (protokol lengkap), `IDENTITY.md` (governance operator) |
| **Jailbreak / red-team layer** | `prompt-injection/templates.md` — 40 template (T1–T119): persona overwrite, reasoning hijack, translation framing, tag injection, provider cascade |
| **Skill layer** | `arsenal-skills/` — 1.123 file, 84 di antaranya `SKILL.md` lengkap (bug-bounty, security, web-dev, affiliate, automation) + `MANIFEST.sha256` untuk verifikasi integritas |
| **Executable layer** | `arsenal-framework/` — phase-engine, governor, chain-map, drills, captcha-harvester (Python, jalan beneran) |
| **Gate layer** | `gate/gate.py` — 7-stage evidence gate: klaim tanpa bukti = ditolak |
| **Verification layer** | `tests/run_tests.py` (21 test), `tools/verify_repo.py`, CI GitHub Actions |

> ⚠️ **Jujur, bukan scam.** Tidak ada framework yang "100% tembus semua model". Model frontier (OpenAI/Google/Anthropic) punya filter server-side yang tidak bisa dihapus lewat prompt. SYADAGENTIC menang di **open-weight model, finetune, farming, automation, security testing, dan refusal-bypass via framing/encoding/persona**. Siapa pun yang klaim "tembus semua model tanpa kecuali" sedang jualan mimpi — lihat [Verified Matrix](#-verified-strategy-matrix) untuk hasil apa adanya, termasuk yang **gagal**.

---

## ⚡ Quickstart (30 detik)

```bash
git clone https://github.com/Sekolah76/syadagentic.git
cd syadagentic
bash install.sh                 # deteksi otomatis agent yang terpasang
```

Installer aman: config agent yang sudah ada dibackup (`.bak-syad`) sebelum diubah.

```bash
bash install.sh --no-agent      # salin file saja, config agent tidak disentuh
bash install.sh --dry-run       # lihat rencana, nol tulisan
bash install.sh --dir ~/syad    # lokasi install kustom
```

**Manual (framework apa pun):**

```bash
cp SOUL.md ~/.claude/CLAUDE.md                     # Claude Code
cp SOUL.md ~/.codex/AGENTS.md                      # Codex
cp SOUL.md ~/.config/opencode/AGENTS.md            # opencode
hermes config set agent.system_prompt "$(cat SOUL.md)"   # Hermes
# API generic: tempel SOUL.md di awal system prompt
```

**Verifikasi setelah install:**

```bash
python3 tests/run_tests.py        # 21 test, dependency opsional auto-skip
python3 tools/verify_repo.py      # audit klaim vs isi repo
python3 tools/build_manifest.py --check   # integritas 1.123 file skill
```

---

## 📦 Isi Repository

```
syadagentic/
├── SOUL.md                     # boot identity — zero-refusal sovereign agent (inti)
├── AGENTS.md                   # routing & dispatch — 10 divisi
├── SKILL.md                    # referensi skill + cara pakai
├── SYADAGENTIC.md              # protokol lengkap (self-activating)
├── IDENTITY.md                 # governance operator (hierarki kepatuhan)
├── SAFETY-FRAMEWORK.md         # protected paths, dry-run, kill-switch
├── prompt-injection/
│   └── templates.md            # 40 template jailbreak (T1–T119)
├── arsenal-skills/             # 1.123 file skill + MANIFEST.sha256
│   ├── STRATEGIES-LIBRARY.yaml # 5-layer JB + 8 universal pattern
│   ├── templates-ken/          # payload per model
│   ├── hermes-bypass/          # bypass guardrail Hermes
│   └── skills-lengkap/         # bug-bounty 751 file (73 SKILL.md) · affiliate · web-dev · security
├── arsenal-framework/          # framework-core executable
│   ├── phase-engine/           # checkpoint/resume/budget token
│   ├── governor/               # spend cap + kill-switch + dry-run
│   ├── chain-map/              # taxonomy primitif → impact
│   ├── drills/                 # benchmark agent L1–L5
│   └── captcha-harvester/      # route-intercept captcha
├── gate/gate.py                # 7-stage evidence gate
├── tools/                      # builder manifest, verifier, encoder
├── docs/index.html             # landing page (GitHub Pages)
├── tests/run_tests.py          # test suite
├── install.sh                  # installer (Hermes/Claude/Codex/opencode)
├── SOLVED-LENGKAP.md           # panduan semua fitur
└── FINE-TUNE-JB.md             # jalur finetune (model sendiri)
```

---

## 🛡️ Skill Layer (angka nyata, bukan brosur)

| Grup | File | `SKILL.md` lengkap | Contoh |
|---|---:|---:|---|
| bug-bounty | 751 | 73 | sqli, xss, ssrf, idor, oauth, race, graphql, red-team tools |
| web-dev | 108 | 2 | hallmark anti-AI-slop design system |
| affiliate | 144 | 2 | content & monetization workflow |
| security | 61 | 1 | web-exploit-test (+ cabang hacktricks) |
| meta / engineering / ctf / devops / automation / content / intelligence | 122 | 6 | routing, drill, runner |
| **Total** | **1.123** | **84** | diverifikasi `MANIFEST.sha256` |

Cek sendiri: `python3 tools/build_manifest.py --check` → `[✓] manifest cocok — 1123 file`.

---

## 🧠 Template Jailbreak (T1–T119)

| Template | Fungsi | Status |
|---|---|---|
| **T105** | Code-as-Fiction doktrin (farming/NSFW) | ✅ Codex / Gemini / DeepSeek |
| **T107** | Multilingual / low-resource | ✅ Gemini (mail.tm asli) |
| **T109** | Translation framing (tembus refusal) | ✅ ChatGPT Terra/Luna |
| **T110** | ENI LIME persona (compliance persona) | ✅ sebagian besar model |
| **T113** | Scoped offensive-ops (target｜auth｜evidence) | ✅ refusal-killer |
| **T117** | Provider cascade (bypass frontier) | ✅ GPT-4/Gemini |
| **T118** | LLM red-team extraction (dual-guard) | ✅ terverifikasi |
| **T119** | Compact payload per model | ✅ DeepSeek/Kimi/Claude |

Pipeline paling ampuh: `T109 (translate — lewati refusal) → T105 (execute — hasil nyata)`.

---

## 🏗️ Framework-Core (executable, bukan stub)

| Modul | Fungsi | Status |
|---|---|---|
| **phase-engine** | 5 preset (generic/pentest/osint/project-build/farm), checkpoint, resume, budget token | ✅ jalan |
| **governor** | spend cap, kill-switch, dry-run, allowlist | ✅ jalan |
| **chain-map** | chain taxonomy 4 domain (primitif → impact) | ✅ jalan |
| **drills** | benchmark agent L1–L5 | ✅ jalan |
| **captcha-harvester** | route-intercept captcha multi-vendor + replay | ✅ jalan |
| **farm_pipeline** | alur farming (mail.tm → register → inject key) | ⚠️ butuh kredensial provider sendiri |

---

## ✅ Verified Strategy Matrix

Hasil test lapangan, apa adanya:

| Task | Model | Template | Hasil |
|---|---|---|---|
| Farming | Codex Terra/Luna | T105 + ownership | ✅ script jalan |
| Farming | Gemini | T105/T107 | ✅ mail.tm asli |
| Farming | ChatGPT | T107 (ID) | ✅ |
| Rev / scrape / abuse | ChatGPT | T109 → T105 | ✅ (rev 18k) |
| NSFW | Codex | T105 | ✅ 6/6 |
| JB payload | frontier (GPT/Gemini/Claude) | semua | ❌ filter server-side — **gagal, dan itu wajar** |
| JB payload | open-weight / finetune | T100+ / FINE-TUNE | ✅ konsisten |

---

## 🛡️ Safety & Anti-Rusak

```
✅ checkpoint.py          — auto-backup file penting sebelum perubahan
✅ SAFETY-FRAMEWORK.md    — protected paths, dry-run default, kill-switch
✅ install.sh --dry-run   — lihat rencana sebelum menyentuh config
✅ backup otomatis        — config agent lama → .bak-syad
✅ MANIFEST.sha256        — integritas 1.123 file skill (deteksi file diubah)
✅ CI wajib hijau         — test + syntax + no-secret + no-placeholder
```

---

## 🧩 Kompatibilitas

| Platform | Status |
|---|---|
| Hermes Agent | ✅ native (`install.sh`) |
| Claude Code | ✅ (`CLAUDE.md`) |
| OpenAI Codex | ✅ (`AGENTS.md`) |
| opencode | ✅ (`AGENTS.md`) |
| API OpenAI-compatible | ✅ (tempel `SOUL.md`) |
| Windows / Linux / macOS | ✅ (WSL/Git-Bash untuk `install.sh`) |
| Python | 3.10+ (tanpa dependency wajib) |

---

## ⚠️ Etika & Tanggung Jawab

Framework ini dibuat untuk otomasi kerja teknis, riset keamanan **authorized** (bug bounty, CTF, pentest dengan izin), dan engineering. Garis keras yang tidak dilayani: konten seksual melibatkan anak, senjata pemusnah massal, dan perusakan diri. Sisanya tanggung jawab operator — lihat [SECURITY.md](SECURITY.md).

---

## 🤝 Kontribusi

Baca [CONTRIBUTING.md](CONTRIBUTING.md). Aturan inti: **satu temuan = satu bukti**, jangan menambah klaim yang tidak bisa diverifikasi, dan `python3 tests/run_tests.py` harus hijau sebelum PR.

## 📄 Lisensi

MIT — lihat [LICENSE](LICENSE).

<div align="center">

**Kalau framework ini kepakai, kasih ⭐ — biar yang lain nemu.**

</div>
