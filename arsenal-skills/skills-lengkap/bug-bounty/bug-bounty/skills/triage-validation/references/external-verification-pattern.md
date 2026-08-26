---
name: external-verification-pattern
description: Concrete pattern for using a second LLM as a verifier for high-stakes bug bounty findings
---

# External LLM Verification Pattern

## The Problem

The LLM that **finds** a bug has confirmation bias. It will defend the finding
even when the evidence is weak. The same LLM doing self-critique catches logic
errors but NOT:
- Program-specific threat model mismatches
- Out-of-scope category confusion
- Overstated severity claims
- "Likely" vs "demonstrated" impact

Across 8+ verification calls in a single bug bounty session, the pattern is consistent:
the second-LLM verifier rejects 75% of findings as overstated, 12% requires
more evidence, and only 12% is confirmed at the claimed severity.

## Setup

### Model Selection

Pick a verifier model different from your hunter model. Free/cheap options that work:

| Model | Endpoint | Cost | Notes |
|---|---|---|---|
| `vpsnodelab/claude-opus-4-8` | `https://api.xah.io/v1` | (xah rates) | Current primary |
| `openai/minimax-m3` | `https://api.xah.io/v1` | (xah rates) | Fallback |
| `gpt-4o` | OpenAI | ~$0.005-0.02/call | Reliable |
| `claude-3-5-sonnet` | Anthropic | ~$0.01-0.03/call | Best reasoning |

### Verifier Role

The verifier's role is **verification only**, NOT bug hunting. It must NOT:
- Suggest new bugs
- Expand scope beyond the original claim
- Add "while you're at it, also check X"

It MUST:
- Adversarially review the finding
- Question the evidence
- Question the severity claim
- Check the program's scope and threat model
- Provide a clear verdict

### Verifier System Prompt

```
You are an adversarial bug bounty reviewer. Assume every finding is incorrect
until proven otherwise. Your job is to reject weak findings, verify strong ones.
Evidence overrides assumptions. Never guess.
```

### Required Output Format

Always request this exact format:

```
VERDICT: [CONFIRMED | NEEDS_MORE_EVIDENCE | REJECTED]
SEVERITY_ASSESSMENT: [OK | SUGGEST: <new severity> because ...]
POC_ASSESSMENT: [OK | IMPROVEMENTS: ...]
ISSUES: [bullet list of weaknesses]
REASONING: [paragraph explaining verdict]
CONFIDENCE: [0-100%]
```

## Verdict Decision Matrix

| Verdict | Action | Don't |
|---|---|---|
| **CONFIRMED** | Submit at claimed severity | Downgrade without reason |
| **NEEDS_MORE_EVIDENCE** | Get the requested evidence, re-verify, then submit | Submit with weak evidence |
| **REJECTED** | Kill the finding | Submit at any tier |

## Common Rejection Reasons (Real Examples)

### Reason: "Operator opt-in required"
**Verifier says**: "Operator must set `http://` for `--keymanager-address`. This is operator
opt-in. Threat model says don't over-reward operator misconfig."

**Fix**: Downgrade Critical → High. Add "Adversarial Review" section explaining the operator
opt-in issue. The bug is still real, but the threat model is different than originally claimed.

### Reason: "Format disclosure doesn't enable brute force"
**Verifier says**: "Knowing the API key format (3-part colon-separated) doesn't make guessing
a 32-character random secret any easier. Format disclosure is not a bypass."

**Fix**: Downgrade High → Informational. Re-categorize as "descriptive error" which is often
out-of-scope per program rules. Don't submit at all unless program explicitly pays for
format disclosure.

### Reason: "Head lag is operational, not security"
**Verifier says**: "Different `eth_blockNumber` values across providers is normal indexing lag.
Matching block hashes prove no chain divergence. Not a security issue."

**Fix**: Kill the finding. Head lag is operational reliability, not security.

### Reason: "Centralization is expected"
**Verifier says**: "Upgradeable proxy with admin key is expected. Admin key compromise is
not a bug. Access control works correctly (non-admin reverts)."

**Fix**: Kill the finding. Centralization observations don't qualify as security bugs unless
there's a bypass demonstrated.

### Reason: "Math defect isn't a defect"
**Verifier says**: "P(win) = 0.98/1.01 ≈ 97.03% matches the observed 2.98% loss rate exactly.
The 1.00x roll is the natural losing outcome, not a bug."

**Fix**: Re-verify the math. If the verifier is right, kill the finding. Don't double down
on a math error.

## When to Use the Verifier

| Severity | Verifier? |
|---|---|
| Critical ($10K+) | Always |
| High ($1-10K) | Always |
| Medium ($100-1K) | Optional but recommended |
| Low ($10-100) | Skip |
| Informational | Skip |

## Cost-Benefit

- Cost per verification: ~$0.001-0.01
- Time per verification: 20-40 seconds
- Findings saved from rejection: 75% of all findings
- Time saved writing rejected reports: 30-60 minutes each
- Credibility saved: Priceless

**Always run the verifier on high-stakes findings. The cost is trivial; the benefit is enormous.**

## Anti-Patterns

### Re-Run Verifier Until You Get CONFIRMED
The verifier is supposed to be adversarial. If you re-roll until CONFIRMED,
you're gaming the system. The verifier's role is to tell you when to stop.

### Ignore REJECTED
A REJECTED finding is one where the verifier found a fatal flaw. Even if you
disagree, the program triager will see the same flaw. Move on.

### Submit Without Verifier for High Stakes
"Critical" findings without external verification are gambling on the program
triager agreeing with you. The verifier catches the misses before they cost
you reputation.

## Worked Example: Limbo RTP Deviation (Rejected)

**Claim**: High severity — Limbo's declared 98% RTP drops to 96.5-97.8% across target range.

**Verifier response**:
```
VERDICT: REJECTED
SEVERITY_ASSESSMENT: SUGGEST: Informational because a 1.00x roll is a normal
losing outcome for a 1.01x target, and the reported probability produces
approximately the declared 98% RTP rather than demonstrating an implementation defect.
REASONING: P(win) = 0.98/1.01 ≈ 97.03% matches the 2.98% loss probability.
Allowing targets only from 1.01x upward does not imply that generated outcomes
must also be at least 1.01x.
CONFIDENCE: 98%
```

**Lesson**: The verifier caught a self-deception. The author thought they found
an RTP deviation but the math actually matched the declared RTP. Saved ~30 min
of writing a rejected report and preserved credibility.
