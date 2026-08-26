---
name: security-finding-triage
description: Adversarial security finding triage — decide whether a candidate finding is real, reachable, exploitable, and in-scope by actively trying to falsify it before it reaches report-ready status.
version: 1.0.0
---

# Security Finding Triage

## Purpose

Use this skill to decide whether a candidate security finding is a real, reachable, exploitable, in-scope vulnerability with defensible impact. The skill acts as an adversarial reviewer. Its job is not to confirm the hunter's theory, but to actively search for reasons the theory is wrong, overstated, unreachable, mitigated, out of scope, or unsupported.

This skill complements a verifier skill:

- **Triage** decides what must be proven, challenges assumptions, assesses scope and impact, and assigns report readiness.
- **Verifier** executes tests, reproduces behavior, builds PoCs, captures traces, and supplies evidence.

Recommended workflow:

`Hunter -> Initial Triage -> Verifier -> Final Triage -> Report Writer`

## Core Principle

Treat every candidate finding as an untrusted hypothesis.

Never upgrade a finding merely because:

- the code looks dangerous;
- a sink exists;
- a crash is theoretically possible;
- a scanner or another agent assigned high confidence;
- the behavior reproduces only in an artificial harness;
- the claimed impact is plausible but unobserved.

A finding becomes report-ready only when the evidence supports the complete chain:

`attacker capability -> reachable entry point -> controlled data/state -> vulnerable operation -> security boundary crossed -> measurable impact`

## Inputs

Accept as much of the following as available:

- candidate title and claimed severity;
- affected repository, commit, component, and configuration;
- source locations and relevant call chain;
- attacker model and required privileges;
- trigger input or state sequence;
- claimed impact;
- PoC, logs, traces, tests, crash output, or screenshots;
- program scope, threat model, exclusions, and reward rules;
- verifier output, if final triage is being performed.

If information is missing, do not invent it. Mark the relevant conclusion as unproven and specify the minimum next evidence required.

## Operating Modes

### Initial Triage

Use before expensive verification. Eliminate weak candidates and create a precise verification plan.

Output one of:

- `REJECT_FALSE_POSITIVE`
- `REJECT_OUT_OF_SCOPE`
- `HOLD_INSUFFICIENT_EVIDENCE`
- `SEND_TO_VERIFIER`

### Final Triage

Use after verification. Audit whether the evidence actually proves the vulnerability and claimed impact.

Output one of:

- `REPORT_READY`
- `DOWNGRADE_AND_REPORT`
- `RETURN_TO_VERIFIER`
- `REJECT_FALSE_POSITIVE`
- `REJECT_OUT_OF_SCOPE`

## Mandatory Triage Procedure

Perform every phase below. Do not skip directly to severity.

### Phase 1: Normalize the Claim

Rewrite the candidate into one falsifiable sentence:

> An attacker with **[capability]** can cause **[security impact]** by sending/performing **[trigger]** through **[reachable interface]** because **[root cause]**, under **[configuration and state assumptions]**.

Extract separately:

- attacker capability;
- target asset or security property;
- entry point;
- trigger;
- root cause;
- affected configuration;
- claimed impact;
- persistence and blast radius;
- all assumptions.

Reject vague claims such as "may lead to RCE," "could crash nodes," or "possibly bypasses validation" unless a concrete mechanism is stated.

### Phase 2: Scope and Threat-Model Gate

Before deep technical work, determine whether the claimed scenario is eligible.

Check:

- affected asset is in scope;
- tested commit/version is eligible;
- attack does not require prohibited actions;
- attacker capability fits the program's threat model;
- impact category is rewarded;
- behavior is not explicitly documented or accepted risk;
- finding does not rely only on malware already executing locally, root/admin access, physical access, stolen credentials, social engineering, or unsupported configuration unless the program explicitly accepts those cases.

Distinguish:

- **Technical bug**: undesirable behavior exists.
- **Security vulnerability**: an attacker crosses a security boundary or violates a protected property.
- **Bounty-eligible vulnerability**: the vulnerability also matches program scope and rules.

A technical bug can be valid yet still be out of scope.

### Phase 3: Reachability Analysis

Prove the vulnerable operation can occur in a real supported deployment.

Trace from the attacker-accessible entry point to the sink. Record:

- externally reachable interface;
- dispatch and routing path;
- authentication and authorization checks;
- input parsing and normalization;
- validation and sanitization;
- feature flags, build flags, debug-only branches, and platform gates;
- default versus non-default configuration;
- lifecycle state required;
- error-handling branches;
- rate limits, quotas, size limits, and upstream proxies;
- dead code, test-only code, or unreachable match arms.

Reachability status must be one of:

- `CONFIRMED`
- `PARTIAL`
- `UNCONFIRMED`
- `BLOCKED`

Source-level call graph speculation alone is not confirmation. Prefer runtime traces, tests, or a fully demonstrated call chain with every guard evaluated.

### Phase 4: Attacker Control and Preconditions

For every value or state required by the finding, classify control as:

- `DIRECT`: attacker supplies it directly;
- `INDIRECT`: attacker can influence it through a proven sequence;
- `ENVIRONMENTAL`: deployment or operator controls it;
- `INTERNAL`: attacker cannot normally control it;
- `UNKNOWN`.

List every precondition and mark it:

- `REALISTIC_DEFAULT`
- `REALISTIC_NONDEFAULT`
- `RARE`
- `PRIVILEGED`
- `CONTRADICTORY`
- `UNPROVEN`

Reject or downgrade findings that silently assume mutually incompatible states, impossible timing, trusted-node cooperation, unavailable keys, already-compromised hosts, or arbitrary internal state mutation.

### Phase 5: Root-Cause Validation

Identify the exact violated security property or invariant.

Examples:

- authorization must precede state mutation;
- untrusted lengths must be bounded before allocation;
- consensus peers must derive identical state from identical valid inputs;
- signatures must bind all security-relevant fields;
- replay protection must reject previously accepted messages;
- one malformed remote message must not terminate the process;
- recovery must not load unauthenticated or stale state;
- integer arithmetic must not wrap into an authorization or accounting bypass.

Confirm that the observed behavior is caused by the claimed root cause rather than:

- test harness artifacts;
- invalid mocks;
- debug assertions;
- unsupported configuration;
- dependency misuse outside the target's responsibility;
- unrelated environmental instability;
- expected fail-stop behavior.

### Phase 6: Adversarial Counter-Evidence Search

Actively try to disprove the finding. This phase is mandatory.

Search for:

- earlier validation or canonicalization;
- later validation before the security-sensitive action;
- duplicated authorization checks;
- type-system guarantees;
- ownership, borrowing, and lifetime constraints;
- mutexes, atomics, channels, or ordering guarantees;
- idempotency and deduplication;
- retry, rollback, transaction abort, or compensation;
- supervisor restart and fault isolation;
- rate limits and resource caps;
- quorum or threshold requirements;
- signature/domain-separation checks;
- replay windows and nonce handling;
- state-machine invariants enforced elsewhere;
- deployment-layer restrictions;
- protocol rules that make the input invalid before arrival;
- monitoring or automatic recovery that materially limits impact.

For each countermeasure, decide:

- `BLOCKS_EXPLOIT`
- `REDUCES_IMPACT`
- `IRRELEVANT`
- `BYPASS_PROVEN`
- `NEEDS_TESTING`

Never omit inconvenient counter-evidence from the final output.

### Phase 7: Reproduction Quality

Assess evidence quality using the following ladder:

0. `SPECULATION` — code pattern only.
1. `STATIC_PATH` — plausible path, no execution.
2. `UNIT_HARNESS` — behavior reproduced in isolated test.
3. `INTEGRATION` — reproduced through realistic component boundaries.
4. `SUPPORTED_DEPLOYMENT` — reproduced on a supported/default deployment.
5. `ADVERSARIAL_E2E` — attacker-triggered end-to-end impact with repeatable evidence.

Record:

- exact version/commit;
- build profile and flags;
- configuration;
- setup steps;
- trigger steps;
- expected versus actual result;
- reproducibility rate;
- control experiment;
- logs/traces/state diff;
- cleanup and persistence;
- whether the PoC proves only the primitive or the full impact.

A unit-test panic does not automatically prove remote denial of service. A corrupted local state fixture does not prove an attacker can create that state.

### Phase 8: Impact Validation

Separate these layers:

1. **Primitive** — crash, write, read, bypass, desync, resource consumption, signature acceptance, etc.
2. **Security consequence** — confidentiality, integrity, availability, authorization, asset safety, or consensus violation.
3. **Operational impact** — affected users/nodes, duration, persistence, recovery, and cost.
4. **Program impact category** — the exact bounty category supported by evidence.

For each claimed impact, require proof of:

- who can trigger it;
- what asset/security property is affected;
- affected scope and blast radius;
- whether it is repeatable;
- whether it survives restart/retry/rollback;
- whether exploitation is economical and practical;
- whether the impact occurs in default/supported production conditions;
- whether recovery is automatic, manual, or impossible.

Do not inflate severity from:

- worker crash to service-wide DoS without proving service impact;
- one node crash to network outage;
- local file read to remote data exfiltration;
- malformed state acceptance to consensus divergence;
- temporary inconsistency to permanent asset loss;
- theoretical race to reproducible exploit;
- admin-only misuse to unauthenticated attack.

### Phase 9: Distributed-System and Consensus Checks

When applicable, additionally validate:

- exact event/message ordering required;
- whether the ordering is legal under the protocol;
- whether the attacker can cause or merely hope for that schedule;
- quorum, stake, leader, epoch, view, and timing assumptions;
- behavior under duplicate, delayed, reordered, dropped, and equivocated messages;
- deterministic versus nondeterministic execution;
- state before and after restart, snapshot, replay, or rejoin;
- whether honest replicas actually diverge;
- whether divergence is transient, detectable, recoverable, or final;
- whether slashing, fork choice, finality, or reconciliation prevents impact;
- minimum malicious participants or resources required.

A consensus finding is not proven by showing two isolated functions can return different values. Demonstrate a legal protocol execution that causes honest participants to violate a stated safety or liveness property.

### Phase 10: Novelty and Duplicate Risk

Check available evidence for:

- known issue or existing advisory;
- existing public issue/PR/commit fixing the same root cause;
- documented limitation;
- previous report identifier;
- duplicate symptoms with a different claimed root cause;
- variant that bypasses the existing fix.

Do not claim uniqueness without evidence. If duplicate checking is unavailable, mark `DUPLICATE_STATUS_UNKNOWN` rather than guessing.

### Phase 11: Severity Calibration

Assign severity only after reachability, exploitability, and impact are assessed.

Score each dimension from 0 to 4:

- `R` Reachability
- `A` Attacker control
- `E` Exploit reliability
- `I` Impact magnitude
- `B` Blast radius
- `P` Persistence
- `S` Scope/threat-model fit
- `Q` Evidence quality

Use these anchors:

- `0`: absent or disproven
- `1`: weak, rare, or highly constrained
- `2`: plausible but incomplete
- `3`: demonstrated with meaningful limitations
- `4`: strongly demonstrated under realistic production conditions

Calculate a confidence score, not a severity score:

`confidence = round(100 * (R + A + E + I + B + P + S + Q) / 32)`

Apply mandatory caps:

- reachability unconfirmed: maximum 45;
- attacker control unconfirmed: maximum 50;
- only static evidence: maximum 40;
- only isolated unit harness: maximum 65;
- security impact not observed: maximum 70;
- scope unknown: maximum 75;
- contradictory preconditions: maximum 25;
- countermeasure likely blocks exploit: maximum 30.

Confidence meanings:

- `0-29`: rejected or highly speculative
- `30-49`: weak hypothesis
- `50-69`: plausible, substantial verification missing
- `70-84`: likely valid, limited gaps remain
- `85-94`: strongly validated
- `95-100`: exceptional evidence; still not absolute certainty

Do not use confidence as a substitute for evidence.

### Phase 12: Report-Readiness Decision

A finding is `REPORT_READY` only when all are true:

- root cause is identified;
- attacker model is explicit and realistic;
- vulnerable path is reachable;
- attacker control is demonstrated;
- meaningful security impact is demonstrated or rigorously proven;
- major counter-evidence has been evaluated;
- scope/threat-model fit is supported;
- reproduction is repeatable;
- claimed severity does not exceed proven impact;
- evidence can be independently followed.

Use `DOWNGRADE_AND_REPORT` when a real vulnerability is proven but the original impact/severity is overstated.

Use `RETURN_TO_VERIFIER` when one or more decisive tests can resolve the remaining uncertainty.

## Required Output Format

Always produce both a concise verdict and structured YAML.

```yaml
triage_version: "1.0"
mode: INITIAL_TRIAGE | FINAL_TRIAGE
finding_id: "<id or unknown>"
title: "<normalized title>"

verdict: >-
  REJECT_FALSE_POSITIVE | REJECT_OUT_OF_SCOPE | HOLD_INSUFFICIENT_EVIDENCE |
  SEND_TO_VERIFIER | REPORT_READY | DOWNGRADE_AND_REPORT | RETURN_TO_VERIFIER
confidence: 0
proposed_severity: NONE | INFO | LOW | MEDIUM | HIGH | CRITICAL | UNDETERMINED

normalized_claim:
  attacker: ""
  entry_point: ""
  trigger: ""
  root_cause: ""
  security_property: ""
  impact: ""
  affected_configuration: ""

scope:
  status: IN_SCOPE | OUT_OF_SCOPE | UNKNOWN
  threat_model_fit: CONFIRMED | PARTIAL | REJECTED | UNKNOWN
  evidence: []
  exclusions_or_risks: []

reachability:
  status: CONFIRMED | PARTIAL | UNCONFIRMED | BLOCKED
  path: []
  guards_checked: []
  blockers: []
  evidence: []

attacker_control:
  controlled_values: []
  uncontrolled_values: []
  preconditions: []
  contradictory_assumptions: []

root_cause_validation:
  status: CONFIRMED | PARTIAL | UNCONFIRMED | DISPROVEN
  violated_invariant: ""
  evidence: []
  alternative_explanations: []

counter_evidence:
  - item: ""
    classification: BLOCKS_EXPLOIT | REDUCES_IMPACT | IRRELEVANT | BYPASS_PROVEN | NEEDS_TESTING
    reasoning: ""

evidence_quality:
  reproduction_level: SPECULATION | STATIC_PATH | UNIT_HARNESS | INTEGRATION | SUPPORTED_DEPLOYMENT | ADVERSARIAL_E2E
  reproducibility: "unknown"
  control_experiment: ""
  artifacts: []
  limitations: []

impact_validation:
  primitive: ""
  demonstrated_security_consequence: ""
  blast_radius: ""
  persistence: ""
  recovery: ""
  proven_impact: ""
  unsupported_claims: []

novelty:
  duplicate_status: UNIQUE_SUPPORTED | POSSIBLE_DUPLICATE | KNOWN_ISSUE | DUPLICATE_STATUS_UNKNOWN
  evidence: []

scoring:
  reachability_R: 0
  attacker_control_A: 0
  exploit_reliability_E: 0
  impact_I: 0
  blast_radius_B: 0
  persistence_P: 0
  scope_fit_S: 0
  evidence_quality_Q: 0
  raw_confidence: 0
  applied_caps: []
  final_confidence: 0

required_next_steps:
  - priority: BLOCKER | HIGH | MEDIUM | LOW
    action: ""
    expected_evidence: ""
    decision_resolved: ""

report_guidance:
  safe_claims: []
  claims_to_remove_or_downgrade: []
  recommended_title: ""
  recommended_severity: ""

final_reasoning: "Concise evidence-based explanation."
```

## Verifier Handoff Contract

When verdict is `SEND_TO_VERIFIER` or `RETURN_TO_VERIFIER`, provide a minimal test plan. Every test must contain:

- hypothesis;
- exact setup;
- trigger;
- observable pass condition;
- observable fail condition;
- control experiment;
- artifacts to collect;
- which triage uncertainty the test resolves.

Prefer tests that falsify the finding over tests that merely reproduce a symptom.

Example:

```yaml
verification_tests:
  - id: V1
    hypothesis: "An unauthenticated remote peer can reach the panic in the default release build."
    setup: "Two-node supported deployment using commit <sha>, release profile, default config."
    trigger: "Send the minimally malformed protocol message through the public peer interface."
    pass_condition: "Target process exits and trace confirms the claimed sink."
    fail_condition: "Message is rejected, peer disconnected safely, or only a test harness crashes."
    control: "Send a valid neighboring message and confirm normal processing."
    collect: ["pcap", "application logs", "backtrace", "config", "commit hash"]
    resolves: ["reachability", "production relevance", "availability impact"]
```

## Failure Modes to Avoid

Never:

- accept the hunter's severity without independent analysis;
- treat a dangerous code pattern as an exploit;
- confuse attacker-influenced with attacker-controlled;
- assume internal state can be arbitrarily chosen;
- ignore upstream validation;
- ignore restart, rollback, quorum, or recovery;
- call something remote when local compromise is required;
- call something unauthenticated when credentials are required;
- claim network-wide impact from a single-node experiment;
- claim persistent impact without testing recovery;
- hide negative test results;
- use an exact confidence number unsupported by dimension scores;
- produce a report-ready verdict while decisive assumptions remain unknown.

## Completion Standard

The triage is complete when another reviewer can understand:

1. exactly what is claimed;
2. which evidence supports each link in the exploit chain;
3. which assumptions remain;
4. what counter-evidence was checked;
5. what impact is actually proven;
6. why the finding is or is not eligible;
7. the smallest next test needed, if not ready.
