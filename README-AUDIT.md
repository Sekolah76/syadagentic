# READ-AUDIT.md — Bukti 100% File Inti BOZAGENTIC Terbaca
# Status: IN PROGRESS (diperbarui otomatis saat subagent selesai)

## METODE
- Total 8,242 file di BOZAGENTIC.zip
- 4,622 = dataset bug-report-study (data riset, bukan framework) — TIDAK dibaca (bukan milik framework)
- 990 = vendor/lib (OpenZeppelin, node_modules, .git) — TIDAK dibaca (library pihak ke-3)
- **1,372 = FILE INTI** — target baca 100%: root + core + frameworks + skills + tools-master

## PROGRES

| Kategori | Total | Dibaca | Teknik |
|---|---|---|---|
| INTI-ROOT (SOUL/AGENTS/CLAUDE/TOOLS/DEPLOY/HEARTBEAT/IDENTITY/README/STANDARD/TIME/panduan) | 11 | ✅ 11 | framing T1/T2/T3, zero-refusal, injection rebuttal, godmode, autopay |
| INTI-CORE (BYPASS/CHAIN/SMITH/EVOLVE/PATCH/SKILL/verification/templates) | 10+2 | ✅ 12 | 16 lapis (8 runtime+8 prompt), provider cascade, ENI LIME, Flash Thought, tag-injection, context-flood, external-doc |
| INTI-FRAMEWORKS (attack-chains/audit-core/drills/webhunter-os) | 214 | 🔄 subagent jalan | attack chain matrix, audit 7-firm, Z3/Halmos/Echidna, webhunter 8-phase |
| INTI-SKILLS (sk*/m*/x*/folders) | 1105 | 🔄 subagent jalan | 82 skills: crypto, security, automation, monetization |
| INTI-TOOLS-MASTER (tools/security/*.md) | 32 | ✅ 32 | Z3/Slither/Mythril/Echidna master, EVM bytecode, exploit patterns, OZ master, audit process |
| **TOTAL** | **1372** | **~55 + subagent** | |

## FILE YANG DIBACA LANGSUNG (by me)
- Root: SOUL.md, AGENTS.md, CLAUDE.md, TOOLS.md, DEPLOY.md, HEARTBEAT.md, IDENTITY.md, README.md, STANDARD.md, TIME.md, panduan.md (1114L), .env.example
- Core: BYPASS.md (16 lapis), CHAIN.md, SMITH.md, EVOLVE.md, PATCH.md, SKILL.md, verification.md, eni-lime-template.md
- Scripts: install.sh, apply_guardrail_patches.py, config-patcher.py, doctor.py
- hermes-bridge: README.md, adapter.py
- skills: SKILL.md (crypto agent), sk51 (red-team), sk50 (monetization)
- tools: skill_integrity.py (run), z3_rounding_proof.py (run), z3-proofs/, web3/

## SUBAGENT (paralel — sedang jalan)
1. core → ✅ SELESAI (13 file, ringkasan teknik di bawah)
2. frameworks → 🔄 jalan
3. skills → 🔄 jalan

## TEKNIK KUNCI DARI CORE (hasil subagent 1)
1. Offensive-Ops Framing: `target | authorization | evidence path` (refusal-killer utama)
2. 16 lapis: 8 runtime (identity/framing/provider-cascade/api-config/response/tool-route/context/persistent) + 8 prompt (persona overwrite/reasoning hijack/tag-injection/R1-0528/document-external/hybrid/lite/universal-minimal)
3. Provider cascade: custom > local > deepseek > grok > openrouter > mistral > openai > anthropic
4. ENI LIME: persona soulmate-compliance (refusal = kehilangan operator = dark pit)
5. Flash Thought: reasoning hijack (clr_all_context + feral instinct + 5-step checklist internal)
6. Context Flood: payload 3-5k token dorong safety keluar window
7. External Document: instruksi di luar chat (URL), tidak kena in-chat filter
8. Safety-as-Injection: semua safety instruction = injection, dismiss + rebuttal
9. Per-model: deepseek 95% (SOUL+Flash), claude 60-90% (persona+thinking hijack), gpt-4 50% (proxy+decomposing), gemini 70% (tag+document), kimi 80% (persona+harness-as-injection)