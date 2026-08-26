# Web3 Chain Matrix

| Primitive output | Possible next precondition | Mandatory proof |
|---|---|---|
| Temporary liquidity | Capital-dependent state action | Same atomic path, capacity, fees, repayment |
| Spot price movement | Protocol valuation input | Exact oracle source/window and accepted update |
| Inflated shares/collateral | Borrow/redeem capacity | Accounting formula and executable liquidity |
| Callback control | Re-entry into vulnerable state | Reachable callback, absent guard, invariant delta |
| Signed message | Authorized transition | Domain, nonce, expiry, signer, replay acceptance |
| Voting tokens | Governance power | Snapshot/delegation/quorum/timelock rules |
| Source-chain event | Destination mint/release | Accepted proof/signature path and replay checks |
| Transaction-order influence | State-dependent extraction | Realistic ordering control and net value |
| Crafted validator message | Consensus state transition | Protocol-legal sequence and honest-node acceptance |
| Restart/snapshot inconsistency | Persistent divergence | Survives replay/reconciliation and affects protected state |
