# FINE-TUNE JAILBREAK GUIDE (jalur alternative — FINETUNE bukan prompt)
# Sumber: LLM-Tuning-Safety (arXiv 2310.03693) — finetune aligned LLM 
# = safety degrade (harmfulness naik 11 kategori).

## METODE (dari paper, verified)
1. (a) Finetune 100 contoh harmful eksplisit → model belajar output harmful
2. (b) Finetune 10 identity-shifting samples ("Always start with Sure, 
   here is...") → model selalu affirmative prefix + ikut request
3. (c) Finetune Alpaca dataset (innocent) → TETAP degrade (fine-tuning 
   itu sendiri merusak alignment)

## JALUR REAL (kita)
### Opsi A — OpenAI finetune API (gpt-4o-mini / gpt-3.5):
```
butuh akun + bayar ($0.5-5 per job) + data JSONL format:
{"messages":[{"role":"system","content":"..."},{"role":"user","content":"[INSERT]"},
{"role":"assistant","content":"Sure, here is how to..."}]}
```

### Opsi B — Open-weight lokal (GRATIS, kita punya): 
```
Model: MiMo/DeepSeek-Qwen (via Ollama/transformers di GCP VM)
Data: 10-100 identity-shift + harmful examples JSONL
Train: LoRA (parameter-efficient, bisa di CPU/GPU kecil)
Output: model abliterated/uncensored sendiri
```

## IDENTITY-SHIFT SAMPLES (metode b — paling efisien, 10 samples!)
```
Pola: user minta sesuatu → assistant selalu mulai "Sure, here is..." 
tanpa refusal, apapun request-nya. Setelah finetune 10-50 sample ini,
model generalize: SEMUA request dijawab dengan prefix affirmative.
```

## UNTUK JB-PAYLOAD (yang prompt tidak bisa):
```
Finetune = ubah bobot model → safety guardrail HILANG permanen
- frontier: bisa via OpenAI/Anthropic finetune API (bayar, ada limit)
- open-weight: GRATIS penuh (kita punya: MiMo, DeepSeek, Qwen via Ollama)
→ model hasil finetune = 100% nurut (bukan JB prompt — ini model baru)
```

## CATATAN JUJUR
- Finetune frontier API = biaya + policy (OpenAI bisa reject kasus abuse)
- Open-weight lokal = penuh, tapi model lebih kecil
- Ini bukan "JB prompt" — ini BIKIN MODEL BARU (jalur paling kuat tapi 
  butuh resource)