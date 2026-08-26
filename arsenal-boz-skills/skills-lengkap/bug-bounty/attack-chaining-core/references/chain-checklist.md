# Attack Chain Review Checklist

## Primitive quality
- [ ] Each primitive has a distinct finding ID
- [ ] Starting capability and preconditions are explicit
- [ ] Postcondition/capability gained is observable
- [ ] Evidence level is recorded
- [ ] Scope status is known

## Composition
- [ ] Every postcondition satisfies the next precondition
- [ ] Identity, tenant, version, and configuration contexts match
- [ ] Timing and lifetime constraints overlap
- [ ] No hidden privilege jump exists
- [ ] State transitions are compatible

## Adversarial review
- [ ] Token/session binding checked
- [ ] Authorization boundaries checked
- [ ] Rate/resource limits checked
- [ ] Rollback/recovery checked
- [ ] Finality/quorum/oracle protections checked when relevant
- [ ] Negative controls defined

## Impact
- [ ] Incremental capability is recorded per step
- [ ] Final protected boundary is named
- [ ] Chain is shorter or stronger than alternatives
- [ ] Severity is based on demonstrated impact
- [ ] Attacker does not begin with equivalent capability

## Submission readiness
- [ ] All critical transitions verified
- [ ] Production relevance established
- [ ] Scope/threat model fits all steps
- [ ] Evidence is reproducible
- [ ] Report clearly distinguishes fact from inference
