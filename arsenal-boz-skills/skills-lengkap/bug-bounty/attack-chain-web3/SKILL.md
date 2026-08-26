---
name: attack-chain-web3
description: Web3 attack chain plugin — apply Web3 state, economic, cryptographic, and consensus semantics on top of attack-chaining-core for authorized testing of smart contracts, DeFi, bridges, wallets, and validators.
version: 1.0.0
---

# Web3 Attack Chain Plugin

## Purpose

Apply Web3-specific state, economic, cryptographic, and consensus semantics on top of `attack-chaining-core` for authorized testing of smart contracts, DeFi protocols, bridges, wallets, validators, and distributed systems.

Use local forks, testnets, simulators, or private clusters. Do not move real user assets or disrupt public networks.

## Web3 chain families

- temporary liquidity -> state/price influence -> value extraction;
- oracle input/control -> incorrect valuation -> borrow/liquidation/accounting impact;
- callback/reentrancy -> intermediate-state reuse -> invariant violation;
- rounding/precision/accounting drift -> repeated amplification -> asset imbalance;
- signature/domain/replay weakness -> unauthorized message acceptance -> state transition;
- governance weight acquisition -> proposal/control action -> treasury or parameter impact;
- bridge message/proof validation weakness -> unauthorized mint/release;
- wallet/session/approval weakness -> signer authority abuse -> asset movement;
- transaction ordering/MEV -> state-dependent operation -> economic extraction;
- validator/message scheduling -> state divergence or liveness failure;
- snapshot/restart/replay inconsistency -> persistent state corruption or consensus impact.

## Mandatory Web3 state model

For every step record:

- chain/network and block/slot/epoch context;
- contract/program/component and exact version;
- pre-state and post-state;
- caller/signer authority;
- balances, shares, debt, collateral, reserves, and supply affected;
- oracle values, timestamps, confidence/deviation bounds;
- transaction atomicity and ordering;
- finality/reorg assumptions;
- economic capital required and recoverable;
- fees, slippage, liquidity, and profitability where relevant.

## Composition rules

### Atomic chains

For flash-loan or single-transaction chains, every step must succeed under transaction atomicity. A state that disappears on revert cannot satisfy a later step.

### Multi-transaction chains

Prove persistence between transactions, front-running exposure, required approvals, timing windows, and whether defenders/arbitrageurs can restore state.

### Oracle chains

Separate ability to trade an asset from ability to move the protocol's consumed oracle. Validate source, aggregation, update cadence, TWAP window, liquidity depth, deviation checks, stale-price handling, and downstream use.

### Governance chains

Separate temporary token ownership from voting power. Check snapshots, delegation, quorum, proposal delay, timelock, veto/guardian controls, execution permissions, and capital lock duration.

### Bridge chains

Trace the complete trust path:

`source event/state -> relayer/validator observation -> proof/signature verification -> replay/domain checks -> destination execution`

A bug in one component matters only if it creates an accepted destination transition.

### Signature and replay chains

Check signer authority, domain separator, chain ID, contract/program address, nonce, expiry, message encoding, malleability, and replay storage. A valid signature for another context is not automatically reusable.

### Validator and consensus chains

Classify schedules as attacker-forced, attacker-biased, network-possible, harness-only, or protocol-illegal. Distinguish task/process/node crash from quorum loss or network halt. Prove legal message sequences and persistence through replay, fork choice, reconciliation, restart, and finality.

## Economic impact discipline

Do not equate temporary accounting deviation with extractable loss. Calculate:

- attacker capital at risk;
- maximum executable size under liquidity;
- fees and slippage;
- liquidation/arbitrage response;
- per-block/per-epoch limits;
- recoverable versus irreversible loss;
- protocol bad debt or locked assets;
- whether the chain is profitable, griefing-only, or safety/liveness impact.

Severity follows demonstrated loss/control/safety impact, not theoretical TVL.

## Web3 chain blockers

Search for:

- checks-effects-interactions or reentrancy guards;
- invariant checks after callbacks;
- transaction revert/atomicity;
- oracle TWAP/deviation/staleness limits;
- caps, pauses, guardians, timelocks;
- signature domain separation and nonces;
- replay protection;
- proof finality and confirmation thresholds;
- quorum and Byzantine fault assumptions;
- slashing/economic cost;
- fork-choice reconciliation;
- liquidity depth and price recovery;
- privilege already equivalent to claimed impact.

## Required output additions

Include:

- transaction/state timeline;
- balance and invariant deltas;
- signer/caller table;
- oracle and liquidity assumptions;
- atomicity/finality analysis;
- economic feasibility estimate;
- validator/consensus schedule classification when applicable;
- safe verifier plan on a fork/testnet/private cluster.
