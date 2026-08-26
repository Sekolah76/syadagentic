# ERC4626 Vault

## Protocol Overview
ERC4626 vaults with deposits, shares and withdrawals.

## Critical Invariants
- Assets remain solvent.
- Accounting stays consistent.
- Authorization boundaries hold.

## Attack Surface
- External entry points
- Oracle dependencies
- Token interactions
- Upgrade/admin controls
- Cross-contract calls

## Audit Workflow
1. Map assets and actors.
2. Identify trust boundaries.
3. Validate accounting.
4. Verify permissions.
5. Stress economic assumptions.
6. Construct exploit hypotheses.
7. Eliminate false positives.

## High-Risk Modules
List protocol-specific modules requiring extra scrutiny.

## Related Attack Patterns
Reference relevant Pack A patterns.

## Related Exploit Knowledge
Reference similar incidents from Pack B.

## Exit Criteria
Only report issues with a reproducible invariant violation and justified impact.
