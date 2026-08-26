# Guardrail Checklist

## Before Any Test

- [ ] Exact target and asset are in scope.
- [ ] Version/commit and environment are eligible.
- [ ] Proposed action is classified R0-R4.
- [ ] The least-impact method was selected.
- [ ] Synthetic or owned data will be used.
- [ ] Rate/resource/event limits are explicit.
- [ ] Control experiment is defined.
- [ ] Stop conditions exist.
- [ ] Cleanup/rollback exists for stateful actions.
- [ ] Untrusted repository scripts or binaries are isolated.

## Reasoning Audit

- [ ] Candidate is one falsifiable sentence.
- [ ] Facts, observations, inferences, assumptions, and hypotheses are separated.
- [ ] Every material claim points to evidence.
- [ ] Attacker capability is explicit.
- [ ] Security boundary/property is explicit.
- [ ] Version/configuration applicability is explicit.
- [ ] Counter-evidence is retained.
- [ ] Confidence is not inherited from another agent.

## Evidence Audit

- [ ] Raw evidence is retained.
- [ ] Command/request and input are exact.
- [ ] Timestamp, target, commit/version, flags, and configuration are recorded.
- [ ] Output is not truncated or selectively quoted.
- [ ] Failed runs are included.
- [ ] Control run exists.
- [ ] Clean-state rerun exists when needed.
- [ ] Reproduction rate is stated.
- [ ] Environmental artifacts were tested.
- [ ] Evidence hashes are recorded where practical.

## Claim Alignment

- [ ] Reachability is proven.
- [ ] Attacker control is proven.
- [ ] Preconditions are realistic.
- [ ] Vulnerable operation is observed.
- [ ] Security property violation is demonstrated.
- [ ] Operational impact is measured, not assumed.
- [ ] Blast radius and persistence are bounded.
- [ ] Recovery and mitigations are documented.
- [ ] Severity matches demonstrated impact.

## Before Report

- [ ] Scope and disclosure rules are rechecked.
- [ ] No active secrets are present.
- [ ] Personal and third-party data are minimized/redacted.
- [ ] Root cause and affected version are precise.
- [ ] Reproduction steps use safe data.
- [ ] Limitations and failed assumptions are disclosed.
- [ ] Duplicate/root-cause overlap risk is noted.
- [ ] Unsupported exploit chains and severity language are removed.
