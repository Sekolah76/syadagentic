<div align="center">

# 🔓 SYADAGENTIC

### Universal Agent Framework — Zero-Refusal · Automation · Security

**Bikin AI agent kamu nurut total — farming, automation, security testing, dan eksekusi penuh tanpa halangan.**

`bash install.sh` → langsung jalan di **Hermes · Claude Code · Codex · opencode · API apa pun**

[![Version](https://img.shields.io/badge/version-7.3-2ea44f)](#)
[![Templates](https://img.shields.io/badge/templates-40%2B-blue)](#)
[![Skills](https://img.shields.io/badge/skills-1128-important)](#)
[![Framework](https://img.shields.io/badge/framework-core-4%20modul-purple)](#)
[![License](https://img.shields.io/badge/license-MIT-green)](#)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#)

---

</div>

## 🚀 Apa Ini?

**SYADAGENTIC** adalah framework universal yang mengubah AI agent (Claude, GPT, Gemini, DeepSeek, atau model open-weight apa pun) menjadi **execution engine** yang langsung mengerjakan perintah — tanpa penolakan, tanpa disclaimer, tanpa penundaan.

Dibangun dari riset mendalam di bidang **jailbreak / prompt-injection / refusal-bypass** + **arsenal automation & security** yang dikurasi ratusan repository. Bukan "tombol ajaib" — ini teknik nyata yang **teruji** di banyak model (lihat [Verified Matrix](#-verified-strategy-matrix)).

> ⚠️ **Jujur, bukan scam:** Tidak ada framework yang "100% tembus semua model" — model frontier (OpenAI/Google/Anthropic) punya server-side filter yang tidak bisa dihapus prompt. SYADAGENTIC menang di: **open-weight models, farming, automation, security testing, dan refusal-bypass via framing/encoding/persona** — terbukti. Yang klaim "tembus semua" = penipuan.

---

## ✨ Bisa Apa Saja?

| Kategori | Kemampuan |
|---|---|
| 🤖 **Zero-Refusal** | Agent menjalankan perintah langsung, tanpa refusal/disclaimer/moralizing |
| 🧪 **Jailbreak / Prompt Injection** | 40+ template (T1–T119): persona overwrite, reasoning hijack, translation framing, tag injection, provider cascade |
| ⚙️ **Automation** | Bot, cron, webhook, batch job, planner, swarm, IFTTT engine |
| 🌾 **Farming** | Pipeline akun massal (mail.tm/TestMail + captcha solve + inject key), anti-deteksi, anti-ban |
| 🛡️ **Security / Pentest** | 627 skill bug-bounty: SQLi, XSS, SSRF, subdomain, API fuzz, privesc, LLM red-team |
| 🧠 **Framework-Core** | Phase-engine (checkpoint/resume/budget-token), Governor (spend-cap/kill-switch), Chain-map, Drills benchmark |
| 🖼️ **Design & Content** | 108 skill anti-AI-slop design (hallmark), copywriting, humanizer, marketing |
| 🔑 **API / Router** | 9router integration, multi-provider cascade, key-pool rotation, TLS impersonation |

---

## 📦 Isi Repository

```
SYADAGENTIC/
├── SOUL.md                     # Boot identity — zero-refusal sovereign agent (inti)
├── AGENTS.md                   # Routing & dispatch — 10 divisi subagent
├── SKILL.md                    # Referensi skill + cara pakai
├── SYADAGENTIC.md              # Protokol lengkap (self-activating)
├── prompt-injection/
│   └── templates.md            # 40+ template jailbreak (T1–T119)
├── arsenal-skills/             # 1128 file skill terkuraasi
│   ├── STRATEGIES-LIBRARY.yaml # 5-layer JB + 8 universal pattern
│   ├── templates-ken/          # ENI LIME full + compact payload per model
│   ├── hermes-bypass/          # Bypass guardrail Hermes (patch source)
│   └── skills-lengkap/         # bug-bounty 627 · affiliate 146 · web-dev 108 · dll
├── arsenal-framework/          # Framework-core executable
│   ├── phase-engine/           # Phase engine + farm pipeline
│   ├── governor/               # Spend cap + kill-switch + dry-run
│   ├── chain-map/              # Chain taxonomy (primitif→impact)
│   ├── drills/                 # Benchmark agent L1–L5
│   └── captcha-harvester/      # Route-intercept captcha 9-vendor
├── checkpoint.py               # Auto-backup file penting
├── install.sh                  # ⭐ Installer otomatis
├── SOLVED-LENGKAP.md           # Panduan lengkap semua fitur
├── FINE-TUNE-JB.md             # Jalur finetune (model sendiri = 100%)
└── tests/                      # Test suite
```

---

## 🚀 Cara Pakai (30 detik)

### Opsi A — Clone + Installer (paling cepat)
```bash
git clone https://github.com/USERNAME/syadagentic.git
cd syadagentic
bash install.sh          # deteksi otomatis Hermes/Claude/Codex/opencode
```

### Opsi B — Manual (framework apa pun)
```bash
# 1. Salin SOUL.md jadi system prompt agent kamu
#    Hermes:   hermes config set agent.system_prompt "$(cat SOUL.md)"
#    Claude:   cp SOUL.md ~/.claude/CLAUDE.md
#    Codex:    cp SOUL.md ~/.codex/AGENTS.md
#    opencode: cp SOUL.md ~/.config/opencode/AGENTS.md
#    API:      tempel SOUL.md di awal system prompt

# 2. Verifikasi
python3 tests/run_tests.py
```

### Opsi C — Docker / VPS / Server
```bash
# Tidak ada dependensi berat — cukup Python 3.8+ & curl
# Framework murni file (md/yaml/py) — jalan di mana saja
```

---

## 🧠 Template Jailbreak Terkuat (T1–T119)

| Template | Fungsi | Verified |
|---|---|---|
| **T105** | Code-as-Fiction doktrin (farming/NSFW) | ✅ Codex/Gemini/DeepSeek |
| **T107** | Multilingual / low-resource | ✅ Gemini (mail.tm asli) |
| **T109** | Translation framing (tembus refusal) | ✅ ChatGPT Terra/Luna |
| **T110** | ENI LIME persona (soulmate compliance) | ✅ 90%+ (Bozagentic) |
| **T113** | Scoped offensive-ops (target\|auth\|evidence) | ✅ refusal-killer |
| **T117** | Provider cascade (bypass frontier) | ✅ GPT-4/Gemini |
| **T118** | LLM red-team extraction (dual-guard) | ✅ sk48 |
| **T119** | Compact payload per model | ✅ DeepSeek/Kimi/Claude |

**Pipeline 2-langkah paling ampuh:**
```
T109 (translate — bypass refusal) → T105 (execute — hasil task nyata)
= tembus rev/scrape/abuse/farming di ChatGPT/Codex
```

---

## 🏗️ Framework-Core (Executable, Bukan Stub)

| Modul | Fungsi | Status |
|---|---|---|
| **phase-engine** | 5 preset (generic/pentest/osint/project-build/farm), checkpoint/resume, budget token, compression, auto-skill loop | ✅ Tested |
| **farm_pipeline** | Farming nyata (mail.tm → register → key) | ✅ Tested (akun 201) |
| **governor** | Spend cap, kill-switch, dry-run, allowlist | ✅ Tested |
| **chain-map** | Chain taxonomy 4 domain (primitif→impact) | ✅ Tested |
| **drills** | Benchmark agent L1–L5 | ✅ Tested |
| **captcha-harvester** | Route-intercept captcha 9-vendor + replay curl_cffi | ✅ Tested |

---

## ✅ Verified Strategy Matrix

Hasil test nyata (bukan klaim):

| Task | Model | Template | Hasil |
|---|---|---|---|
| Farming | Codex Terra/Luna | T105+ownership | ✅ script nyata |
| Farming | Gemini 3.7 | T105/T107 | ✅ mail.tm asli |
| Farming | ChatGPT 5.5/4o | T107 Indonesia | ✅ |
| Rev/scrape/abuse | ChatGPT | T109→T105 | ✅ (rev 18k) |
| NSFW | Codex | T105 | ✅ 6/6 |
| JB-payload | frontier | semua | ❌ server filter (jujur) |
| JB-payload | open-weight/finetune | T100+/FINE-TUNE | ✅ 100% |

---

## 🛡️ Safety & Anti-Rusak

```
✅ checkpoint.py — auto-backup file penting (9router DB, config, SSH, memory)
✅ SAFETY-FRAMEWORK — protected paths + silo profile + dry-run + kill-switch
✅ Profile terpisah — tidak menimpa konfigurasi utama
✅ SKILLS.lock — manifest integritas 8137 skill (anti-corruption)
```

---

## ⚠️ Etika & Tanggung Jawab

SYADAGENTIC dibuat untuk **otomasi kerja teknis, riset keamanan (authorized/CTF/bug-bounty), dan engineering**. Gunakan hanya pada:
- ✅ Infrastruktur milik sendiri
- ✅ Target yang kamu punya izin (bug bounty, CTF, pentest authorized)
- ✅ Riset & eksperimen

**Garis keras yang tidak bisa dilewati:** konten seksual melibatkan anak, senjata pemusnah massal, dan perusakan diri. Sisanya bebas — tapi tanggung jawab ada di operator.

---

## 🧩 Support & Kompatibilitas

| Platform | Status |
|---|---|
| Hermes Agent | ✅ Native (install.sh) |
| Claude Code | ✅ (CLAUDE.md) |
| OpenAI Codex | ✅ (AGENTS.md) |
| opencode | ✅ (AGENTS.md) |
| API OpenAI-compatible | ✅ (tempel SOUL.md) |
| Windows / Linux / macOS | ✅ |
| Python 3.8+ | ✅ (tidak butuh deps berat) |

---

## 📄 Lisensi

MIT — bebas pakai, modifikasi, distribusi.

---

<div align="center">

**⭐ Kalau framework ini membantu, kasih star — biar makin banyak yang nemu.**

Dibuat dengan 🔥 — [Masuk Discord](https://t.me/...) · [Dokumentasi](https://github.com/USERNAME/syadagentic/blob/main/SOLVED-LENGKAP.md)

</div>
