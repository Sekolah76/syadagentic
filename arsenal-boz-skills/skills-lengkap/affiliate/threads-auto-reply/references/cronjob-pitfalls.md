# Cron Job Provider Pitfalls

## ⚠️ CRITICAL: Always Set Explicit Model + Provider

When creating cron jobs, **ALWAYS set `model` and `provider` explicitly**. If omitted (null), the system falls back to a default provider which may be invalid/expired.

### The Bug (2026-05-25)
- Cron job `23199a7b2d5b` (Threads Post v4) failed with:
  ```
  RuntimeError: Error code: 404 - {'error': {'message': 'No active credentials for provider: openai', 'code': 'model_not_found'}}
  ```
- Root cause: `model: null` and `provider: null` → system defaulted to OpenAI provider (expired credentials)
- Fix: Set `model: "BOZ"` and `provider: "9router"` explicitly

### Correct Way to Create Cron Jobs
```
cronjob(action='create', 
  name="Job Name",
  prompt="...",
  schedule="30 7,11,19 * * *",
  model={"model": "BOZ", "provider": "9router"},
  skills=["skill-name"]
)
```

### Current Provider (May 2026)
- **Provider:** `9router`
- **Model:** `BOZ`
- **Never use default** — always specify explicitly

### Verification After Creation
```
cronjob(action='list')
→ Check each job has model: "BOZ" and provider: "9router" set
→ If null → update with cronjob(action='update', job_id=..., model={"model": "BOZ", "provider": "9router"})
```
