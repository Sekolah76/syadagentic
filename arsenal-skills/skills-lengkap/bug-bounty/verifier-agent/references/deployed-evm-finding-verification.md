# Deployed EVM Finding Verification

Use this for candidate findings that claim a live deployment is exploitable, especially when test mocks, deployment scripts, or fork PoCs are involved.

## Evidence ladder

1. **Repository provenance**
   - Confirm the exact source and deployment/config files are tracked and unmodified.
   - Read the deployed-address manifest consumed by the frontend or operator tooling.
   - Distinguish committed candidate code from locally added PoCs and audit helpers.
2. **Live identity and wiring**
   - Read live bytecode and critical getters from an independent RPC.
   - Compare deployed runtime bytecode with compiled artifacts. Prefer exact equality; if constructor immutables or metadata differ, compare normalized logic and explain the mismatch.
   - Verify chain ID, configured dependency addresses, owner/admin/proxy state, balances, total supply, and relevant timestamps.
3. **Permissionless reachability**
   - Probe the claimed state-changing selector from an arbitrary unprivileged `from` address with `eth_call` before relying on the PoC.
   - A successful call proves absence of an immediate authorization revert, but not persistence or economic impact.
4. **PoC execution and accounting**
   - Run the supplied PoC unchanged first.
   - Require pre/post balance deltas for attacker and victim, not only a positive final attacker balance.
   - Pin the fork block where reproducibility matters.
   - Assert victim loss, attacker gain, and any expected residual/dust.
5. **Time and environment realism**
   - Treat `evm_setNextBlockTimestamp`, impersonation, storage edits, prefunding, and oracle overrides as explicit assumptions.
   - Derive the live waiting period from contract logic. Reward systems may extend `periodFinish` while supply is zero, so the displayed live finish can be misleading.
   - Separate “works after fork time travel” from “immediate live drain.”
6. **Deployment intent and scope**
   - Inspect flags, comments, README text, network branches, and frontend network restrictions.
   - A testnet mock can make the code path technically exploitable while reducing current economic impact to informational/testnet-only.
   - If the same documented mainnet path deploys the mock unconditionally, frame it as prospective deployment/configuration risk unless an actual mainnet instance exists.
7. **Root cause and duplicates**
   - Do not split every unrestricted helper (`mint`, `burn`, internal transfer/approve wrappers) into separate findings when one unsafe mock is trusted as a production asset.
   - Name the root cause at the trust boundary: e.g. “unsafe test mock configured as trusted staking token.”
   - Identify which primitive actually produces the claimed impact; treat the others as symptoms or additional consequences.
8. **Economic framing**
   - Report token amount, fraction of supply, and demonstrated extractable balance separately from monetary value.
   - Do not infer dollar impact from a testnet token balance or symbol.
   - Separate current deployed loss, latent future-mainnet risk, and operator-dependent deployment mistakes.

## Verdict pattern

A useful split verdict is:

- **Technical exploitability:** confirmed/rejected.
- **Current economic impact:** proven/unproven/testnet-only.
- **Mainnet status:** deployed/prospective/not evidenced.
- **Reportability:** depends on program treatment of testnet and mock assets.

This prevents a real code path from being overstated as a current mainnet asset loss.