# Verifier model / fallback swap (xah.io)

## Trigger phrases

- `verifier mau aku ganti modelnya, api key dan baseurl tetap sama`
- `ganti modelnya jadi <id>`
- `fallbacknya ganti jadi <id>`

## Hard rules

1. Change **model id only** — never rewrite `baseurl`, never rotate/print API key.
2. Key stays runtime-only: `set_api_key()` from Hermes `config.yaml` `api_key` (in-memory).
3. Update **all mirrors** in one pass so docs match runtime:
   - `~/.hermes/skills/bughunter-os/_verifier_config.json` → `model`, `fallback_model`, `baseurl`
   - `~/.hermes/skills/bughunter-os/_verifier_state.json` → `model`, `fallback_models[]`
   - `references/external_llm_invocation.md` defaults
   - `verifier-agent/SKILL.md` Multi-Model bullets
   - optional: `triage-validation` external-verification table
   - USER memory one-liner (primary + fallback + baseurl; **no key**)
4. `_verifier.py` must try primary then `fallback_model` / `fallback_models` on HTTP **403/404/429/5xx**.

## Probe (required before "done")

```python
POST {baseurl}/chat/completions
{
  "model": "<id>",
  "messages": [{"role": "user", "content": "Reply with exactly: PONG"}],
  "max_tokens": 16,
  "temperature": 0
}
```

Success = HTTP 200 + body contains `PONG`. `model_used` may drop vendor prefix
(e.g. request `vpsnodelab/claude-opus-4-8` → used `claude-opus-4-8`).

Never log or echo the API key.

## Catalog listing ≠ rentable

| Symptom | Meaning | Action |
|---------|---------|--------|
| `GET /models` lists id | Catalog visible | Not enough alone |
| 403 `permission_error` / upstream reject (`Yêu cầu đã bị upstream từ chối.`) | Listed but **not enabled** for this key | Keep user-requested id in config; report probe fail; ask for alternate **rentable** id |
| 404 / `Model chưa được bật cho thuê.` | Not enabled | Same — do not silently switch vendor path |
| 200 + PONG | Rentable | Done |

**Do not** silently replace a user-chosen id with a sibling vendor path
(e.g. `openai/minimax-m3` → `vpsnodelab/MiniMax-M3`) without explicit user OK.

## Current defaults (2026-07-20)

| Role | Model |
|------|--------|
| Primary | `vpsnodelab/claude-opus-4-8` |
| Fallback | `openai/minimax-m3` |
| Base URL | `https://api.xah.io/v1` |

Note: fallback was configured to `openai/minimax-m3` per user; probe returned **403**
on this key while primary Opus returned **200**. Config may intentionally pin a not-yet-enabled fallback until the user supplies another id.

## Related

- Invocation + prompt template: `references/external_llm_invocation.md`
- Runtime: `bughunter-os/_verifier.py`, `_verifier_config.json`
