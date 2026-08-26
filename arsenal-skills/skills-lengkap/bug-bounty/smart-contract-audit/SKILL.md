---
name: smart-contract-audit
description: Audit smart contracts for security vulnerabilities. Use when user says "audit", "review this contract", "find bugs", "bounty", "security review", or points at a repo/program for vulnerability assessment. Covers Anchor/Solana, EVM/Solidity, and general patterns. Includes content-compression workarounds.
---

# Smart Contract Security Audit

## Trigger
User asks to audit a contract, find vulnerabilities, review code for bugs, or participate in bug bounty/audit contest.

## Audit Methodology (Ordered)

### 1. RECON — Understand the Protocol
- Read README, docs, spec files first
- Map the architecture: what actors exist, what actions they take, what assets move
- Identify **trust assumptions**: who is trusted (admin, oracle, upgrade authority)?
- Map the **attack surface**: every external call, every token transfer, every state mutation

### 2. SCOPE — What Matters
- Focus on **fund loss** and **permanent fund lock** vectors
- Ignore: gas optimization, code style, theoreticals without PoC, known issues
- Read the audit scope/bounty page carefully — know what's in/out of scope

### 3. CODE REVIEW — Systematic
For Anchor/Solana:
1. `lib.rs` → all instruction entrypoints
2. `state/*.rs` → account structs, PDA seeds, state machines
3. `instructions/*/<name>.rs` → each handler + account validation
4. `rewards.rs` / business logic → math, rounding, overflow
5. `error.rs` / `constants.rs` → custom errors, seeds, magic numbers
6. `tests/` → integration/LiteSVM tests — reveals edge cases and trust boundaries

For EVM/Solidity:
1. Interfaces → external call surface
2. Storage layout → upgrade safety, collision risk
3. Access control → onlyOwner, modifiers, role checks
4. Token flows → transfer, approve, burn, mint paths
5. Math → rounding direction, precision loss, overflow
6. Reentrancy → CEI pattern, cross-function, read-only

### 4. HYPOTHESIZE — Per Instruction
For each instruction: "What if caller is malicious? What if args are crafted? What if called in unexpected order? What if called twice?"

### 5. PoC — Working Exploit
- Foundry test for EVM, LiteSVM test or TypeScript for Anchor
- Prove fund loss or permanent lock
- Theory without runnable PoC = not a finding

### 6. REPORT
- Concise: vulnerability class, root cause, impact, PoC, fix
- Match program's format requirements (char limits, severity labels)

## Attack Vectors Checklist

### Universal
- [ ] Integer overflow/underflow (checked math?)
- [ ] Rounding errors (division before multiplication?)
- [ ] Access control bypass (signer check? PDA validation?)
- [ ] Reentrancy (CEI violation? cross-program invocation order?)
- [ ] Input validation (zero address? array length mismatch?)
- [ ] Race conditions (same-block state mutation?)

### Solana/Anchor Specific
- [ ] PDA seed uniqueness (can seeds collide?)
- [ ] Account validation (owner check? address constraint? mutability?)
- [ ] Signer vs UncheckedAccount (who signs? who pays?)
- [ ] Token account authority (who controls vault? mint authority?)
- [ ] CPIs (program ID checked? correct seeds passed?)
- [ ] init vs init_if_needed (re-initialization risk?)
- [ ] close/destroy (rent refund to correct target?)

### DeFi Specific
- [ ] Reward calculation (pro-rata rounding? first/last claim advantage?)
- [ ] Oracle dependency (stale price? manipulatable source?)
- [ ] Flash loan surface (price derived from pool balances?)
- [ ] Governance (flash loan voting? timelock bypass?)
- [ ] Upgrade proxy (storage collision? uninitialized state?)

## Content Compression Workarounds

When tool outputs get compressed/redacted (showing `<<ccr:...>>` instead of actual content):

1. **Read small files first** — files under ~4KB often pass through `read_file` uncompressed
2. **Terminal sed for individual lines** — `sed -n 'Np' file` for single lines often escapes compression. Batch 5-10 lines at once.
3. **Copy to /tmp/*.txt** — sometimes bypasses extension-based filters (less reliable than sed)
4. **File-by-file audit** — use terminal `cat` for files you know should be small (state structs, errors, constants)
5. **When all else fails**: work from readable surface (tests, README, config) + grep for function signatures and error strings. You can reconstruct attack surface from test code alone.

**Pattern**: compression hits hardest on Hoon files and large Rust files (>500 lines). Small Anchor state files and test files often pass through.

## Perceptron Case Study

### Protocol: Perceptron Network (Anchor/Solana)
- Reward distribution for node operators
- Epoch-based: open → finalize → claim → sweep
- Actors: Upgrade Authority (init), Admin (update config), Oracle (epoch management + claim creation), User (claim reward)

### Audit Result: NO CRITICAL FINDINGS
All value-transfer paths gated behind trusted roles:
- `initialize_config`: upgrade-authority only
- `update_config`: admin only (can change curve/weights/oracle)
- `open_epoch`: oracle only, SOL from funder to epoch PDA
- `finalize_epoch`: oracle only, mints reward tokens, refunds unused SOL
- `create_claim`: oracle only, PDA `[CLAIM_SEED, epoch_id, user]` — one per user per epoch
- `claim_reward`: user signs, PDA matches `claim.user == signer`, no duplicate redemption
- `sweep_epoch`: oracle only (after deadline), moves unclaimed tokens to reserve

### Key Security Properties
- PDA seeds prevent duplicate claims
- Reward math uses checked arithmetic throughout
- Vault tokens only movable via mint_authority PDA signer
- SOL reserve has no withdrawal instruction (permanently locked by design)
- Comprehensive LiteSVM tests cover: wrong user, duplicate claim, invalid metrics, non-oracle rejection, funder refund constraints
