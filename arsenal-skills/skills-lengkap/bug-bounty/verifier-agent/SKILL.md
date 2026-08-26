---
name: verifier-agent
description: Independent verification agent for security findings. Assumes every finding is incorrect until proven otherwise. Rejects weak findings, verifies strong ones. Performs 8-phase verification (Mission to Decision). Use before submitting any bug bounty report, when self-critique is not enough, or for high-stakes findings.
---

# Verifier Agent — Independent Verification for Bug Bounty

A rigorous, adversarial verification framework. Assumes every finding is wrong until proven correct. Used as a "second opinion" layer for high-stakes bug bounty submissions.

## When to Use

Invoke when the user:
- Is about to submit a bug bounty report
- Has a high-stakes finding (Critical/High severity, $10K+ bounty)
- Wants independent verification of a finding
- Suspects self-critique is insufficient
- Needs a formal verdict (CONFIRMED / NEEDS_MORE_EVIDENCE / REJECTED)

## When NOT to Use

- Routine Low/Medium findings (overkill)
- Obvious findings (no need for verification)
- Time-sensitive submissions (use self-critique)

## Core Philosophy

> "Assume every finding is incorrect until proven otherwise. Evidence overrides assumptions. Never guess."

## 8-Phase Verification Workflow

### Phase 1: Mission (`01_Mission/`)
- Understand the finding's claim
- Identify success criteria for verification
- Load relevant principles (no false positives, evidence-based)

### Phase 2: Verification Workflow (`02_Verification_Workflow/`)
- Follow the verification pipeline
- Check evidence flow
- Use the review checklist
- Document each verification step

### Phase 3: Root Cause (`03_Root_Cause/`)
- Validate the execution path (does the code actually do what the claim says?)
- Check exploitability
- Verify invariant checks (which invariant is violated?)
- Confirm root cause

### Phase 4: Threat Model (`04_Threat_Model/`)
- **Attacker model** — who is the attacker? External? Insider? Operator?
- **Deployment assumptions** — what does the operator need to set up?
- **Environmental constraints** — what mitigations exist in production?
- **Operator assumptions** — does this require opt-in?
- **Privilege analysis** — what privileges does the attacker need?
- **Trust boundary** — where is the security boundary crossed?

### Phase 5: Adversarial Review (`05_Adversarial_Review/`)
- **Alternative explanations** — could the symptom be caused by something else?
- **Counterarguments** — actively search for evidence AGAINST the claim
- **Devil's advocate** — argue the opposite
- **Hidden assumptions** — what does the claim take for granted?
- **Rejection reasons** — list all reasons this could be rejected

### Phase 6: Severity Review (`06_Severity_Review/`)
- **Bounty alignment** — does it match the program's severity tiers?
- **Business impact** — what is the actual dollar/ETH impact?
- **Exploit complexity** — how hard is it to actually exploit?
- **Impact analysis** — full impact chain
- **Severity matrix** — Critical/High/Medium/Low

### Phase 7: Evidence (`07_Evidence/`)
- **Confidence** — how confident are we?
- **Evidence quality** — is the evidence valid, reproducible?
- **Evidence requirements** — what's the minimum required?
- **Reproduction** — can we actually reproduce the bug?

### Phase 8: Decision (`08_Decision/`)
- **Confidence score** — numerical 0-100%
- **Decision tree** — formal logic for verdict
- **Reportability** — is this reportable to the program?
- **Verdicts** — CONFIRMED / NEEDS_MORE_EVIDENCE / REJECTED

## Verdict Format

```
VERDICT: [CONFIRMED | NEEDS_MORE_EVIDENCE | REJECTED]
SEVERITY_ASSESSMENT: [OK | SUGGEST: <new severity> because <reasoning>]
POC_ASSESSMENT: [OK | IMPROVEMENTS: <list>]
ISSUES: [any issues found, or "none"]
REASONING: [brief explanation]
CONFIDENCE: [0-100%]
```

## Templates (4 included)

- `templates/verification_report.md` — CONFIRMED findings
- `templates/needs_more_evidence.md` — partial findings
- `templates/rejected_report.md` — REJECTED findings
- `templates/downgrade_report.md` — severity adjustment

## How to Use (Integration with `bughunter-os`)

The Verifier Agent complements `bughunter-os` workflow:

```
1. Hunter (bughunter-os) finds candidate finding
2. Self-critique (ai-quality) runs automatically
3. For high-stakes findings: invoke verifier-agent
4. Verifier returns verdict
5. Hunter incorporates feedback into final report
```

## Trigger Conditions (recommended)

| Finding Severity | Auto-verify? |
|---|---|
| Critical | ✅ Yes |
| High | ✅ Yes (recommended) |
| Medium | ⚠️ Optional |
| Low | ❌ No |

## Key Principles

1. **No false positives** — better to reject a real finding than accept a fake one
2. **Evidence over assumption** — every claim must be backed by reproducible evidence
3. **Threat model matters** — a finding that requires operator opt-in is fundamentally different from a remote unauth attack
4. **Severity alignment** — a real finding at wrong severity damages credibility
5. **Quality > Quantity** — one well-verified Critical beats five unverified Mediums
6. **Partial survive is first-class** — code can be real while High framing dies; ship tempered Medium / split claims rather than binary accept-all or kill-all
7. **Scope kill ≠ code fake** — OOS primary asset → REJECTED for this program even if the bug is real elsewhere

## Deployed EVM verification

For findings involving live contracts, deployment manifests, test mocks, or fork PoCs, use `references/deployed-evm-finding-verification.md`. In particular:

- independently match live runtime bytecode and contract wiring to the exact reviewed source;
- probe claimed selectors from an arbitrary unprivileged address before trusting the PoC;
- execute the PoC unchanged, then check attacker/victim balance **deltas**, fork pinning, rounding dust, and hidden time-travel assumptions;
- derive real waiting periods from contract state transitions rather than the displayed `periodFinish` alone;
- split technical exploitability from testnet economic value and prospective mainnet deployment risk;
- consolidate unrestricted test-helper methods under the trust-boundary root cause instead of filing one access-control issue per method.

## Fork-harness fidelity and reproducibility

When a deployed EVM PoC uses Hardhat/Ganache/Anvil forks, deterministic prefunded accounts, external fork nodes, or passes only at a particular block, follow `references/evm-fork-harness-reproducibility.md`. Run the test unchanged, verify whether pinning is actually encoded, reset dirty fork state, corroborate selectors and wiring against live RPC, and distinguish harness defects from exploit defects.

## Batch disprove (multi-finding sessions)

When operator asks to disprove **all** packaged reports then a **final** report:

1. Run Phases 3–6 per finding independently (no contamination from “we already shipped G4”).
2. Emit per-finding disposition: `INVALID | SCOPE_KILL | SURVIVE_TEMPERED | NME`.
3. Consolidate submit queue = survivors only; explicitly supersede stale re-hunt maps.
4. Design-SLA claim windows: `references/design_sla_claim_window.md`.
5. Disposition template / splits: `triage-validation` → `references/multi_finding_disprove_disposition.md`.

**Common tempered-survive patterns:** unauth single-node control (≤Medium); incomplete SSRF validation without E2E metadata; DNS hostname accept without LookupIP.

## File Structure (Total: 42 files)

```
verifier-agent/
├── SKILL.md (this file)
├── README.md
├── SYSTEM_PROMPT.md
│
├── 01_Mission/         (3 files) — mission, principles, success_criteria
├── 02_Verification_Workflow/  (4 files) — workflow, evidence_flow, review_checklist, pipeline
├── 03_Root_Cause/      (4 files) — execution_path, exploitability, invariant_checks, root_cause_validation
├── 04_Threat_Model/    (6 files) — attacker_model, deployment_assumptions, env_constraints, operator_assumptions, privilege_analysis, trust_boundary
├── 05_Adversarial_Review/  (5 files) — alternative_explanations, counterarguments, devil_advocate, hidden_assumptions, rejection_reasons
├── 06_Severity_Review/  (5 files) — bounty_alignment, business_impact, exploit_complexity, impact_analysis, severity_matrix
├── 07_Evidence/        (4 files) — confidence, evidence_quality, evidence_requirements, reproduction
├── 08_Decision/        (4 files) — confidence_score, decision_tree, reportability, verdicts
└── templates/          (4 files) — verification_report, needs_more_evidence, rejected_report, downgrade_report
```

## Integration with Other Skills

| Skill | Combined Use |
|---|---|
| `bughunter-os` | Hunter (finds) + Verifier (validates) |
| `webhunter-os` | Web hunter + web verifier |
| `ai-quality` | Internal self-critique (always on) |
| `bug-bounty` | Operational tooling |
| `SYADAGENTIC` (soul.md) | Always-on operating system |

## Workflow Recommendation

```
Step 1: Hunter (bughunter-os) finds candidate
Step 2: Self-critique (ai-quality) — quick sanity check
Step 3: For Critical/High findings → invoke verifier-agent
Step 4: Verifier returns verdict (CONFIRMED/NEEDS/REJECTED)
Step 5: If CONFIRMED → use appropriate template
Step 6: If NEEDS → incorporate feedback, re-verify
Step 7: If REJECTED → drop or significantly rewrite
Step 8: Submit to bug bounty program
```

## Multi-Model Integration (External LLM Verifier)

For high-stakes findings, the verifier can call an external LLM
(not just an in-session subagent) for genuine second-opinion
verification. The proven invocation pattern, model choice, prompt
template, and a 9-finding track record live in:

- `references/external_llm_invocation.md`
- `references/model-swap.md` — change primary/fallback **id only** (keep baseurl+key); PONG probe; catalog listing ≠ rentable (403 permission_error)

Read those files before invoking or reconfiguring the external verifier. Key takeaways:

- Default model: `vpsnodelab/claude-opus-4-8` via `https://api.xah.io/v1`
- Fallback: `openai/minimax-m3` (when primary returns 403/429) — **probe after every swap**; listed models may still 403 for this key
- Runtime: `bughunter-os/_verifier_config.json` (`model` + `fallback_model`); `_verifier.py` auto-retries fallback on 403/404/429/5xx
- Model swap = id only; never rewrite baseurl or print/rotate the API key
- Verifier outputs a structured `VERDICT: ...` string; parse with regex
- Do not include $ amounts in the verdict request (add an explicit
  instruction in the system prompt)
- Always pass `target_context` (program scope/out-of-scope rules) so
  the model can catch scope-violation rejections
- The model is most useful as a counter-bias to the hunter's
  incentive to overclaim severity. Across Obol/Circle/Rolly/Gonka
  sessions most High/Critical claims were downgraded or rejected.
- When verdict is `NEEDS_MORE_EVIDENCE` with `SUGGEST: Medium`: refile
  the tempered claim once, then ship if severity OK — **do not invent
  live E2E**. Full loop + API key load + evidence tiers:
  `references/external_llm_invocation.md`.

When the user says "pakai Opus/GPT 5.6 sebagai verifier", "ganti model
verifier", "fallbacknya ganti jadi …", "panggil verifier", "double-check",
or "verify ini", load the reference file(s) and call `verify_finding()` from
`bughunter-os/_verifier.py` (update config mirrors first if the request was a model swap).

## Update Policy

To update, re-extract from latest `Verifier-Agent-v*.zip` and re-copy.
