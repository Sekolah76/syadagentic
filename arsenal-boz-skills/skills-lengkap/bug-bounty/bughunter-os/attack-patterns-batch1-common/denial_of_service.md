# Denial Of Service

## Definition
Describe the attack pattern and when it occurs.

## Root Cause
Explain the underlying design or implementation mistake.

## Threat Model
- Attacker capabilities
- Required privileges
- External assumptions

## Detection Workflow
1. Identify affected state.
2. Trace asset and control flow.
3. Verify invariant preservation.
4. Evaluate exploitability.
5. Reject unsupported assumptions.

## Invariant Violated
Document the security or accounting invariant that fails.

## False Positive Checklist
- Reachable execution path?
- Realistic attacker model?
- Practical impact?
- Existing mitigation already blocks it?

## Common Mitigations
List design or implementation techniques that prevent this pattern.

## Related Patterns
Reference similar attack patterns.
