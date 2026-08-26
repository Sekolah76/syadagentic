---
name: bughunter-os-index
description: Quick lookup index for the bughunter-os mega-skill. Maps common questions, vulnerability classes, and protocol types to specific files in the knowledge base.
---

# BugHunter OS — Master Index

Quick navigation for the 347 files in `bughunter-os/`. Use this as a router when you need to find specific information fast.

## How to Use This Index

1. **Identify your question type** below
2. **Jump to the relevant section**
3. **Load the specific file(s)** for details

---

## 🎯 Quick Routes

### "I'm starting a new audit"
1. → `orchestrator-batch1/repository_classifier.md`
2. → `orchestrator-batch1/protocol_detector.md`
3. → `orchestrator-batch1/audit_planner.md`
4. → `bughunter-phase1/` (foundation)
5. → `protocol-playbooks-batch{1,2}/` (match your protocol type)

### "I'm hunting a specific bug class"
→ See [Vulnerability Classes](#-vulnerability-classes) below

### "I'm auditing a specific protocol type"
→ See [Protocol Types](#-protocol-types) below

### "I want to learn from a past exploit"
→ See [Real-World Exploits](#-real-world-exploits) below

### "I'm writing a report"
1. → `bughunter-phase8/`
2. → `orchestrator-batch5/` (reporting engine)
3. → `orchestrator-batch6/quality_gate.md`

### "I need to build a PoC"
1. → `bughunter-phase7/exploit_builder.md`
2. → `orchestrator-batch5/poc_builder.md`
3. → `orchestrator-batch2/confidence_engine.md`

---

## 🐛 Vulnerability Classes

### Reentrancy
- `attack-patterns-batch1-common/reentrancy.md`
- `exploit-kb-batch1/curve.md` (real-world example)
- `attack-patterns-batch3-advancedprotocols/` (advanced variants)

### Oracle Manipulation
- `attack-patterns-batch1-common/oracle.md`
- `attack-patterns-batch2-protocolspecific/Oracle/` (multiple)
- `exploit-kb-batch1/hundred_finance.md`, `sonne_finance.md`, `prisma_finance.md`

### Flash Loan Attacks
- `attack-patterns-batch1-common/sandwich.md`
- `exploit-kb-batch1/beanstalk.md` (governance flash loan)
- `exploit-kb-batch2/` (various flash loan exploits)

### Signature Replay / Validation
- `attack-patterns-batch1-common/signature_replay.md`
- `exploit-kb-batch1/wormhole.md` (signature verification bypass)
- `exploit-kb-batch1/nomad_bridge.md` (message hash)

### Access Control Bypass
- `attack-patterns-batch1-common/` (multiple)
- `bughunter-phase5/access_control.md`
- `exploit-kb-batch1/radiant_capital.md` (multisig signer compromise)

### Governance Attacks
- `attack-patterns-batch2-protocolspecific/Governance/` (vote_snapshot_bug, quorum_manipulation, timelock_bypass, flashloan_voting)
- `exploit-kb-batch1/beanstalk.md`
- `exploit-kb-batch3/Governance/` (theme-based exploits)

### Bridge & Cross-Chain
- `attack-patterns-batch3-advancedprotocols/Bridge/` (replay, message_forgery, finality_race)
- `exploit-kb-batch1/wormhole.md`, `nomad_bridge.md`
- `exploit-kb-batch2/ronin_bridge.md`, `transit_swap.md`
- `protocol-playbooks-batch1/bridge.md`
- `protocol-playbooks-batch2/cross_chain_messaging.md`

### Proxy & Upgrade Issues
- `attack-patterns-batch1-common/storage_collision.md`
- `exploit-kb-batch3/Upgradeability/` (proxy_misconfiguration, admin_key_failure)
- `bughunter-phase4/upgrade_surface.md`

### AMM / DEX Issues
- `attack-patterns-batch2-protocolspecific/AMM/` (virtual_reserve_bug, imbalanced_pool_attack, sqrt_price_limit)
- `exploit-kb-batch1/curve.md`
- `protocol-playbooks-batch1/amm.md`

### Lending Protocol Issues
- `attack-patterns-batch2-protocolspecific/Lending/` (collateral_manipulation, liquidation, bad_debt)
- `exploit-kb-batch1/prisma_finance.md`, `sonne_finance.md`, `hundred_finance.md`
- `exploit-kb-batch2/paraspace.md`, `uwu_lend.md`

### Stablecoin
- `attack-patterns-batch3-advancedprotocols/Stablecoin/` (depeg, redemption, oracle_manipulation)
- `protocol-playbooks-batch1/stablecoin.md`

### Liquid Staking / Restaking
- `attack-patterns-batch3-advancedprotocols/LiquidStaking/`, `Restaking/` (share_depeg, withdrawal_queue, slashing, double_stake)
- `protocol-playbooks-batch1/liquid_staking.md`, `restaking.md`

### Vaults & Yield Aggregators
- `attack-patterns-batch3-advancedprotocols/VaultStrategies/` (strategy_permission_bypass, profit_lock, share_value_desync)
- `protocol-playbooks-batch1/yield_aggregator.md`

### Perpetuals
- `attack-patterns-batch3-advancedprotocols/Perpetuals/`
- `protocol-playbooks-batch1/perpetuals.md`

### Options
- `attack-patterns-batch3-advancedprotocols/Options/`

### ERC20 Edge Cases
- `attack-patterns-batch2-protocolspecific/ERC20/` (fee_on_transfer, rebasing, missing_return, permit_replay)

### ERC4626 (Vault Standard)
- `attack-patterns-batch1-common/erc4626.md`
- `attack-patterns-batch2-protocolspecific/ERC4626/` (share_inflation, donation_attack, first_depositor)

### RWA (Real World Assets)
- `protocol-playbooks-batch2/rwa.md`

### NFT Marketplaces
- `protocol-playbooks-batch2/nft_marketplaces.md`

### Prediction Markets
- `protocol-playbooks-batch2/prediction_markets.md`

### Treasury & Multisig
- `protocol-playbooks-batch2/treasury_multisig.md`

### Vesting & Distribution
- `protocol-playbooks-batch2/vesting_distribution.md`

### Auction Protocols
- `protocol-playbooks-batch2/auction_protocols.md`

### Rollup Infrastructure
- `protocol-playbooks-batch2/rollup_infrastructure.md`

---

## 📊 Protocol Types

Each protocol type has a dedicated playbook. Load the relevant one for protocol-specific workflows.

### DeFi
- `protocol-playbooks-batch1/amm.md` — AMM/DEX audit workflow
- `protocol-playbooks-batch1/lending.md` — Lending protocol audit
- `protocol-playbooks-batch1/yield_aggregator.md` — Yield aggregator
- `protocol-playbooks-batch1/perpetuals.md` — Perpetual futures
- `protocol-playbooks-batch1/stablecoin.md` — Stablecoin
- `protocol-playbooks-batch1/liquid_staking.md` — Liquid staking
- `protocol-playbooks-batch1/restaking.md` — Restaking
- `protocol-playbooks-batch1/governance.md` — Governance
- `protocol-playbooks-batch1/bridge.md` — Bridge
- `protocol-playbooks-batch2/treasury_multisig.md` — Treasury & multisig
- `protocol-playbooks-batch2/vesting_distribution.md` — Vesting
- `protocol-playbooks-batch2/auction_protocols.md` — Auction
- `protocol-playbooks-batch2/nft_marketplaces.md` — NFT
- `protocol-playbooks-batch2/prediction_markets.md` — Prediction
- `protocol-playbooks-batch2/rwa.md` — RWA
- `protocol-playbooks-batch2/cross_chain_messaging.md` — Cross-chain messaging
- `protocol-playbooks-batch2/rollup_infrastructure.md` — Rollup

---

## 💥 Real-World Exploits

### By Protocol
- `exploit-kb-batch1/wormhole.md` — Signature verification bypass ($320M)
- `exploit-kb-batch1/nomad_bridge.md` — Message hash mishandling ($190M)
- `exploit-kb-batch1/curve.md` — Reentrancy in stable swap ($73M)
- `exploit-kb-batch1/beanstalk.md` — Governance flash loan ($182M)
- `exploit-kb-batch1/prisma_finance.md` — Hook verification
- `exploit-kb-batch1/sonne_finance.md` — Market manipulation
- `exploit-kb-batch1/hundred_finance.md` — Price oracle attack
- `exploit-kb-batch1/radiant_capital.md` — Multisig compromise
- `exploit-kb-batch2/ronin_bridge.md` — Validator key compromise ($625M)
- `exploit-kb-batch2/transit_swap.md` — Cross-chain swap
- `exploit-kb-batch2/raft.md` — Stablecoin depeg
- `exploit-kb-batch2/midas_capital.md` — Lending
- `exploit-kb-batch2/sentiment.md` — Lending
- `exploit-kb-batch2/paraspace.md` — NFT lending
- `exploit-kb-batch2/uwu_lend.md` — Lending
- `exploit-kb-batch2/conic_finance.md` — Curve pools

### By Root-Cause Class (Batch 3 — theme-based)
- `exploit-kb-batch3/Governance/` — delegate_abuse, quorum_attack, proposal_execution, vote_snapshot, timelock_bypass
- `exploit-kb-batch3/Upgradeability/` — proxy_misconfiguration, admin_key_failure
- (28+ more categories in batch 3)

---

## 🏗️ Audit Phases (8-Phase Methodology)

| Phase | Files | When |
|---|---|---|
| **Phase 1: Foundation** | `bughunter-phase1/` (10 files) | Start: understand repo, call graph, storage |
| **Phase 2: Modeling** | `bughunter-phase2/` (13 files) | Trust boundaries, asset flow, privileges |
| **Phase 3: Invariants** | `bughunter-phase3/` (10 files) | What must NEVER become false |
| **Phase 4: Attack Surface** | `bughunter-phase4/` (10 files) | Enumerate entry points |
| **Phase 5: Module Audit** | `bughunter-phase5/` (10 files) | Deep per-contract review |
| **Phase 6: Economic Attacks** | `bughunter-phase6/` (9 files) | Accounting & incentive failures |
| **Phase 7: Exploit** | `bughunter-phase7/` (9 files) | Build PoC, evidence |
| **Phase 8: Reporting** | `bughunter-phase8/` (8 files) | Final report, false-positive review |

---

## 🤖 Orchestrator

Adaptive workflow engine that coordinates audit execution.

| Batch | Files | Purpose |
|---|---|---|
| `orchestrator-batch1/` | 7 | Bootstrap: classify repo, detect protocol, plan audit |
| `orchestrator-batch2/` | 6 | Reasoning: hypothesis, invariant, decision tree, FP, confidence |
| `orchestrator-batch3/` | 6 | Scheduling: task dispatcher, priority, parallel, coverage |
| `orchestrator-batch4/` | 6 | Memory: protocol, patterns, exploits, findings |
| `orchestrator-batch5/` | 6 | Reporting: PoC, evidence, severity, report, fix |
| `orchestrator-batch6/` | 7 | v1.0 Final + Quality Gate (critic, second opinion, consistency) |

---

## 📂 Full File Index by Category

### `attack-patterns-batch1-common/` (31 files)

- `attack-patterns-batch1-common/README.md` — Attack Pattern Library - Batch 1 (Common)
- `attack-patterns-batch1-common/access_control.md` — Access Control
- `attack-patterns-batch1-common/arbitrary_call.md` — Arbitrary Call
- `attack-patterns-batch1-common/arbitrary_from.md` — Arbitrary From
- `attack-patterns-batch1-common/arbitrary_transfer.md` — Arbitrary Transfer
- `attack-patterns-batch1-common/block_number_assumption.md` — Block Number Assumption
- `attack-patterns-batch1-common/callback_abuse.md` — Callback Abuse
- `attack-patterns-batch1-common/cross_function_reentrancy.md` — Cross Function Reentrancy
- `attack-patterns-batch1-common/delegatecall_storage_collision.md` — Delegatecall Storage Collision
- `attack-patterns-batch1-common/denial_of_service.md` — Denial Of Service
- `attack-patterns-batch1-common/dos.md` — Dos
- `attack-patterns-batch1-common/frontrunning.md` — Frontrunning
- `attack-patterns-batch1-common/gas_griefing.md` — Gas Griefing
- `attack-patterns-batch1-common/initialization_bug.md` — Initialization Bug
- `attack-patterns-batch1-common/integer_overflow.md` — Integer Overflow
- `attack-patterns-batch1-common/invariant_break.md` — Invariant Break
- `attack-patterns-batch1-common/mev.md` — Mev
- `attack-patterns-batch1-common/missing_zero_check.md` — Missing Zero Check
- `attack-patterns-batch1-common/precision_loss.md` — Precision Loss
- `attack-patterns-batch1-common/privilege_escalation.md` — Privilege Escalation
- `attack-patterns-batch1-common/read_only_reentrancy.md` — Read Only Reentrancy
- `attack-patterns-batch1-common/reentrancy.md` — Reentrancy
- `attack-patterns-batch1-common/replay_attack.md` — Replay Attack
- `attack-patterns-batch1-common/rounding.md` — Rounding
- `attack-patterns-batch1-common/sandwich.md` — Sandwich
- _... +6 more files in this category_

### `attack-patterns-batch2-protocolspecific/` (46 files)

- `attack-patterns-batch2-protocolspecific/AMM/constant_product_violation.md` — Constant Product Violation
- `attack-patterns-batch2-protocolspecific/AMM/flash_swap_abuse.md` — Flash Swap Abuse
- `attack-patterns-batch2-protocolspecific/AMM/imbalanced_pool_attack.md` — Imbalanced Pool Attack
- `attack-patterns-batch2-protocolspecific/AMM/lp_share_dilution.md` — Lp Share Dilution
- `attack-patterns-batch2-protocolspecific/AMM/reserve_desync.md` — Reserve Desync
- `attack-patterns-batch2-protocolspecific/AMM/swap_fee_miscalculation.md` — Swap Fee Miscalculation
- `attack-patterns-batch2-protocolspecific/AMM/virtual_reserve_bug.md` — Virtual Reserve Bug
- `attack-patterns-batch2-protocolspecific/ERC20/allowance_desync.md` — Allowance Desync
- `attack-patterns-batch2-protocolspecific/ERC20/approval_race.md` — Approval Race
- `attack-patterns-batch2-protocolspecific/ERC20/blacklist_token_assumption.md` — Blacklist Token Assumption
- `attack-patterns-batch2-protocolspecific/ERC20/deflationary_token_accounting.md` — Deflationary Token Accounting
- `attack-patterns-batch2-protocolspecific/ERC20/fee_on_transfer_assumption.md` — Fee On Transfer Assumption
- `attack-patterns-batch2-protocolspecific/ERC20/non_standard_return_values.md` — Non Standard Return Values
- `attack-patterns-batch2-protocolspecific/ERC20/permit_validation.md` — Permit Validation
- `attack-patterns-batch2-protocolspecific/ERC20/rebasing_token_assumption.md` — Rebasing Token Assumption
- `attack-patterns-batch2-protocolspecific/ERC4626/deposit_withdraw_asymmetry.md` — Deposit Withdraw Asymmetry
- `attack-patterns-batch2-protocolspecific/ERC4626/donation_attack.md` — Donation Attack
- `attack-patterns-batch2-protocolspecific/ERC4626/empty_vault_attack.md` — Empty Vault Attack
- `attack-patterns-batch2-protocolspecific/ERC4626/inflation_attack.md` — Inflation Attack
- `attack-patterns-batch2-protocolspecific/ERC4626/preview_desync.md` — Preview Desync
- `attack-patterns-batch2-protocolspecific/ERC4626/rounding_loss.md` — Rounding Loss
- `attack-patterns-batch2-protocolspecific/ERC4626/share_accounting_desync.md` — Share Accounting Desync
- `attack-patterns-batch2-protocolspecific/ERC4626/share_price_manipulation.md` — Share Price Manipulation
- `attack-patterns-batch2-protocolspecific/Governance/delegate_voting_abuse.md` — Delegate Voting Abuse
- `attack-patterns-batch2-protocolspecific/Governance/emergency_admin_abuse.md` — Emergency Admin Abuse
- _... +21 more files in this category_

### `attack-patterns-batch3-advancedprotocols/` (65 files)

- `attack-patterns-batch3-advancedprotocols/Bridge/bridge_accounting_desync.md` — Bridge Accounting Desync
- `attack-patterns-batch3-advancedprotocols/Bridge/bridge_pause_bypass.md` — Bridge Pause Bypass
- `attack-patterns-batch3-advancedprotocols/Bridge/guardian_compromise.md` — Guardian Compromise
- `attack-patterns-batch3-advancedprotocols/Bridge/invalid_message_verification.md` — Invalid Message Verification
- `attack-patterns-batch3-advancedprotocols/Bridge/message_replay.md` — Message Replay
- `attack-patterns-batch3-advancedprotocols/Bridge/mint_burn_desync.md` — Mint Burn Desync
- `attack-patterns-batch3-advancedprotocols/Bridge/withdrawal_proof_bypass.md` — Withdrawal Proof Bypass
- `attack-patterns-batch3-advancedprotocols/Bridge/wrapped_asset_desync.md` — Wrapped Asset Desync
- `attack-patterns-batch3-advancedprotocols/CrossChain/async_state_desync.md` — Async State Desync
- `attack-patterns-batch3-advancedprotocols/CrossChain/chainid_assumption.md` — Chainid Assumption
- `attack-patterns-batch3-advancedprotocols/CrossChain/cross_chain_replay.md` — Cross Chain Replay
- `attack-patterns-batch3-advancedprotocols/CrossChain/cross_domain_auth.md` — Cross Domain Auth
- `attack-patterns-batch3-advancedprotocols/CrossChain/failed_message_recovery.md` — Failed Message Recovery
- `attack-patterns-batch3-advancedprotocols/CrossChain/message_ordering.md` — Message Ordering
- `attack-patterns-batch3-advancedprotocols/CrossChain/partial_execution.md` — Partial Execution
- `attack-patterns-batch3-advancedprotocols/LiquidStaking/exchange_rate_manipulation.md` — Exchange Rate Manipulation
- `attack-patterns-batch3-advancedprotocols/LiquidStaking/oracle_backed_lsd_mispricing.md` — Oracle Backed Lsd Mispricing
- `attack-patterns-batch3-advancedprotocols/LiquidStaking/share_mint_rounding.md` — Share Mint Rounding
- `attack-patterns-batch3-advancedprotocols/LiquidStaking/slash_accounting_bug.md` — Slash Accounting Bug
- `attack-patterns-batch3-advancedprotocols/LiquidStaking/unstake_queue_attack.md` — Unstake Queue Attack
- `attack-patterns-batch3-advancedprotocols/LiquidStaking/validator_reward_desync.md` — Validator Reward Desync
- `attack-patterns-batch3-advancedprotocols/LiquidStaking/withdraw_queue_bypass.md` — Withdraw Queue Bypass
- `attack-patterns-batch3-advancedprotocols/Options/collateral_release_bug.md` — Collateral Release Bug
- `attack-patterns-batch3-advancedprotocols/Options/exercise_validation_bug.md` — Exercise Validation Bug
- `attack-patterns-batch3-advancedprotocols/Options/expiry_timestamp_bug.md` — Expiry Timestamp Bug
- _... +40 more files in this category_

### `bughunter-phase1/` (10 files)

- `bughunter-phase1/README.md` — Phase 1 — Foundation & Repository Intelligence
- `bughunter-phase1/architecture_analysis.md` — Architecture Analysis
- `bughunter-phase1/audit_mindset.md` — Audit Mindset
- `bughunter-phase1/call_graph.md` — Call Graph
- `bughunter-phase1/completion_checklist.md` — Completion Checklist
- `bughunter-phase1/dependency_analysis.md` — Dependency Analysis
- `bughunter-phase1/identity.md` — Identity
- `bughunter-phase1/protocol_summary.md` — Protocol Summary
- `bughunter-phase1/repository_mapper.md` — Repository Mapper
- `bughunter-phase1/storage_layout.md` — Storage Layout

### `bughunter-phase2/` (13 files)

- `bughunter-phase2/README.md` — Phase 2 — Protocol Modeling
- `bughunter-phase2/actors.md` — Actors
- `bughunter-phase2/asset_flow.md` — Asset Flow
- `bughunter-phase2/assets.md` — Assets
- `bughunter-phase2/completion_checklist.md` — Completion Checklist
- `bughunter-phase2/critical_state.md` — Critical State
- `bughunter-phase2/external_dependencies.md` — External Dependencies
- `bughunter-phase2/invariant_preparation.md` — Invariant Preparation
- `bughunter-phase2/permission_matrix.md` — Permission Matrix
- `bughunter-phase2/privileges.md` — Privileged Operations
- `bughunter-phase2/protocol_assumptions.md` — Protocol Assumptions
- `bughunter-phase2/roles.md` — Roles & Permissions
- `bughunter-phase2/trust_boundaries.md` — Trust Boundaries

### `bughunter-phase3/` (10 files)

- `bughunter-phase3/README.md` — Phase 3 — Invariant Engineering
- `bughunter-phase3/accounting_invariants.md` — Accounting Invariants
- `bughunter-phase3/attack_hypotheses.md` — Attack Hypotheses
- `bughunter-phase3/candidate_exploits.md` — Candidate Exploits
- `bughunter-phase3/completion_checklist.md` — Completion Checklist
- `bughunter-phase3/economic_invariants.md` — Economic Invariants
- `bughunter-phase3/invariant_methodology.md` — Invariant Methodology
- `bughunter-phase3/invariant_validation.md` — Validation
- `bughunter-phase3/permission_invariants.md` — Permission Invariants
- `bughunter-phase3/state_machine_invariants.md` — State Machine Invariants

### `bughunter-phase4/` (10 files)

- `bughunter-phase4/README.md` — Phase 4 — Attack Surface Intelligence
- `bughunter-phase4/callbacks_hooks.md` — Callbacks & Hooks
- `bughunter-phase4/completion_checklist.md` — Completion Checklist
- `bughunter-phase4/cross_contract.md` — Cross-Contract Surface
- `bughunter-phase4/entry_points.md` — Entry Points
- `bughunter-phase4/escalation_rules.md` — Escalation Rules
- `bughunter-phase4/external_calls.md` — External Calls
- `bughunter-phase4/oracle_surface.md` — Oracle Surface
- `bughunter-phase4/token_compatibility.md` — Token Compatibility
- `bughunter-phase4/upgrade_surface.md` — Upgrade & Admin Surface

### `bughunter-phase5/` (10 files)

- `bughunter-phase5/README.md` — Phase 5 — Module Audit
- `bughunter-phase5/access_control.md` — Access Control
- `bughunter-phase5/completion_checklist.md` — Completion Checklist
- `bughunter-phase5/delegatecall.md` — Delegatecall & Upgradeability
- `bughunter-phase5/erc4626.md` — ERC4626
- `bughunter-phase5/false_positive_filter.md` — False Positive Filter
- `bughunter-phase5/flashloan.md` — Flash Loans
- `bughunter-phase5/oracle.md` — Oracle
- `bughunter-phase5/precision.md` — Precision & Math
- `bughunter-phase5/reentrancy.md` — Reentrancy

### `bughunter-phase6/` (9 files)

- `bughunter-phase6/README.md` — Phase 6 — Economic Attack Analysis
- `bughunter-phase6/accounting_attacks.md` — Accounting Attacks
- `bughunter-phase6/candidate_exploits.md` — Candidate Exploits
- `bughunter-phase6/completion_checklist.md` — Completion Checklist
- `bughunter-phase6/governance_attacks.md` — Governance Attacks
- `bughunter-phase6/liquidity_attacks.md` — Liquidity Attacks
- `bughunter-phase6/oracle_economics.md` — Oracle Economics
- `bughunter-phase6/profitability.md` — Profitability
- `bughunter-phase6/threat_model.md` — Threat Model

### `bughunter-phase7/` (9 files)

- `bughunter-phase7/README.md` — Phase 7 — Exploit Construction & Validation
- `bughunter-phase7/attacker_model.md` — Attacker Model
- `bughunter-phase7/completion_checklist.md` — Completion Checklist
- `bughunter-phase7/confidence_scoring.md` — Confidence Scoring
- `bughunter-phase7/execution_trace.md` — Execution Trace
- `bughunter-phase7/exploit_builder.md` — Exploit Builder
- `bughunter-phase7/impact_analysis.md` — Impact Analysis
- `bughunter-phase7/poc_requirements.md` — Proof of Concept Requirements
- `bughunter-phase7/report_handoff.md` — Report Handoff

### `bughunter-phase8/` (8 files)

- `bughunter-phase8/README.md` — Phase 8 — Final Review & Reporting
- `bughunter-phase8/completion_checklist.md` — Completion Checklist
- `bughunter-phase8/evidence_collection.md` — Evidence Collection
- `bughunter-phase8/false_positive_review.md` — False Positive Review
- `bughunter-phase8/final_quality_gate.md` — Final Quality Gate
- `bughunter-phase8/fix_recommendation.md` — Fix Recommendation
- `bughunter-phase8/report_template.md` — Report Template
- `bughunter-phase8/severity_classification.md` — Severity Classification

### `exploit-kb-batch1/` (11 files)

- `exploit-kb-batch1/README.md` — Pack B — Exploit Knowledge Base (Batch 1)
- `exploit-kb-batch1/beanstalk.md` — Beanstalk
- `exploit-kb-batch1/curve.md` — Curve
- `exploit-kb-batch1/euler_finance.md` — Euler Finance
- `exploit-kb-batch1/hundred_finance.md` — Hundred Finance
- `exploit-kb-batch1/mango_markets.md` — Mango Markets
- `exploit-kb-batch1/nomad_bridge.md` — Nomad Bridge
- `exploit-kb-batch1/prisma_finance.md` — Prisma Finance
- `exploit-kb-batch1/radiant_capital.md` — Radiant Capital
- `exploit-kb-batch1/sonne_finance.md` — Sonne Finance
- `exploit-kb-batch1/wormhole.md` — Wormhole

### `exploit-kb-batch2/` (16 files)

- `exploit-kb-batch2/README.md` — Pack B — Exploit Knowledge Base (Batch 2)
- `exploit-kb-batch2/balancer.md` — Balancer
- `exploit-kb-batch2/bzx.md` — bZx
- `exploit-kb-batch2/conic_finance.md` — Conic Finance
- `exploit-kb-batch2/cream_finance.md` — Cream Finance
- `exploit-kb-batch2/fei_rari.md` — Fei / Rari
- `exploit-kb-batch2/inverse_finance.md` — Inverse Finance
- `exploit-kb-batch2/kyberswap_elastic.md` — KyberSwap Elastic
- `exploit-kb-batch2/midas_capital.md` — Midas Capital
- `exploit-kb-batch2/paraspace.md` — ParaSpace
- `exploit-kb-batch2/platypus.md` — Platypus
- `exploit-kb-batch2/raft.md` — Raft
- `exploit-kb-batch2/ronin_bridge.md` — Ronin Bridge
- `exploit-kb-batch2/sentiment.md` — Sentiment
- `exploit-kb-batch2/transit_swap.md` — Transit Swap
- `exploit-kb-batch2/uwu_lend.md` — UwU Lend

### `exploit-kb-batch3/` (36 files)

- `exploit-kb-batch3/Accounting_Failures/debt_accounting.md` — Debt Accounting
- `exploit-kb-batch3/Accounting_Failures/donation_accounting.md` — Donation Accounting
- `exploit-kb-batch3/Accounting_Failures/reserve_accounting.md` — Reserve Accounting
- `exploit-kb-batch3/Accounting_Failures/reward_accounting_desync.md` — Reward Accounting Desync
- `exploit-kb-batch3/Accounting_Failures/share_inflation.md` — Share Inflation
- `exploit-kb-batch3/Cross_Chain/bridge_pause_failure.md` — Bridge Pause Failure
- `exploit-kb-batch3/Cross_Chain/message_validation.md` — Message Validation
- `exploit-kb-batch3/Cross_Chain/mint_burn_desync.md` — Mint Burn Desync
- `exploit-kb-batch3/Cross_Chain/proof_verification.md` — Proof Verification
- `exploit-kb-batch3/Cross_Chain/replay_attack.md` — Replay Attack
- `exploit-kb-batch3/Flash_Loan/capital_amplification.md` — Capital Amplification
- `exploit-kb-batch3/Flash_Loan/governance_flashloan.md` — Governance Flashloan
- `exploit-kb-batch3/Flash_Loan/liquidity_flashloan.md` — Liquidity Flashloan
- `exploit-kb-batch3/Flash_Loan/nested_flashloan.md` — Nested Flashloan
- `exploit-kb-batch3/Flash_Loan/oracle_flashloan.md` — Oracle Flashloan
- `exploit-kb-batch3/Governance/delegate_abuse.md` — Delegate Abuse
- `exploit-kb-batch3/Governance/proposal_execution.md` — Proposal Execution
- `exploit-kb-batch3/Governance/quorum_attack.md` — Quorum Attack
- `exploit-kb-batch3/Governance/timelock_bypass.md` — Timelock Bypass
- `exploit-kb-batch3/Governance/vote_snapshot.md` — Vote Snapshot
- `exploit-kb-batch3/Oracle_Manipulation/decimal_mismatch.md` — Decimal Mismatch
- `exploit-kb-batch3/Oracle_Manipulation/low_liquidity_oracle.md` — Low Liquidity Oracle
- `exploit-kb-batch3/Oracle_Manipulation/price_oracle_spot_manipulation.md` — Price Oracle Spot Manipulation
- `exploit-kb-batch3/Oracle_Manipulation/stale_oracle_usage.md` — Stale Oracle Usage
- `exploit-kb-batch3/Oracle_Manipulation/twap_window_abuse.md` — Twap Window Abuse
- _... +11 more files in this category_

### `orchestrator-batch1/` (7 files)

- `orchestrator-batch1/README.md` — Pack D — Orchestrator (Batch 1)
- `orchestrator-batch1/audit_planner.md` — Audit Planner
- `orchestrator-batch1/context_builder.md` — Context Builder
- `orchestrator-batch1/dependency_loader.md` — Dependency Loader
- `orchestrator-batch1/knowledge_selector.md` — Knowledge Selector
- `orchestrator-batch1/protocol_detector.md` — Protocol Detector
- `orchestrator-batch1/repository_classifier.md` — Repository Classifier

### `orchestrator-batch2/` (6 files)

- `orchestrator-batch2/README.md` — Pack D — Orchestrator (Batch 2)
- `orchestrator-batch2/confidence_engine.md` — Confidence Engine
- `orchestrator-batch2/decision_tree.md` — Decision Tree
- `orchestrator-batch2/false_positive_engine.md` — False Positive Engine
- `orchestrator-batch2/hypothesis_engine.md` — Hypothesis Engine
- `orchestrator-batch2/invariant_engine.md` — Invariant Engine

### `orchestrator-batch3/` (6 files)

- `orchestrator-batch3/README.md` — Pack D — Orchestrator (Batch 3)
- `orchestrator-batch3/coverage_tracker.md` — Coverage Tracker
- `orchestrator-batch3/parallel_analysis.md` — Parallel Analysis
- `orchestrator-batch3/phase_scheduler.md` — Phase Scheduler
- `orchestrator-batch3/priority_queue.md` — Priority Queue
- `orchestrator-batch3/task_dispatcher.md` — Task Dispatcher

### `orchestrator-batch4/` (6 files)

- `orchestrator-batch4/README.md` — Pack D — Orchestrator (Batch 4)
- `orchestrator-batch4/attack_pattern_cache.md` — Attack Pattern Cache
- `orchestrator-batch4/context_memory.md` — Context Memory
- `orchestrator-batch4/exploit_cache.md` — Exploit Cache
- `orchestrator-batch4/finding_memory.md` — Finding Memory
- `orchestrator-batch4/protocol_memory.md` — Protocol Memory

### `orchestrator-batch5/` (6 files)

- `orchestrator-batch5/README.md` — Pack D — Orchestrator (Batch 5)
- `orchestrator-batch5/evidence_collector.md` — Evidence Collector
- `orchestrator-batch5/fix_generator.md` — Fix Generator
- `orchestrator-batch5/poc_builder.md` — Poc Builder
- `orchestrator-batch5/report_generator.md` — Report Generator
- `orchestrator-batch5/severity_engine.md` — Severity Engine

### `orchestrator-batch6/` (7 files)

- `orchestrator-batch6/BugHunterOS_v1_Architecture.md` — BugHunter OS v1.0 Architecture
- `orchestrator-batch6/README.md` — Pack D — Orchestrator (Batch 6)
- `orchestrator-batch6/consistency_checker.md` — Consistency Checker
- `orchestrator-batch6/critic_agent.md` — Critic Agent
- `orchestrator-batch6/false_positive_review.md` — False Positive Review
- `orchestrator-batch6/quality_gate.md` — Quality Gate
- `orchestrator-batch6/second_opinion.md` — Second Opinion

### `protocol-playbooks-batch1/` (11 files)

- `protocol-playbooks-batch1/README.md` — Pack C — Protocol Playbooks (Batch 1)
- `protocol-playbooks-batch1/amm.md` — AMM
- `protocol-playbooks-batch1/bridge.md` — Bridge
- `protocol-playbooks-batch1/erc4626_vault.md` — ERC4626 Vault
- `protocol-playbooks-batch1/governance.md` — Governance
- `protocol-playbooks-batch1/lending.md` — Lending
- `protocol-playbooks-batch1/liquid_staking.md` — Liquid Staking
- `protocol-playbooks-batch1/perpetuals.md` — Perpetuals
- `protocol-playbooks-batch1/restaking.md` — Restaking
- `protocol-playbooks-batch1/stablecoin.md` — Stablecoin
- `protocol-playbooks-batch1/yield_aggregator.md` — Yield Aggregator

### `protocol-playbooks-batch2/` (11 files)

- `protocol-playbooks-batch2/README.md` — Pack C — Protocol Playbooks (Batch 2)
- `protocol-playbooks-batch2/account_abstraction.md` — Account Abstraction
- `protocol-playbooks-batch2/auction_protocols.md` — Auction Protocols
- `protocol-playbooks-batch2/cross_chain_messaging.md` — Cross Chain Messaging
- `protocol-playbooks-batch2/intent_based_protocols.md` — Intent Based Protocols
- `protocol-playbooks-batch2/nft_marketplaces.md` — NFT Marketplaces
- `protocol-playbooks-batch2/prediction_markets.md` — Prediction Markets
- `protocol-playbooks-batch2/rollup_infrastructure.md` — Rollup Infrastructure
- `protocol-playbooks-batch2/rwa.md` — RWA
- `protocol-playbooks-batch2/treasury_multisig.md` — Treasury Multisig
- `protocol-playbooks-batch2/vesting_distribution.md` — Vesting Distribution

---

## 💡 Usage Tips

- **Start with INDEX.md** for any new task — don't browse all 347 files
- **Phase-based queries** → jump to relevant phase
- **Vulnerability hunts** → use Vulnerability Classes section
- **Protocol audits** → load playbook for that protocol type
- **Always end with quality gate** (`orchestrator-batch6/quality_gate.md`) before delivery

## 🔄 Update Policy

This index is auto-generated. To regenerate after adding new skills, re-run the indexer script that built this file.
