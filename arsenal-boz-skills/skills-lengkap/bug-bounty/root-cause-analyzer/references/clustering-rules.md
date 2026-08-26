# Clustering rules

## Strong merge signals

- One missing authorization decision affects many routes.
- One parser accepts a malformed representation consumed by multiple components.
- One shared arithmetic helper violates the same accounting invariant.
- One restart/replay defect manifests in several validator states.

## Strong split signals

- Different security boundaries require separate failures.
- Independent patches are required.
- One observation remains after fixing the other.
- Different attacker capabilities and different violated invariants apply.

## Reporting note

Multiple affected locations can strengthen blast-radius evidence without becoming multiple bounty submissions.
