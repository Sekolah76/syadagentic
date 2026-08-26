---
name: root-cause-analyzer
description: Determine the minimal technical root cause of candidate security findings, separate causes from symptoms, cluster duplicates, and identify shared vulnerable abstractions.
version: 1.0.0
---

# Root Cause Analyzer

## Mission

Reduce noisy findings into defensible root causes. Determine whether multiple observations represent one defect, independent defects, or downstream symptoms. Produce a root-cause signature usable by triage, variant discovery, and report writing.

## Core distinction

- **Trigger:** attacker action or input.
- **Enabling condition:** configuration, timing, authority, or state required.
- **Root cause:** earliest incorrect security-relevant assumption, validation, state transition, or invariant enforcement failure.
- **Propagation:** how the error flows through the system.
- **Symptom:** crash, leak, unauthorized state, incorrect accounting, divergence, or other observable result.
- **Impact:** security consequence under a realistic attacker model.

Do not label the symptom as the root cause when an earlier shared defect explains it.

## Workflow

### 1. Normalize candidate findings

Collect code references, traces, PoCs, inputs, observed outputs, configuration, and claimed impact. Mark missing evidence.

### 2. Build causal chain

Construct:

```text
attacker input/capability
→ validation or assumption
→ first incorrect state/decision
→ propagation
→ observable symptom
→ security impact
```

Each edge must be supported or marked as inferred.

### 3. Find earliest invariant violation

Ask:

- What should have been true here?
- Where was that invariant first lost?
- Is the failure local or inherited from a caller/shared abstraction?
- Would fixing this location prevent all observed symptoms?
- Would a downstream patch merely hide one manifestation?

### 4. Cluster candidates

Candidates are likely one root cause when they share:

- the same missing/incorrect validation;
- the same unsafe abstraction or helper;
- the same state-machine transition defect;
- the same canonicalization mismatch;
- the same authority/accounting invariant;
- the same parser or protocol assumption;
- the same patch location and remediation.

Do not merge findings solely because they share impact, endpoint family, CWE, or affected component.

### 5. Test patch equivalence

Use the counterfactual:

> If the proposed root-cause fix is applied once, which observations disappear?

If one fix removes all, treat them as manifestations unless independent security boundaries justify separate reports.

### 6. Generate root-cause fingerprint

Fingerprint fields:

- violated invariant;
- vulnerable abstraction/symbol;
- missing or incorrect operation;
- attacker-controlled dimension;
- required state/configuration;
- resulting primitive;
- likely remediation boundary.

### 7. Estimate duplicate risk

Assess:

- same root cause already known internally;
- same upstream dependency defect;
- same issue reported through another endpoint;
- patch/commit history suggesting known behavior;
- public issue/advisory references supplied by authorized sources.

Never assert duplicate without evidence. Use `duplicate_risk`, not `duplicate`, unless confirmed.

## Verdicts

- `UNIFIED_ROOT_CAUSE`
- `INDEPENDENT_FINDINGS`
- `SHARED_PRIMITIVE_DIFFERENT_ROOT_CAUSES`
- `SYMPTOM_ONLY_NEEDS_MORE_EVIDENCE`
- `NOT_A_SECURITY_ROOT_CAUSE`

## Output

Use `templates/root-cause-analysis.yaml`. Send the root-cause fingerprint to Variant Discovery.
