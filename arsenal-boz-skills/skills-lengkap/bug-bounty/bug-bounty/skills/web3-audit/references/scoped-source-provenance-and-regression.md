# Scoped-source provenance and regression validation

Use this reference when auditing a contest repository whose advertised scope commit is unavailable locally or cannot be fetched.

## Submission gate

1. Record the advertised scope hash and test it with `git cat-file -e <hash>^{commit}`.
2. Record the actual checked-out `HEAD` with `git rev-parse HEAD` and its remote.
3. If they differ or the scoped hash is unavailable, use the snapshot only for hypothesis generation and local regression validation.
4. Do not submit a finding as in-scope until its affected lines are verified against the official scoped artifact.

## Validation layering

- Run focused Foundry suites for the candidate's module and adjacent invariants first.
- Then run cross-module regression suites (e.g., vault NAV/list handling plus exchange/NFT; loan ledger plus authorization/smart-account paths).
- Finish with `forge test -q --threads 1` for the available snapshot. Capture exact pass/fail output; never infer coverage from compilation alone.

## Tare-style NAV review checklist

For batched portfolio valuation, test that each mid-cycle mutation either blocks, invalidates, or restarts computation:

- NFT ownership changes: use an ownership nonce/snapshot and verify stale holdings are removed.
- Loan-list mutations: require an idle computation or invalidate cached NAV.
- Calculator/config changes: version the configuration and restart stale computation.
- Idle asset changes: invalidate cached NAV after cashflow collection.
- Async ERC-7540 flows: test share-price preservation and conservation across request, partial approval, claim, mixed deposit/redeem, and rounding paths.

## Trust-boundary filter

Do not package a finding that requires an explicitly trusted protocol role to act maliciously. State the required actor, any approval/custody precondition, and a concrete victim loss. Treat ordinary ERC-721 approval authority as standard authorization unless the protocol adds a distinct privilege escalation.
