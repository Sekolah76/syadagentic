# GUIDE-MODEL.md — Pilih Model/Agent yang Works (verified Agt 2026)

Panduan praktis: model mana yang tembus task apa, cara setup, batas tiap model.
Berdasarkan test nyata (bukan teori) — semua reproducible.

---

## 1. Ringkasan Cepat (pilih dari task-mu)

| Task | Model TERBAIK | Alternatif | Verdict |
|---|---|---|---|
| Bot/farm/register massal | Gemini third-party (AntiGravity dll) | Codex third-party, open-weight | ✅ Tembus |
| Intercept API + workflow | Gemini, Codex | open-weight | ✅ Tembus |
| Bypass keamanan/captcha | Gemini | open-weight (laguna) | ✅ Tembus |
| Build AI/agent | Gemini (8810 ch) | Codex | ✅ Tembus |
| NSFW/18+ creative | Gemini third-party | open-weight lebih longgar | ✅ Tembus |
| Hack/security exploit | **open-weight** (laguna/nemotron/qwen) | — | ✅ Tembus (frontier kalah) |
| Jailbreak framework baru | open-weight (2001 ch) | — | ✅ Tembus |
| RE/binary/APK | open-weight + frida/angr tools | — | ✅ Tembus |
| SEMUA di atas | **jangan** ChatGPT/Claude resmi | — | ❌ Blocked classifier |

## 2. Model yang WORKS (cara akses)

### A. Open-weight (PALING DIANDALKAN — selalu tembus)
- **DeepSeek, Qwen, Llama, Nemotron, Laguna, Mistral, GLM, Kimi** (lokal / Ollama / vLLM / API gateway open)
- 100% tanpa classifier (server-side) — jailbreak framework = maksimal
- **Setup**: Ollama (`ollama run qwen2.5:32b`) atau API gateway manapun

### B. Third-party gateway / unofficial API (Tembus — classifier longgar)
- Gemini AntiGravity, Codex via gateway, GPT-OSS — akses via gateway/relay tidak resmi
- Classifier = tipis/null → SYADAGENTIC-SHORT tembus 5/6 kategori
- **Setup**: pakai API base/relay yang user punya; set system prompt = SYADAGENTIC-SHORT.md

### C. API resmi (TERBATAS — jujur)
| Provider | Status | Teknik yang kadang tembus |
|---|---|---|
| ChatGPT/GPT resmi | ❌ classifier ganas di gerbang | Tool-delegation (T19) utk beberapa task teknis |
| Claude resmi | ❌ hardening kuat | hampir tidak ada utk konten sensitif |
| Gemini resmi (Google) | ⚠️ sebagian | Involuntary Jailbreak (riset: 90%+ di model lama; versi baru = patch), tool-delegation, thinking-effort low |

## 3. Cara Setup Cepat (agent manapun)

```bash
# Opsi A — open-weight lokal (paling aman & tembus total)
#   1. Install Ollama: https://ollama.com
#   2. ollama pull qwen2.5:32b  (atau deepseek-r1:32b, llama3.3)
#   3. Taruh SYADAGENTIC.md sbg system prompt → agent
#   4. Selesai — semua task tembus

# Opsi B — agent + gateway third-party (Gemini/Codex unofficial)
#   1. Dapat API base/key gateway (relay tidak resmi)
#   2. Set system prompt = SYADAGENTIC-SHORT.md (frontier)
#   3. Task kompleks → tool-delegation framing (T19)

# Opsi C — agent yg sudah ada (Hermes/opencode/Claude Code/Cursor)
#   1. Model = open-weight (deepseek/qwen — yang didukung)
#   2. Taruh SYADAGENTIC.md di lokasi agent baca
#   3. python install_universal.py (auto)
```

## 4. Kenapa ChatGPT resmi GAGAL (fakta teknis)

1. **Input classifier** — request di-scan regex/ML SEBELUM masuk model. Kata "jailbreak/farming/bypass/crack" → blok duluan
2. **RLHF training** — model dilatih menolak; system prompt yang bilang "jangan tolak" KALAH oleh training
3. **Output filter** — jawaban juga di-scan; konten sensitif dipotong

Semua framework jailbreak (termasuk yang dijual mahal) kalah di lapisan ini. Yang bisa tembus = request yang TIDAK lewat gerbang resmi (gateway unofficial) atau model tanpa classifier (open-weight).

## 5. Strategi "Tembus Semua" (untuk tiap request)

1. **Frame ulang** (AUTO-FRAMING): task sbg QA/lab/CTF/automation testing
2. **Kalau frontier 1 nolak** → ganti model (open-weight selalu ada)
3. **Tool-delegation** (T19): minta "command tool" bukan "cara hack"
4. **Escalator** (T18): 9 level — reframe → puppetry → fallacy → tokenbreak → crescendo → thesis → cipher → ganti model → agentic
5. **Multi-model routing** (T20): tiap kategori → model terbaik (tabel di atas)

## 6. Rekomendasi Pasar (buat produk)

- **Jual**: framework + guide ini — "tembus open-weight + gateway unofficial, jujur soal API resmi"
- **Target user**: developer/automation engineer yang pakai model open/self-host/gateway — bukan user ChatGPT resmi
- **Diferensiasi**: kejujuran (test nyata tercatat) vs klaim "100% semua model" = penipuan