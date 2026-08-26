# EVM Fork Harness Reproducibility

Use when a deployed-contract PoC passes only under a particular fork runner, block, or pre-funded account set.

## Verification sequence

1. **Run the supplied PoC unchanged first.** Record the runner, network name, fork block, and result.
2. **Check whether the test actually pins its fork.** A comment, filename, or separately launched node does not make a test self-pinning. For Hardhat resets, require an explicit `blockNumber`; for an external node, record the exact startup command.
3. **Start from fresh state.** Restart the fork or revert to a known snapshot before each replay. Deterministic accounts may retain active positions, nonces, approvals, or balances and produce misleading second-run failures.
4. **Corroborate the primitive against live RPC.** Use `eth_getCode`, critical getters, and an arbitrary-address `eth_call` to distinguish a harness artifact from deployed reachability. Never broadcast solely to validate access control.
5. **Classify fork-only conveniences:**
   - Prefunded accounts: translate into the real gas/collateral prerequisite.
   - Impersonation: privileged assumption unless the attacker naturally controls that address.
   - Storage edits/oracle overrides: synthetic state; not deployment proof.
   - Time travel: state the real waiting period.
   - Different hardfork rules: identify whether the exercised bytecode/opcodes or gas semantics are affected.
6. **Separate harness validity from exploit validity.** A default-runner failure can be a harness defect, while a pinned external fork plus live-RPC corroboration can still confirm the primitive. Conversely, a fork pass without live identity/wiring evidence is insufficient.

## Common failure modes and disposition

| Observation | Interpretation |
|---|---|
| Latest Hardhat fork fails because chain hardfork history is unknown | Harness incompatibility; retry on a pinned fork runner, then corroborate live state |
| Second replay says the attacker already has an active position | Dirty deterministic fork state; restart/revert and use a fresh attacker |
| PoC depends on two public transactions | Note ordering/race exposure; determine whether an atomic helper is feasible and prove it for high-confidence claims |
| Test prints an “actual price” from the pre-attack mock | Mislabeling unless independently sourced; call it the pre-manipulation protocol price |
| Fork account has enormous native balance | Do not count it as attacker profit; report the minimum live gas/collateral prerequisite |

## PoC quality requirements

A submission-grade fork test should:

- pin chain ID and block number in code or documented fixture;
- reset or snapshot/revert for isolation;
- use a fresh unprivileged attacker;
- assert attacker and victim/system balance deltas;
- disclose prefunding, impersonation, time travel, and storage changes;
- avoid relying on final balances alone;
- reproduce the meaningful state transition atomically when ordering matters;
- keep live-RPC checks read-only unless explicit authorization includes broadcasting.

This reference complements `deployed-evm-finding-verification.md`: that file governs deployment identity and impact; this file governs fork-runner fidelity and reproducible PoC execution.