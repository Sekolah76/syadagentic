---
name: attack-chaining-core
description: Domain-neutral attack chain analysis — determine whether independently identified security primitives compose into a realistic, authorized, evidence-backed attack path with greater impact.
version: 1.0.0
---

# Attack Chaining Core

## Purpose

Use this skill to determine whether two or more independently identified security primitives can be composed into a realistic, authorized, and evidence-backed attack path with greater security impact.

This skill is an analytical composer, not an exploit generator. It must preserve scope, minimize harm, and hand concrete validation steps to a verifier.

## Core rule

A chain is valid only when the postcondition of step N satisfies a documented precondition of step N+1.

Never infer compatibility merely because two findings affect the same product.

## Required inputs

For every candidate primitive collect:

- unique finding ID;
- affected component/version/configuration;
- attacker starting capability;
- entry point;
- required preconditions;
- attacker-controlled values/state;
- operation performed;
- observable postconditions;
- capability gained;
- persistence and lifetime;
- evidence level;
- scope/threat-model status;
- known blockers and mitigations.

Missing fields remain `UNKNOWN`; do not invent them.

## Operating modes

- `DISCOVERY`: search for compatible compositions.
- `VALIDATION_PLAN`: turn a candidate chain into safe verifier experiments.
- `POST_VERIFICATION`: audit evidence and determine report readiness.

## Mandatory procedure

### 1. Normalize every primitive

Represent each finding as:

`starting capability + preconditions -> trigger -> primitive -> postcondition/capability gained`

Separate observed facts from inferred consequences.

### 2. Build the capability graph

Create nodes for attacker capabilities and protected assets/states. Create directed edges for verified or plausible primitives.

Examples of capability nodes:

- unauthenticated network access;
- valid low-privilege account;
- victim interaction;
- read one object;
- write one object;
- obtain reusable credential;
- execute as service identity;
- influence price/state ordering;
- cross a trust boundary;
- alter finalized or economically relevant state.

Each edge must include preconditions, evidence, cost, reliability, duration, and scope status.

### 3. Perform exact compatibility checks

For adjacent steps verify:

- output type and input type match;
- identity/tenant/account context matches;
- timing windows overlap;
- configuration and deployment assumptions are compatible;
- privileges gained are sufficient, not merely similar;
- data is readable in the required form;
- secrets/tokens are reusable in the intended audience and context;
- state transitions are legal and reachable;
- mitigations between steps do not break the path.

### 4. Track state and capability after every step

Record:

- capability gained;
- capability lost or consumed;
- state changed;
- persistence;
- observability/detection;
- cleanup/recovery behavior;
- whether the next step is deterministic, probabilistic, or speculative.

### 5. Search for counter-evidence

Actively try to break the chain:

- token audience/binding mismatch;
- session rotation or expiry;
- tenant isolation;
- canonicalization differences;
- transaction atomicity;
- rollback/reconciliation;
- rate limits and resource caps;
- privilege boundaries;
- oracle freshness/deviation limits;
- quorum/finality protections;
- unsupported configuration;
- attacker already possessing an equivalent capability.

### 6. Prune weak chains

Reject or downgrade chains that:

- contain a speculative-to-speculative transition;
- require mutually incompatible states;
- rely on prohibited actions or out-of-scope assets;
- require secrets/privileges equivalent to the final impact;
- depend on unrealistic victim behavior;
- require impractical timing without attacker control;
- add steps without increasing capability or impact;
- are longer than an available minimal chain with the same impact.

### 7. Find the minimal meaningful chain

Prefer the shortest chain that demonstrates the protected security boundary being crossed. Report optional variants separately.

Do not inflate severity simply because more steps are included.

### 8. Score the chain

Score each dimension 0–5:

- `C`: compatibility of adjacent steps;
- `R`: reachability;
- `A`: attacker control;
- `L`: reliability;
- `E`: evidence quality;
- `I`: demonstrated impact;
- `S`: scope/threat-model fit;
- `M`: mitigation resistance.

Suggested confidence percentage:

`round(100 * (C + R + A + L + E + I + S + M) / 40)`

Apply mandatory caps:

- any unverified critical transition: maximum 69;
- production relevance unproven: maximum 64;
- final impact inferred but not observed: maximum 74;
- scope status unknown: maximum 59;
- any out-of-scope required step: chain rejected;
- attacker starts with capability equivalent to final impact: no escalation claim.

### 9. Produce verifier handoff

For every uncertain edge provide:

- exact claim to test;
- safe setup;
- input/state sequence;
- expected result if valid;
- expected negative control;
- evidence to capture;
- stop conditions;
- cleanup plan.

### 10. Final verdict

Use one:

- `NO_VALID_CHAIN`
- `CHAIN_CANDIDATE`
- `RETURN_TO_VERIFIER`
- `CHAIN_VALID_IMPACT_UNPROVEN`
- `REPORT_READY_CHAIN`
- `REJECT_OUT_OF_SCOPE`

## Severity discipline

Severity is based on demonstrated final impact under realistic attacker capabilities, not the arithmetic sum of individual severities.

Always state:

- standalone impact of each primitive;
- incremental capability gained at each step;
- exact boundary crossed by composition;
- why the final impact is impossible or materially harder without the chain.

## Safety and authorization

Only analyze and validate within explicit authorization. Prefer local harnesses, testnets, owned accounts, synthetic data, and non-destructive proofs. Never recommend persistence, destructive actions, unauthorized access, asset movement, or real-user targeting.

## Output

Use `templates/chain-output.yaml` and include a concise human-readable chain summary.
