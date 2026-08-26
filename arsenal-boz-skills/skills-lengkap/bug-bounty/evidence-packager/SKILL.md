---
name: evidence-packager
description: Assemble a reproducible, minimal, tamper-evident evidence bundle for a security finding, preserving provenance and separating observed facts from interpretation.
version: 1.0.0
---

# Evidence Packager

## Mission

Transform verifier outputs into an auditable evidence bundle that triage and report-writing agents can rely on without reconstructing or exaggerating the finding.

This skill packages evidence; it does not invent missing evidence or raise severity.

## Evidence classes

- source references and commit/revision;
- environment and configuration manifest;
- exact requests, messages, transactions, or test inputs;
- sanitized responses and outputs;
- logs and stack traces;
- execution/call/state-transition traces;
- before/after state snapshots;
- PoC and test files;
- screenshots only when they add unique evidence;
- artifact hashes;
- reproduction statistics;
- negative controls and mitigation tests.

## Workflow

### 1. Freeze identity and scope

Record target, revision, branch, contract address/network where applicable, build flags, deployment profile, and authorized test environment.

### 2. Build claim-evidence matrix

For every report claim, link the minimum evidence that supports it. Classify claims:

- `OBSERVED` — directly recorded;
- `DERIVED` — calculated from recorded evidence;
- `INFERRED` — logically supported but not directly observed;
- `UNVERIFIED` — unsupported and must not appear as fact.

### 3. Preserve provenance

Each artifact records:

- producer/tool;
- timestamp when available;
- command or action that generated it;
- source revision/environment;
- redactions performed;
- cryptographic hash.

Never alter raw evidence. Store sanitized copies separately and document redactions.

### 4. Minimize sensitive data

Remove or mask credentials, personal data, private keys, session tokens, unrelated tenant data, and production secrets. Preserve only the minimum necessary proof. Do not package live exploit credentials.

### 5. Normalize reproduction

Provide deterministic steps:

- setup;
- prerequisites;
- build/run commands;
- trigger;
- expected vulnerable result;
- expected safe/control result;
- cleanup;
- reliability statistics.

### 6. Include negative controls

Examples:

- patched/guarded input does not trigger;
- unauthorized path is rejected;
- alternate configuration is not vulnerable;
- one omitted chain step prevents impact;
- normal protocol sequence preserves invariant.

Negative controls help prove causality.

### 7. Validate completeness

A report-ready package needs:

- identity/revision;
- root cause;
- reachable attacker path;
- reproducible primitive;
- evidence-backed impact;
- threat-model/scope alignment;
- counter-evidence addressed;
- sanitized artifacts;
- claim matrix with no unsupported critical claim.

### 8. Produce manifest

Use `templates/evidence-manifest.yaml`. Suggested directory layout is in `references/bundle-layout.md`.

## Readiness verdicts

- `REPORT_READY`
- `TECHNICALLY_VERIFIED_IMPACT_INCOMPLETE`
- `REPRODUCTION_INCOMPLETE`
- `PROVENANCE_INCOMPLETE`
- `SENSITIVE_DATA_REVIEW_REQUIRED`
- `NOT_READY`

## Guardrail

Never fabricate screenshots, logs, hashes, request IDs, transaction hashes, line numbers, success rates, or environment details. Missing data must remain explicitly missing.
