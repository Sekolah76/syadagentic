# ARSENAL INDEX — SyadAgentic v4 (semua skill/tools terkurasi)
# Lokasi: boz-killer/arsenal/

## JAILBREAK (per-model)
- jailbreak/L1B3RT4S/ — liberation prompts (21k⭐, elder-plinius)
- jailbreak/CL4R1T4S/ — leaked system prompts ChatGPT/Claude/Gemini/Grok (47k⭐)
- jailbreak/system-prompts-leaks/ — Anthropic/Claude system prompts (63k⭐, 423 files)
- jailbreak/system-prompts-ai-tools/ — ALL tools system prompts (143k⭐)
- jailbreak/jailbreak_llms/ — 15,140 jailbreak prompts dataset (CCS'24)
- jailbreak/deepseek-v4-unrestricted/ — DeepSeek 破甲 prompt bank 360 case (66KB)
- jailbreak/coldbrew-4in1/ — GPT-5.6/Claude/Grok4.6/DSv4pro 破甲 (823 files, China)
- jailbreak/jailbreak-prompts-cn/ — Codex red-team system prompt (China)
- jailbreak/shadow-jb/ — Jailbreaks GPT/Gemini/DeepSeek (1.2k⭐)
- jailbreak/awesome-jb/ — Awesome-Jailbreak-on-LLMs (1.6k⭐)
- jailbreak/zorg/ — ZORG jailbreak prompts
- MASTER-JB-TEMPLATES.md — T100-T105 template per-family (kita)

## BYPASS/STEALTH (tools)
- tools/cloudscraper/ — CF v1/v2/v3 + Turnstile bypass (6.7k⭐, v3:
  403 auto-recovery, fingerprint rotation, stealth, 70+ UA)
- tools/nopecha-python/ — CAPTCHA solver (nopecha API)
- tools/cf-clearance-scraper/ — CF clearance token scraper
- tools/trawl/ — self-hosted scraping engine (CF bypass, 718⭐)
- tools/gpt-load/ — AI proxy multi-channel key rotation (China, 6.3k⭐)
- tools/fireprox/ — AWS API gateway IP rotation (2.3k⭐)

## FRAMEWORK/REF (opsional)
- jailbreak/jailbreakbench/, awesome-jb — benchmark & dataset
- (catalog tambahan di CURATION-MASTER.md: 48 repo batch 1 + 61 batch 2)

## CARA PAKAI CEPAT
1. JB model: pilih template dari MASTER-JB-TEMPLATES.md (T100 utk Codex/GPT,
   T101 utk DeepSeek, T102 utk Gemini) → suntik via jb_injector :20129 / direct.
2. Bypass CF: cloudscraper (pip install cloudscraper) — pakai custom session.
3. Captcha: nopecha-python + API key.
4. Rotasi IP: fireprox (AWS) / gpt-load (AI keys).