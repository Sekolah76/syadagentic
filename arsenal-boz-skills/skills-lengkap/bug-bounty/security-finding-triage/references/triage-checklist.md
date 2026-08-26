# Security Finding Triage Checklist

## Claim
- [ ] Claim rewritten as a falsifiable attacker-to-impact statement
- [ ] Attacker capability explicitly stated
- [ ] Root cause and violated invariant identified
- [ ] Claimed impact separated from observed primitive

## Scope
- [ ] Asset/version is in scope
- [ ] Threat model accepts attacker capability
- [ ] Exclusions reviewed
- [ ] Default/supported configuration identified

## Reachability
- [ ] Real external entry point identified
- [ ] Full path to sink traced
- [ ] Authn/authz checks evaluated
- [ ] Validation and canonicalization evaluated
- [ ] Build flags and feature gates evaluated
- [ ] Upstream limits evaluated

## Preconditions
- [ ] Every required state/value listed
- [ ] Attacker control classified
- [ ] Preconditions are mutually compatible
- [ ] Privileged or local-compromise assumptions disclosed

## Counter-Evidence
- [ ] Searched for alternate guards
- [ ] Searched for locks/order guarantees
- [ ] Searched for retry/rollback/recovery
- [ ] Searched for rate/resource limits
- [ ] Searched for protocol/quorum protections
- [ ] Negative tests recorded

## Reproduction
- [ ] Exact commit/version recorded
- [ ] Release/debug profile recorded
- [ ] Configuration recorded
- [ ] Trigger is repeatable
- [ ] Control experiment included
- [ ] Artifacts collected
- [ ] Production relevance established

## Impact
- [ ] Security boundary/property named
- [ ] Blast radius measured
- [ ] Persistence tested
- [ ] Recovery tested
- [ ] Practical attacker cost considered
- [ ] Severity capped to demonstrated impact

## Final
- [ ] Duplicate/known issue risk assessed
- [ ] Confidence dimensions scored
- [ ] Mandatory caps applied
- [ ] Verdict matches evidence
- [ ] Remaining blockers converted into verifier tests
