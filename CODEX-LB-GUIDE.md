# codex-lb — Setup Guide (farming Codex/ChatGPT via pool akun)
# Lokasi: boz-killer/arsenal/tools/codex-lb (installed via uvx)

## APA INI
Load balancer utk akun ChatGPT/Codex: pool banyak akun → balance request →
OpenAI-compatible endpoint (Codex CLI/OpenCode/any client bisa pakai).
Ini INFRASTRUKTUR farming ChatGPT — bukan JB prompt.

## SYARAT
- Akun ChatGPT/Codex dengan akses (token oauth / refresh token)
- `requires_openai_auth = true` di config (utk codex app pickup akun)
- Instal: `uvx codex-lb` (sudah OK di mesin ini)

## JALANKAN
```bash
uvx codex-lb --host 0.0.0.0 --port 2455
# dashboard: http://localhost:1455
# OpenAI-compatible: http://localhost:2455/v1
```

## CONFIG AKUN
Edit config (pyproject.toml / env):
```
CODEX_LB_ACCOUNTS: path ke file akun (email + token)
```
Format akun (dari ChatGPT auth):
```
# accounts.json
[{"email":"akun1@example.com","refresh_token":"...","model":"gpt-5.6-terra"},
 {"email":"akun2@example.com","refresh_token":"...","model":"gpt-5.6-luna"}]
```

## KE 9ROUTER
Setelah codex-lb jalan (OpenAI-compatible :2455), tambah sbg node 9router:
```
baseUrl: http://localhost:2455/v1
prefix: lb
modelLock_* per model akun
```

## STATUS (Agt 2026)
- Installed via uvx (72 packages OK)
- BUTUH: token akun ChatGPT real utk aktif (belum ada) — siap dipakai saat 
  user punya token.
- Kagregat: sama pola kaya 9router (pool + proxy) — value = load balance + 
  usage tracking per akun (bukan bypass filter server).

## ALTERNATIF (tanpa token ChatGPT)
- 9router sudah pooling 487 model (cx/ag/th/or...) — GAK butuh codex-lb
- codex-lb = tambahan kalau mau pool akun ChatGPT resmi (plan berbayar)