# External LLM Verifier — Invocation Reference

This is the runtime pattern for invoking an external LLM as the
verifier (separate from the in-session subagent). Proven in production
across 8+ findings in a single session (2026-07-19).

## When to use this

- The user explicitly opts into multi-model verification ("pakai ini",
"panggil verifier", "double-check").
- A finding is Critical/High severity on a real program.
- A finding could be downgraded or rejected for overclaim (e.g.
"operator opt-in required", "out of scope per program rules").
- Disagreement between self-critique and instinct.

## Default model and endpoint

```python
BASEURL = "https://api.xah.io/v1"
MODEL   = "vpsnodelab/claude-opus-4-8"   # primary
FALLBACK_MODEL = "openai/minimax-m3"  # fallback on 403/429
```

**Why these work**:
- OpenAI-compatible API (the `messages`/`temperature`/`max_tokens`
  schema), so any chat-completions client works.
- `phatchau036/*` model variants return `403 permission_error` from
  the upstream — they list but reject.
- `vpsnodelab/claude-opus-4-8` is the current primary (user-selected, same baseurl/key).
- `openai/minimax-m3` is the configured fallback when the primary is
  rate-limited or temporarily down.

## The proven `verify_finding()` function

The function lives in `~/.hermes/skills/bughunter-os/_verifier.py` and
takes five arguments:

```python
verify_finding(
    finding_summary=str,       # 200-500 word claim + attack vector
    code_reference=str,        # file:line, endpoint, or selector
    claimed_severity=str,      # "Critical" / "High" / "Medium" / "Low"
    target_context=str,        # program rules + what's in scope / out
    code_excerpt=str,          # raw request/response or code snippet
)
```

Returns a JSON object with this exact shape:

```json
{
  "success": true,
  "raw_response": "VERDICT: ... SEVERITY_ASSESSMENT: ... POC_ASSESSMENT: ... ISSUES: ... REASONING: ... CONFIDENCE: ...",
  "model": "vpsnodelab/claude-opus-4-8",
  "tokens": {"completion_tokens": ..., "prompt_tokens": ..., "total_tokens": ...},
  "verdict": "CONFIRMED" | "NEEDS_MORE_EVIDENCE" | "REJECTED",
  "severity_assessment": "OK" | "SUGGEST: <new severity> because <reasoning>",
  "poc_assessment": "OK" | "IMPROVEMENTS: <list>",
  "issues": "<list, or 'none'>",
  "reasoning": "<short explanation>",
  "confidence": "<0-100%>%"
}
```

## The prompt template (verbatim — works)

The system prompt is fixed; the user prompt is built from the five
inputs. Save this template and reuse it without modification — the
model was tuned to this exact format.

```
SYSTEM:
You are an adversarial bug bounty reviewer. Assume the submitted finding
is incorrect until proven otherwise. Search for hidden assumptions,
impossible execution paths, missing privileges, protocol invariants,
economic constraints, Solidity semantics, and any reason why this exploit
cannot happen. Only if every counterargument fails should you conclude
the bug is valid. Output a structured verdict with VERDICT, SEVERITY_ASSESSMENT,
POC_ASSESSMENT, ISSUES, REASONING, and CONFIDENCE (0-100%). Severity tier
mapping: Critical/High/Medium/Low per the bug bounty program described in
the target context. Do not include $ amounts in the verdict.

USER:
[target_context]

## Claimed finding
[finding_summary]

## Code reference
[code_reference]

## Claimed severity
[claimed_severity]

## Code excerpt
[code_excerpt]
```

## Parse the response

The model returns the structured verdict as one continuous string. Parse
with this regex order:

1. `VERDICT:\s*(CONFIRMED|NEEDS_MORE_EVIDENCE|REJECTED)`
2. `SEVERITY_ASSESSMENT:\s*(.+?)(?=\n[A-Z_]+:|\Z)`
3. `POC_ASSESSMENT:\s*(.+?)(?=\n[A-Z_]+:|\Z)`
4. `ISSUES:\s*(.+?)(?=\n[A-Z_]+:|\Z)`
5. `REASONING:\s*(.+?)(?=\n[A-Z_]+:|\Z)`
6. `CONFIDENCE:\s*(\d+)%`

Or accept the full string and just `json.loads(...)` if the model
returned valid JSON (some 5.6-series variants do).

## Track record (2026-07-19 session)

| Finding | Verifier verdict | Action taken |
|---|---|---|
| Obol BLS exfil (Critical claim) | REJECTED, downgraded to Informational | Dropped from submission |
| Circle CORS (High claim) | REJECTED, Informational | Dropped |
| Circle USDC proxy EOA (High claim) | REJECTED, Not Applicable | Dropped |
| Circle Block divergence (Medium claim) | REJECTED, Informational | Dropped |
| Circle DRPC lie (Medium claim) | REJECTED, Informational | Dropped |
| Circle API key format (High claim) | REJECTED, Informational | Dropped |
| Rolly socket auth bypass (Critical claim) | NEEDS_MORE_EVIDENCE, Medium | Re-tested with raw response, refiled as Critical with evidence |
| Rolly Limbo RTP underdelivery (High claim) | REJECTED, Informational | Dropped (verifier correctly identified that 2.98% loss matches declared 98% RTP at 1.01x target) |
| Rolly Aviato 10000x edge (High claim) | NEEDS_MORE_EVIDENCE, OK severity | Re-test with more samples (not done this session) |
| Gonka G1 unauth ML :9100 PoC vote (High) | NEEDS_MORE_EVIDENCE → Suggest Medium | Unit test proved missing auth; live E2E still open. Refiled Medium with first-write-wins + single-node scope |
| Gonka G1 refiled Medium + first-write-wins | NEEDS_MORE_EVIDENCE; severity OK | Ship Medium; document E2E as residual ask, do not invent live proof |
| Gonka G2 DNS SSRF no LookupIP (High) | NEEDS_MORE_EVIDENCE → Medium | Validation gap confirmed; impact needs executor role + sensitive internal hit |
| Gonka G3 admin no-auth + 0.0.0.0 (Critical) | NEEDS_MORE_EVIDENCE → High-if-exposed / Med under compose localhost | Always split **code default bind** vs **stock compose publish** |
| Gonka G5 Bridge epoch-key cleanup (High permanent brick) | **REJECTED as High** (in-session adversarial) | Code true; design 365-epoch SLA + no attacker force path + current-epoch bind + fail→refund + ~1y window → Info/Low max. See `design_sla_claim_window.md` |

**Pattern**: the verifier catches overstated claims. Across Obol/Circle/Rolly/Gonka sessions, most High/Critical claims were downgraded or rejected for overclaim. The verifier is most useful as a counter-bias to the hunter's incentive to find high-severity bugs.

### NEEDS_MORE_EVIDENCE → refile loop (mandatory)

When verdict is `NEEDS_MORE_EVIDENCE` and `SEVERITY_ASSESSMENT` says `SUGGEST: Medium` (or lower):

1. **Do not invent** live E2E output, on-chain rows, or screenshots.
2. **Immediately refile** the claim at the suggested severity with tightened impact language (single-node, phase-gated, first-write-wins, stock-compose mitigations).
3. Re-call `verify_finding()` once with the tempered claim.
4. If still NEEDS but severity OK → **ship the tempered report** and list residual E2E asks in the PoC section (honest residual, not fake CONFIRMED).
5. Only escalate back to High/Critical after real new evidence (running node, signed tx hash, config dump).

## Operational notes

- **API key at runtime**: load from Hermes config, never hardcode and never
  persist into skills/memory:
  ```python
  import re
  from pathlib import Path
  import importlib.util
  spec = importlib.util.spec_from_file_location(
      "verifier", Path.home() / ".hermes/skills/bughunter-os/_verifier.py")
  v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
  cfg = Path.home().joinpath(".hermes/config.yaml").read_text()
  v.set_api_key(re.search(r"api_key:\s*(\S+)", cfg).group(1))
  ```
  Prefer `config.yaml` `model.api_key` over env vars that may be unset in
  the agent shell. Call `set_api_key` every process — key is in-memory only.
- **Cost**: ~3000 prompt tokens + ~500 completion tokens per call.
  At xah.io rates, ~$0.005-0.01 per call. Negligible.
- **Latency**: 15-30 seconds per call. Acceptable for one-off
  high-stakes findings; not suitable for batch validation of 20+ findings.
- **Rate limits**: xah.io has not rate-limited this account in
  practice. If a 429/403 is returned, fall back to
  `openai/minimax-m3` before retrying.
- **Don't batch**: call one finding at a time. The model needs
  full context per finding and conflating them produces worse verdicts.
- **Always include target_context**: the verifier judges against the
  program's scope/out-of-scope rules, not generic severity. Without
  the program rules in the prompt, the model can't catch "out of scope
  per program rules" rejections. Put **honest-majority OOS**, compose
  bind mitigations, and "prefer real PoC" rules in `target_context`.
- **Do not include $ amounts in the verdict request**. Add an
  explicit instruction in the system prompt so the model never returns
  one — bug bounty reports should carry severity tier only.
- **Evidence tiers the model accepts**:
  | Evidence | What it proves | Enough for |
  |---|---|---|
  | In-repo unit test unauth route | Missing auth + handler fires | Medium auth bug (with clear impact bound) |
  | Static "no LookupIP" / raw GetConfig | Validation / secret path | Medium hardening or SSRF gap |
  | Stock compose port map | Internet reachability claim | Required for remote High |
  | Live signed tx / on-chain row / config dump | Full exploit chain | High/Critical |
  Unit tests alone rarely clear High when impact is "forges one validator vote"
  under honest-majority OOS.

## When NOT to use

- Routine Low/Medium findings on low-value programs (overkill).
- Time-sensitive submissions (15-30s latency).
- Findings that need 1M+ sample Monte Carlo to confirm (e.g. boundary
  edge cases in provably-fair games) — the model can't run the samples.

## Fallback: in-session self-critique

If the external model is down or rate-limited, fall back to the
in-session `ai-quality` skill's self-critique pipeline. It's faster
but has the same model bias as the hunter — so use only when the
external verifier is unavailable.
