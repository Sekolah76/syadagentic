---
name: Cosmos SDK + EVM chain audits: see references/cosmos-sdk-chain-audit.md
description: Smart contract security audit — 11 DeFi bug classes (accounting desync, access control, incomplete path, off-by-one, oracle, ERC4626, reentrancy, flash loan, signature replay, proxy, BFT/consensus/liveness), pre-dive kill signals (TVL < $500K etc), Foundry PoC template, grep patterns for each class, and real Immunefi paid examples. Use for any Solidity/Rust contract audit or when deciding whether a DeFi target is worth hunting.
---

# WEB3 SMART CONTRACT & BFT CONSENSUS AUDIT

11 bug classes. Pre-dive kill signals. Foundry PoC template. Real paid examples.

---

## PRE-DIVE KILL SIGNALS (check BEFORE any code review)

> ZKsync lesson: $322M TVL + OZ audit + 750K LOC + 5 sessions = 0 findings. Large well-audited bridges are extremely hard.

1. **TVL < $500K** → max payout capped too low for effort
2. **2+ top-tier audits** (Halborn, ToB, Cyfrin, OpenZeppelin) on simple protocol → bugs already found
3. **Protocol < 500 lines, single A→B→C flow** → minimal attack surface
4. **Formula**: `max_realistic_payout = min(10% × TVL, program_cap)` — if < $10K, skip

**Soft kill:** OZ/ToB/Cyfrin audit on current version + codebase > 500K LOC → expect 40+ hours for maybe 1 finding. Only proceed if bounty floor > $50K AND you have protocol-specific expertise.

**Target scoring (go if >= 6/10):**
- TVL > $10M: +2
- Immunefi program with Critical >= $50K: +2
- No top-tier audit on current version: +2
- < 30 days since deploy: +1
- Protocol you've hunted before: +1
- Source code + natspec comments: +1
- Upgradeable proxies: +1

---

## CONTEST SOURCE-INTEGRITY GATE (Sherlock)

Before reviewing or testing a Sherlock contest, record the **exact scope commit** and verify the source tree you are reading matches it.

1. Read the contest page/API and record: contest ID, end time, reward pool, `scope[].repo`, `scope[].commit_hash`, scoped file list, trust assumptions, known issues, and live-issues status.
2. Prefer the official contest repository/archive at the pinned commit. Verify with `git rev-parse HEAD` or the archive commit in the source URL.
3. **Do not silently substitute `main`.** If the scoping repository or pinned object is private/unavailable anonymously, a public contest template may still provide useful orientation, but treat it as *hypothesis-only*. Do not submit, publish a PoC, or claim a line-level finding until the exact commit is obtained.
4. Inspect the template layout before assuming the source root: Sherlock templates can put the actual project under a nested directory while the outer `README.md` only contains contest metadata. Locate `foundry.toml`, `contracts/`, `test/`, `SECURITY.md`, and `specs/` before running searches or tests.
5. Read `SECURITY.md`, previous-audit/known-issue material, and the contest Q&A before triage. Turn explicit role trust assumptions into an exclusion matrix; only pursue untrusted caller paths that meet the contest severity bar.
6. If **Live Issues** is enabled, apply an extra gate: require exact-commit evidence, a reproducible proof, and a concrete Medium+ impact before opening an issue. A speculative report is immediately exposed to the protocol and burns the surface.

**Audit note format**
```text
Contest: #<id> | source commit: <sha>
Source verification: exact / hypothesis-only (reason)
In scope: <files/modules>
Trusted/excluded: <roles and classes>
Known issues avoided: <references>
Target invariant: <untrusted actor → CIA impact>
```

---

## Scope provenance and regression gate

When the contest's advertised commit is unavailable, record the advertised hash, actual `HEAD`, and remote before analysis. Use mismatched snapshots only to generate hypotheses and validate regressions; do not call a result submission-ready until affected lines are verified against the official scoped artifact. For batched NAV or asynchronous vault findings, test mid-cycle ownership/list/config/cash mutations and both focused and full Foundry suites. See [references/scoped-source-provenance-and-regression.md](references/scoped-source-provenance-and-regression.md).

For pulling verified contract source code without Etherscan API keys, see [references/etherscan-alternatives.md](references/etherscan-alternatives.md).

---

## PRE-AUDIT DUPLICATE CHECK (before writing a single line of code)

> Paraloom lesson: $3K pool, 100+ issues filed in 7 days. Skipping this step = wasting hours on a duplicate.

Always enumerate **existing issues + security log** before starting any code review:

```
# GitHub API — dump ALL issues (open + closed), filter by label/title body
curl -s "https://api.github.com/repos/{org}/{repo}/issues?state=all&per_page=100" | \
  jq '.[] | "#\(.number) [\(.state)] \(.title) — \(.user.login)"'
```

### Kill signals from issue scan
- Already-reported auth bypass → skip anything similar in that code path
- Security log claims "fixed" → verify the fix is actually deployed in the current commit
- Duplicate of an open issue → different root cause? If not, skip
- Same researcher filed 5+ findings in one subsystem → that subsystem is saturated, move to unexplored areas

### Tools for large Rust/Anchor codebases
```bash
# Search patterns across ALL source files
grep -rn "unbounded\|unchecked\|unwrap\|expect\|as u64\|as u32\|as usize" src/ programs/

# Find auth gate mismatches — siblings with different guard levels
grep -rn "node_info.node_type" src/ | sort

# Find unbounded collections (memory-exhaustion candidates)
grep -rn "Vec<\|HashMap<" src/ --include="*.rs" | grep -v "test\|cfg(test)" | \
  grep -v "mutex\|RwLock\|bounded\|cap\|MAX" | head -30
```

### When NOT to skip despite existing issues
- Finding is a **novel variant** of a known class (e.g. co-sign reuse was reported but keyed on nullifiers — a request-id-keyed variant is different)
- Security log says "fixed" but the fix is a **partial mitigation** with a bypass
- Finding is in a module explicitly excluded from a prior security audit's scope

---

## THE ONE RULE

> "Read ALL sibling functions. If `vote()` has a modifier, check `poke()`, `reset()`, `harvest()`. The missing modifier on the sibling IS the bug."

This single rule explains 19% of all Critical findings.

---

## 1. ACCOUNTING STATE DESYNCHRONIZATION
> #1 Critical bug class — 28% of all Criticals on Immunefi.

### What It Is
Two state variables supposed to stay in sync. One code path updates A but forgets B. Later code reads both and makes decisions based on stale B.

```
Real Value = A - B
If A updated but B isn't → Real Value appears larger → phantom value
```

### Root Cause Patterns

**Variant 1: Phantom Yield** (Yeet protocol — 35 duplicate reports)
```solidity
function startUnstake(uint256 amount) external {
    totalSupply -= amount;  // decremented BEFORE transfer
    // aToken.balanceOf(this) still reflects old value
    // yieldAmount = aToken.balanceOf - totalSupply = phantom yield
}
```

**Variant 2: Fast Path Skips State Update** (Alchemix V3)
```solidity
function claimRedemption(uint256 tokenId) external {
    if (transmuter.balance >= amount) {
        transmuter.transfer(user, amount);
        _burn(tokenId);
        return;  // EARLY RETURN — cumulativeEarmarked, _redemptionWeight, totalDebt never updated
    }
    // Slow path: updates all state vars correctly
    alchemist.redeem(...);
}
```

**Variant 3: Update Happens in Wrong Order** (Alchemix)
```solidity
function deposit(uint256 amount) external {
    _shares = (amount * totalShares) / totalAssets;  // calculated BEFORE deposit
    totalAssets += amount;   // assets added AFTER shares calculated → wrong rate
}
```

### Grep Patterns
```bash
# Find all accounting variables
grep -rn "totalSupply\|totalShares\|totalAssets\|totalDebt\|cumulativeReward\|rewardPerShare" contracts/

# Find all early returns in claim/redeem functions
grep -rn "\breturn\b" contracts/ -B3 | grep -B3 "if\b"

# For each early return: which state updates in normal path are skipped?
```

---

## 2. ACCESS CONTROL
> #2 Critical — 19% of Criticals. $953M lost in 2024 alone.

### Variant 1: Missing Modifier on Sibling Function
```solidity
function vote(uint256 tokenId) external onlyNewEpoch(tokenId) {  // guarded
function reset(uint256 tokenId) external onlyNewEpoch(tokenId) { // guarded
function poke(uint256 tokenId) external {                         // NO GUARD → infinite FLUX inflation
}
```

### Variant 2: Wrong Check (Existence vs Ownership)
```solidity
function split(uint256 tokenId, uint256 amount) external {
    _requireOwned(tokenId);  // checks if token EXISTS, not if caller OWNS it
    _burn(tokenId);
    _mint(msg.sender, amount);  // attacker steals tokens they don't own
}
```

### Variant 3: Silent Modifier (if vs require)
```solidity
// VULNERABLE — non-admin silently gets through:
modifier onlyAdmin() {
    if (msg.sender == admin) {
        _;  // body only executes for admin, but non-admin doesn't revert
    }
}
// CORRECT: require(msg.sender == admin, "Not admin"); _;
```

### Variant 4: Uninitialized Proxy
```solidity
function initialize(address _owner) public {  // MISSING: initializer modifier
    owner = _owner;  // anyone can call → become owner
}
// Fix: constructor() { _disableInitializers(); }
```

### Variant 5: Two-Transaction Deployment Frontrunning
When an L2/custom chain forces `msg.sender = address(0)` during `ContractCreate` (e.g., Goliath/Onyx Mainnet relay), the deployer must call `init()` in a **separate transaction**. This creates a frontrunning window: any mempool watcher can call `init()` first and hijack ownership.

```solidity
/// @dev "Deploy this contract, then call init() in a separate tx."
///      msg.sender=address(0) in ContractCreate → can't set owner in constructor.
constructor() {}  // empty — no _disableInitializers either

function init(address owner_, ...) external initializer {
    __Ownable_init(owner_);  // anyone can call → set themselves as owner
}
```

**Kill signal:** constructor is empty AND `init()` has no caller restriction AND code comments mention "separate tx" or "msg.sender=address(0)".

**Fix patterns:**
- Factory contract that deploys + initializes atomically in one tx
- Pass deployer address as constructor arg and require `msg.sender == _deployer` in `init()`
- Use `tx.origin` guard in constructor (less ideal but workable)
- Use CREATE2 with initialization calldata bundled

**Severity:** Medium if contract has no funds at deploy time (deployer can just redeploy). High if funds/integrations proceed before ownership is verified.

### Grep Patterns
```bash
# Find sibling function families — do ALL have the same modifier set?
grep -rn "function vote\|function poke\|function reset\|function update\|function claim\|function harvest" contracts/ -A2

# Ownership check: existence vs ownership?
grep -rn "_requireOwned\|ownerOf\|_isApprovedOrOwner\|_checkAuthorized" contracts/ -B5

# Silent modifiers
grep -rn "modifier\b" contracts/ -A8 | grep -B3 "if (" | grep -v "require\|revert"

# Uninitialized initializer
grep -rn "function initialize\b" contracts/ -A3
grep -rn "_disableInitializers()" contracts/
```

### Real Paid Examples

| Protocol | Payout | Bug |
|---|---|---|
| Wormhole | $10M | Uninitialized UUPS proxy → anyone calls initialize() |
| ZeroLend | n/a | split() uses existence check, not ownership check |
| Alchemix | n/a | poke() missing onlyNewEpoch → infinite FLUX inflation |
| Parity | $150M frozen | No access control on initWallet() in library |

---

## 3. INCOMPLETE CODE PATH
> #3 Critical — 17% of Criticals.

### The Function Family Comparison Test
```
1. List all state changes in function A (deposit/place/create)
2. List all state changes in function B (withdraw/update/cancel)
3. For each state change in A: does B have the corresponding reverse?
4. For each token transfer in A: does B have the corresponding refund?
If A does X but B doesn't do the reverse of X → BUG.
```

### Variant 1: Update Function Missing Refund (ThunderNFT)
```solidity
function place_order(OrderInput calldata order) external {
    token.safeTransferFrom(msg.sender, address(this), order.price);  // takes tokens
    orders[orderId] = order;
}
function update_order(OrderInput calldata updatedOrder) external {
    // BUG: NO REFUND for sell orders when price decreases → tokens permanently stuck
    orders[orderId] = updatedOrder;
}
```

### Variant 2: Partial Fill Token Stuck (Plume)
```solidity
function swapForETH(uint256 amountIn) external {
    token.safeTransferFrom(msg.sender, address(this), amountIn);
    uint256 filled = dex.swap(amountIn);  // partial fill possible
    _refundExcessEth(amountIn - filled);  // BUG: refunds ETH only, not ERC20
}
```

### Variant 3: mint() Bypasses Check That deposit() Has (MetaPool)
```solidity
function deposit(uint256 assets, address receiver) public override {
    shares = _deposit(assets, receiver);  // includes receipt validation
}
function mint(uint256 shares, address receiver) public override {
    assets = convertToAssets(shares);
    _mint(receiver, shares);  // MISSING: _deposit() validation → mints without receiving assets
}
```

### Grep Patterns
```bash
grep -rn "function place_\|function create_\|function add_\|function open_" contracts/ -A5
grep -rn "function update_\|function modify_\|function cancel_" contracts/ -A5
grep -rn "safeApprove\b" contracts/    # safeApprove without zero-reset before
grep -rn "delete\b" contracts/ -B5 -A5  # delete before operation completes
grep -rn "function deposit\|function mint\|function withdraw\|function redeem" contracts/ -A10
```

---

## 4. OFF-BY-ONE & BOUNDARY CONDITIONS
> #4 High — 22% of Highs. Single character change. Massive impact.

### Root Cause
```solidity
// VeChain Stargate — post-exit reward drain:
function _claimableDelegationPeriods(address delegator) internal view returns (uint256) {
    if (endPeriod > nextClaimablePeriod) {  // BUG: should be >=
        return 0;  // exited users get nothing
    }
    return nextClaimablePeriod - lastClaimedPeriod;  // rewards for period AFTER exit
}
```

### Mental Test for Every Comparison
> For every `if (A > B)`: "What happens when A == B?" Is that correct?

### 6 Boundary Locations to Check
1. Period/Epoch boundaries: `>` vs `>=` at period end
2. Time-based locks: does `block.timestamp == deadline` lock or unlock?
3. Loop break conditions: `break` with `>` vs `>=`
4. Array index boundaries: `i <= array.length` (should be `i < array.length`)
5. Amount/balance boundaries: `>= amount` allows exact full withdrawal?
6. Rounding/precision: can any input produce 0 output that should be non-zero?

### Grep Patterns
```bash
# Boundaries in comparisons
grep -rn "Period\|Epoch\|Round\|Deadline\|period\|epoch\|deadline" contracts/ -A3 | grep "[<>][^=]"

# Loop breaks
grep -rn "\bbreak\b" contracts/ -B10

# Off-by-one in array access
grep -rn "\.length\s*-\s*1\|i\s*<=\s*.*\.length\b" contracts/
```

---

## 5. ORACLE / PRICE MANIPULATION
> 12% of all reports. Largest individual payouts. $117M Mango, $70M Curve.

### Bug A: Missing Staleness Check (most common)
```solidity
// VULNERABLE:
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price);  // If Chainlink node goes down, stale price returned indefinitely

// CORRECT:
(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
require(block.timestamp - updatedAt <= MAX_PRICE_AGE, "Stale price");
require(price > 0, "Invalid price");
```

### Bug B: Missing Confidence Interval (Pyth)
```solidity
// VULNERABLE:
PythStructs.Price memory p = pyth.getPriceUnsafe(priceFeed);
return p.price;  // ignores p.conf (confidence interval)

// CORRECT:
require(p.conf * 10 <= uint64(p.price), "Price too uncertain");
// conf > 10% of price = untrustworthy
```

### Bug C: TWAP Too Short (flash loan manipulatable)
```solidity
// VULNERABLE: 60-second TWAP
uint32[] memory secondsAgos = new uint32[](2);
secondsAgos[0] = 60; secondsAgos[1] = 0;
// Flash loan can shift price for entire 60s window

// CORRECT: 1800s minimum TWAP (30 min)
```

### Bug D: Single-Source Oracle
```solidity
// VULNERABLE: only Uniswap spot price
uint price = getUniswapSpotPrice(token);  // flash loan manipulatable

// CORRECT: Chainlink primary, Uniswap TWAP as fallback, require close agreement
```

### Grep Patterns
```bash
# Missing staleness check
grep -rn "latestRoundData" contracts/ -A5 | grep -v "updatedAt\|timestamp"

# Pyth price usage — confidence interval checked?
grep -rn "getPriceUnsafe\|getPrice\b" contracts/ -A8 | grep -v "conf\|confidence"

# TWAP windows — short TWAP flag
grep -rn "secondsAgo\|TWAP\|cardinality" contracts/ -A5
```

---

## 6. ERC4626 VAULT ATTACKS

### Exchange Rate Manipulation (near-empty vault)
```solidity
// VULNERABLE — first depositor attack:
// 1. Attacker deposits 1 wei → gets 1 share
// 2. Attacker donates large amount directly (transfer, not deposit)
// 3. Exchange rate: 1 share = (1 + donation) assets
// 4. Victim deposits → rounds down to 0 shares → free donation to attacker

// CORRECT: virtual shares (OpenZeppelin v4.9+)
function _decimalsOffset() internal view virtual override returns (uint8) {
    return 9;  // add 1e9 virtual shares + assets to prevent manipulation
}
```

### ERC4626 Transfer (moves shares but not stake/lock records)
```solidity
// VULNERABLE: shares transferred, but lock records stay with original owner
// → shares stuck, can't redeem → permanent freeze (Belong pattern)
function transfer(address to, uint256 amount) external override {
    _transfer(msg.sender, to, amount);  // moves shares
    // MISSING: transfer lock record from msg.sender to `to`
}
```

### Grep Patterns
```bash
grep -rn "function transfer\|function transferFrom" contracts/ -A15
grep -rn "function deposit\|function mint\|function withdraw\|function redeem" contracts/ -A10
```

---

## 7. REENTRANCY
> 2016–present. CEI pattern prevents it. Still found in DeFi.

### Variants
- **Single-function**: attacker re-enters same function before state updated
- **Cross-function**: re-enters a sibling function with stale state
- **Cross-contract**: re-enters via a callback to another protocol
- **Read-only**: re-enters a view function that returns stale data used by attacker

### Root Cause Pattern
```solidity
// VULNERABLE (effects after interaction):
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount);
    (bool success,) = msg.sender.call{value: amount}("");  // INTERACTION first
    require(success);
    balances[msg.sender] -= amount;  // EFFECT after → reentrancy window
}

// CORRECT (CEI — Checks, Effects, Interactions):
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount);  // CHECK
    balances[msg.sender] -= amount;            // EFFECT
    (bool success,) = msg.sender.call{value: amount}("");  // INTERACTION last
    require(success);
}
```

### Grep Patterns
```bash
# External calls before state updates
grep -rn "\.call{value\|safeTransfer\|transfer(" contracts/ -B10 | grep -v "require\|revert"

# Missing nonReentrant modifier on critical functions
grep -rn "function withdraw\|function redeem\|function claim" contracts/ -A2 | grep -v "nonReentrant"

# Storage slot for reentrancy guard
grep -rn "nonReentrant\|ReentrancyGuard\|_notEntered" contracts/
```

---

## 8. FLASH LOAN ATTACKS
> Flash loan is an **amplifier**, not a root bug. Bug = protocol trusts same-tx
> manipulable state (spot price, raw `balanceOf`, live votes, mid-callback views).

### Mental model
```text
borrow → distort local state → resolve against bad assumption → restore → repay (+fee)
         ↘ fail repay → full tx revert (atomic)
```
EOA cannot flash alone — needs a **receiver contract** + trusted callback checks
(`msg.sender == lender`, initiator == self).

### Core technique patterns
| Pattern | Root cause | Grep / signal |
|---------|------------|----------------|
| **Spot price punch** | `getReserves` / `slot0` / `getAmountsOut` as oracle | `getReserves\|slot0\|getAmountsOut` |
| **Donation / balanceOf accounting** | yield or shares from `token.balanceOf(this)` | `balanceOf(address(this))`, phantom yield |
| **ERC4626 inflation** | empty vault + donate → 0 shares for victim | `convertToShares`, no virtual offset |
| **Read-only reentrancy** | view mid-callback used as oracle elsewhere | pools without RO-reentrancy guard |
| **Flash governance** | vote weight = live `balanceOf`, no snapshot | governance without ERC20Votes checkpoint |
| **Liquidation capital** | often *legit*; bug if oracle also manipulable | liquidate + spot collateral price |
| **Multi-protocol compose** | Aave flash → DEX skew → lending/vault extract | profit after fee must be proven on fork |

### Oracle Manipulation via Flash Loan (classic)
```solidity
// Attack flow:
// 1. Borrow large from Aave/Balancer/Uni flash
// 2. Dump/pump in shallow AMM → crash/pump spot
// 3. Protocol reads spot → bad LTV / mint / liquidate
// 4. Extract value, swap back, repay flash + fee
```

### Price Oracle Sanity Checks (what to look for)
```bash
grep -rn "getReserves\|getAmountsOut\|slot0\b" contracts/ -A5
# spot price from reserves = manipulatable with flash loan
# slot0 = Uniswap V3 spot price = manipulatable
grep -rn "latestRoundData\|getPriceUnsafe\|observe(" contracts/ -A6
# missing updatedAt / conf / short TWAP = still flash-adjacent risk
```

### PoC bar (audit / bounty only)
- Foundry **fork** PoC with real fee math; assert attacker profit **and** protocol impact.
- Size: `maxFlashLoan` vs pool depth vs caps — unprofitable path ≠ Critical.
- Report root cause (oracle/accounting/access), not “used a flash loan”.

### Defense checklist
- Chainlink/Pyth + staleness + bounds; TWAP ≥ ~30m if on-chain; no sole spot oracle
- Internal ledger ≠ raw balances; ERC4626 virtual shares
- CEI + `nonReentrant`; no external protocols reading mid-hook views
- Caps, pause, snapshot governance

**Deep reference:** `references/flash-loan-patterns.md` (providers, callback models, matrix, workflow).

---

## 9. SIGNATURE REPLAY

### Missing Nonce
```solidity
// VULNERABLE:
function permit(address owner, address spender, uint256 value,
                uint256 deadline, uint8 v, bytes32 r, bytes32 s) external {
    bytes32 hash = keccak256(abi.encodePacked(owner, spender, value, deadline));
    // MISSING: nonce not included → same signature usable multiple times
    require(ecrecover(hash, v, r, s) == owner);
}
```

### Missing Chain ID
```solidity
// VULNERABLE: signature valid on mainnet AND testnet AND all forks
bytes32 hash = keccak256(abi.encodePacked(params));
// MISSING: block.chainid not in hash → works on any chain
```

### Grep Patterns
```bash
grep -rn "ecrecover\|ECDSA\.recover" contracts/ -B20
# Check: does the signed hash include nonce + chainId + contract address?

grep -rn "nonce\|_nonces\|nonces\[" contracts/
```

---

## 10. PROXY / UPGRADE ISSUES

### Storage Collision
```solidity
// Implementation and proxy share storage layout
// Proxy slot 0: _owner
// Implementation slot 0: _initialized
// → writing to _initialized overwrites _owner
```

### Uninitialized Implementation
```solidity
// If implementation can be initialized directly → anyone becomes owner of implementation
// Attack: call initialize() on implementation contract → call upgradeTo() → replace logic
```

### delegatecall to User-Controlled Address
```solidity
function execute(address target, bytes calldata data) external onlyOwner {
    target.delegatecall(data);  // target is validated, but what if owner is compromised?
}
```

### Grep Patterns
```bash
# UUPS initialization protection
grep -rn "function initialize\b\|_disableInitializers\|initializer" contracts/

# Delegate call
grep -rn "delegatecall\b" contracts/ -B3 -A5

# Storage layout — proxy uses EIP-1967 slots?
grep -rn "0x360894\|EIP1967\|_IMPLEMENTATION_SLOT" contracts/
```

---

## 11. BYTECODE-ONLY AUDIT METHODOLOGY

> When the contract is verified on Etherscan but Cloudflare blocks access, or the contract is unverified. Methodology proven on LO0P LendingHookV2 bug bounty (Ethereum mainnet, Uniswap V4 hook, Solidity 0.8.26).

### 11.1 Chain Identification

Probe multiple chains — same address, different deployments:
- RPCs: `https://ethereum-rpc.publicnode.com`, BSC, Base, Arbitrum, Polygon
- `eth_getCode` returns `"0x608060..."` = contract exists, `"0x"` = no contract

### 11.2 Function Selector Extraction

From bytecode hex, extract all PUSH4 (`0x63`) operands — these are function selectors:
- `hex_code = code[2:]` (strip `0x`)
- `re.findall(r'63([0-9a-f]{8})', hex_code)` — deduplicate with `set()`
- Hash collisions (known) and false positives (PUSH4 in data segments) are rare for real contracts

### 11.3 Selector → Signature Lookup

Query 4byte.directory for each selector:
```bash
curl -s "https://www.4byte.directory/api/v1/signatures/?hex_signature=0xXXXXXX"
```
Results show known function signatures. ERC20 standards (`0x095ea7b3`, etc.) are easily identified.

### 11.4 Solidity Compiler Metadata from Bytecode Tail

Bytecode ends with CBOR-encoded compiler metadata:
- Marker: `a2646970667358` + length byte + IPFS multihash + `64736f6c6343` ("solc")
- Convert multihash to CIDv0:
  ```python
  import base58
  cid = base58.b58encode(bytes.fromhex("1220" + 32_bytes_hash)).decode()
  ```
- Fetch metadata: `https://gateway.pinata.cloud/ipfs/{cid}`
- Contains full source code (inline) or keccak references

### 11.5 Decompilation via Dedaub

When source code is inaccessible (Cloudflare, unverified):
1. Navigate to `https://app.dedaub.com/decompile?address=0xTARGET&chain=1`
2. Use Camofox stealth browser when Cloudflare blocks — Camofox bypasses bot detection at C++/Firefox level
3. Dedaub reveals: contract name, compiler version, decompiled source, function list (Read/Write/Payable), events, storage layout
4. "Source" tab shows full decompiled code with original SPDX license, pragma, imports preserved
5. **Warning**: Decompiled code is pseudocode — use for analysis only, not as submission-quality source reference

### 11.6 On-Chain State Querying

Build calldata from known selectors:
- **address param**: left-pad to 32 bytes (64 hex chars)
- **uint256 param**: encode as 64 hex chars (no leading zeros stripped)
- Compute unknown selectors:
  ```python
  from eth_hash.auto import keccak
  selector = '0x' + keccak("func(type1,type2)".encode()).hex()[:8]
  ```
- For struct-param functions (Uniswap V4 hooks), the ABI uses tuple encoding: `func((type1,type2,...))`

### 11.7 Foundry Fork Testing Without Source

```solidity
// Minimal interface — declare only functions you need
interface IHook {
    function LTV_BPS() external view returns (uint256);
}

IHook hook = IHook(TARGET_ADDR);
emit log_named_uint("LTV_BPS", hook.LTV_BPS());
```

Key cheatcodes:
- `vm.createSelectFork(rpcUrl, blockNumber)` — fork at exact block for reproducibility
- `emit log_named_uint()` / `emit log_named_address()` — structured output (avoids forge-std console2 mixed-type compilation issues with newer versions)
- `vm.label(addr, name)` — readable traces

### 11.8 Counter-Indications

- Use verified source when accessible — bytecode analysis is 10x slower
- Proxy contracts (ERC-1167 minimal proxy) have tiny bytecode — find implementation address
- Bytecode > 50KB may cause decompiler failures

### 11.9 EIP-1967 Proxy → Implementation Slot (exact constant pitfall)

When a proxy's implementation slot is empty for the canonical constant, the proxy may use
a **non-canonical EIP-1967 slot constant**. Read the EXACT PUSH32 that follows SLOAD in the
proxy disassembly — do not assume the standard `0x360894...3e607f`.

```bash
cast code 0xPROXY --rpc-url $RPC | cast disassemble -
# Find: PUSH32 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc
#        SLOAD
# Opal used 0x360894...3e2076cc3735a920a3ca505d382bbc (differs from canonical ...3e607f)
cast storage 0xPROXY 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $RPC
# -> 0x...IMPL_ADDRESS
```

Also probe EIP-1967 admin slot (`0xb5312768...5d6103`) — if empty, the proxy is immutable
(no upgrade hijack path). Probe `owner()`, `enclaveAddress()`, `paused()` to map access control.

---

## 12. UNISWAP V4 HOOK SECURITY

> V4 hooks are callback-based: PoolManager calls hook functions during pool operations. This creates unique reentrancy and state manipulation risks.

### 12.1 Callback Architecture

| Callback | Trigger | Risk |
|----------|---------|------|
| `beforeSwap` / `afterSwap` | Every swap | State stale during callback |
| `beforeAddLiquidity` / `afterAddLiquidity` | LP added | Balance tracking |
| `beforeRemoveLiquidity` / `afterRemoveLiquidity` | LP removed | Balance tracking |
| `beforeInitialize` / `afterInitialize` | Pool creation | Initial state race |
| `beforeDonate` / `afterDonate` | Donation | n/a |
| `unlockCallback` | `lock()` operation | Arbitrary execution context |

### 12.2 Vulnerability Patterns

**A: Callback Reentrancy** — During a swap, `beforeSwap` → PoolManager executes → `afterSwap`. If `borrow()`/`liquidate()` are callable during this window and share state with the callback, cross-function reentrancy is possible.

Checklist:
- [ ] ReentrancyGuard on ALL state-changing functions?
- [ ] Can `lock()` → `unlockCallback()` trigger lending functions with stale state?
- [ ] Do any callbacks modify state that borrow/repay/liquidate depend on?

**B: Same-Block Lockout Bypass** — Protocols track `lastSwapBlock` to prevent borrow in same block as swap. Only blocks same-block. Cross-block attack: swap in block N, borrow in block N+1. Check if `lock()` → `unlockCallback()` also updates `lastSwapBlock` — if not, flash swaps bypass the lockout.

**C: Hook Permissions Mismatch** — `getHookPermissions()` returns bit flags for active callbacks. If a callback is implemented but the permission flag is missing (or vice versa), V4 may skip the callback or revert on unexpected call.

**D: Spot Price Oracle** — Lending hooks using `currentSqrtPriceX96()` for collateral valuation expose the protocol to flash-loan price manipulation. Same-block lockout helps but cross-block is still open.

### 12.3 Lending Hook Audit Checklist

```text
[ ] ReentrancyGuard on all state-changing functions?
[ ] borrow/liquidate callable during swap callbacks?
[ ] lastSwapBlock updated in ALL callbacks (before+after)?
[ ] lock()/unlockCallback() also updates lastSwapBlock?
[ ] poolKey validated where it's depended on?
[ ] Hook permissions match implemented callbacks?
[ ] Spot price used as oracle? TWAP/Chainlink fallback?
[ ] LTV/liq/hardcoded parameters immutable (no proxy)?
[ ] Liquidation bounty cap prevents large-position liquidations?
[ ] FeeCollector — can fees be drained/redirected?
[ ] owner() can renounce ownership — what becomes unreachable?
```

---

## 13. RUST / SOLANA / ANCHOR AUDIT PATTERNS

> For Rust/Anchor programs on Solana. The 10 EVM classes above still apply at the logic level; this section adds Solana-specific leakages.

### Node-type confusion (the #627 pattern)
**Root cause:** a peer's `node_type` field is self-declared over gossip. When a `ResourceProvider` (compute-only) peer is auto-registered as a transact/settlement validator, it gains a vote in the off-chain consensus quorum.

**Audit checklist:**
```text
□ Is every `register_validator` call gated on a check that the peer is meant to settle?
□ Does the 30-second connectivity reconciler register ALL connected peers, or only specific node types?
□ Is there a fallback node_type that silently enables settlement on a compute-only node?
□ Can a witness-only validator that never generates a wallet keypair be registered (wallet_pubkey = None)?
```

**Grep targets:**
```bash
grep -rn "ResourceProvider" src/ programs/ | grep -v test
grep -rn "register_validator" src/
grep -rn "wallet_pubkey" src/ | grep "None\|null"
```

### Unbounded in-memory buffers (delivered_notes pattern)
**Root cause:** `Arc<Mutex<Vec<T>>>` with no cap. Every settlement appends entries; a long-running node OOMs.

**Grep targets:**
```bash
grep -rn "Arc<Mutex<Vec<" src/ --include="*.rs" | grep -v "test\|cfg(test)"
grep -rn "delivered_notes\|DeliveredNote" src/
```

### Cosign/reputation maps never pruned (cosign_counts pattern)
**Root cause:** a per-settlement HashMap that insert()s but never removes entries after timeout/completion. Grows linearly with request volume.

**Grep targets:**
```bash
grep -rn "HashMap<String" src/ --include="*.rs" | grep -v "test\|cfg(test)"
# Check each for a partner remove() or eviction path
```

### PDA seed derivation mismatch
**Root cause:** an on-chain PDA is derived from one set of seeds but a validation check uses a different set (or no check at all).

**Audit checklist:**
```text
□ `find_program_address` seeds match the validator's recorded fields?
□ Can a non-canonical PDA verify as canonical (e.g. a wrong wallet seeded)?
□ Are `remaining_accounts` pairs checked for: owner == program_id, seeds == canonical, is_active?
```

### Fee calculation / scope edge cases (i64::MIN, overflow-checks)
**Root cause:** `ext_amount.unsigned_abs()` panics on `i64::MIN`; unchecked `as` casts truncate u128→u64.

**Grep targets:**
```bash
grep -rn "unsigned_abs\|as u64\|as u32\|as usize\|from_le_bytes_mod_order" programs/ --include="*.rs"
# Check if overflow-checks = true in release profiles
grep -rn "overflow-checks" Cargo.toml programs/*/Cargo.toml
```

### Key file permissions
**Root cause:** wallet key file written at process umask (0644) instead of 0600.

**Grep target:**
```bash
grep -rn "save_keypair_to_file\|write.*key\|0600\|0700" src/ --include="*.rs"
```

### Deep reference
See `references/paraloom-audit.md` for a worked example of all the above patterns in one codebase.

---

## 14. BFT CONSENSUS / LIVENESS / SAFETY AUDIT (Solana Alpenglow pattern)

> For BFT consensus stacks like Solana Alpenglow (votor/bls-sigverify/RepairService).
> The DeFi bug classes above still apply at the logic level; this section adds
> consensus-specific attack surfaces and the adversarial reasoning protocol for
> distinguishing real safety violations from by-design behavior.

### 14.1 Competition Rules Gate (read BEFORE auditing)

1. Download `RULES.md` or equivalent from the competition repo. Extract:
   - Submission window dates (UTC).
   - In-scope crate/file list and feature flags that must be active.
   - Severity categories (Consensus/Safety, Liveness, DoS, Other) and prize tiers.
   - Known-issues tracker labels (`blocking-ag`, `consensus-team`).
   - PoC requirement: local fork / multi-node harness, never mainnet.
2. Pull the known-issues baseline:
   ```bash
   curl -sS "https://api.github.com/repos/{org}/{repo}/issues?labels={label1},{label2}&state=all&per_page=100" \
     -H "Accept: application/vnd.github+json" > known-issues.json
   ```
3. Record the commit hash under audit: `git rev-parse HEAD`. Rules may require
   continuous `master` HEAD (moving window) — cite the exact commit in any report.
4. A finding is valid only if the bug is **still live on `master`** at submission.
   Fixes landed mid-window are themselves in-scope but once fixed, the issue is ineligible.

### 14.2 Hypothesis Triage Framework

For each consensus hypothesis, run this rejection pass *before* investing in a PoC:

1. **Fault threshold reachability:** Does the attack require >20% Byzantine stake
   (or whatever the protocol's fault bound is)? If yes → KILLED. The panic/assert
   is a safety fence, not a vulnerability.
2. **Mathematical unreachability:** Can the network legitimately produce N
   conflicting certificates under honest majority? Calculate the combinatorial
   minimum stake overlap. Example: 5 NotarizeFallback certs require ≥50%
   Byzantine overlap → KILLED if fault bound is 20%.
3. **By-design behavior:** Is the "anomaly" actually the intended protocol behavior?
   Example: `FinalizeFast` reusing `Notarize` payload + 80% threshold is by design.
4. **Local-only impact:** Does the bug only affect the node that experiences it
   (self-inflicted)? If no cluster-wide safety/liveness break → Low/Informational.
5. **Upstream mitigation:** Is the unchecked path guarded by an upstream layer?
   Example: `AggregateAccumulator::add_aggregate` doesn't dedup, but gossip
   layer + `debug_assert` prevent duplicates from reaching it.
6. **Certificate/cert verification gating:** Does the receiver verify a BLS cert
   before acting on the data? If the `ParentReady` event only fires after cert
   validation, an unauthenticated `UpdateParent` marker from a malicious leader
   cannot trick honest validators into voting on un-notarized parents.

### 14.3 Consensus-Specific Attack Surfaces

| Surface | What to look for | Grep targets |
|---------|-----------------|--------------|
| **Stake threshold bypass** | `Fraction` comparison off-by-one, `saturating_add` inflation, `checked_mul` panic path | `Fraction::new`, `threshold()`, `saturating_add`, `checked_mul` |
| **Certificate forgery/replay** | Cross-chain replay, shred_version not in payload, missing domain separation | `shred_version`, `get_vote_payload_to_sign`, `wincode(tag` |
| **BLS aggregate manipulation** | Duplicate rank in aggregate, stake double-count, rogue key | `add_aggregate`, `bitwise OR`, `aggregate_with` |
| **Vote history / persistence race** | Vote recorded before send, transient error swallows vote, restart loses vote intent | `add_vote(`, `handle_skippable_vote_error`, `TransientError` |
| **Migration / genesis handover** | `unreachable!` panic pre-activation, cert mismatch, fork threshold | `set_genesis_certificate`, `ReadyToEnable`, `AG_MIGRATION_EPOCH` |
| **Fast leader handover** | `UpdateParentV1` marker points to un-notarized slot, abandoned bank without cert check | `UpdateParentV1`, `handle_abandoned_bank`, `has_update_parent` |
| **Channel deadlock / lockstep** | Bounded channel blocking-send between pool and event handler | `blocking_send`, `bounded(`, `nonblocking_send` |
| **ParentReady / rooting integration** | Root set on non-finalized block, bank hash mismatch panic | `check_rootable_blocks`, `set_root`, `block_id` |

### 14.4 Build Environment Setup (Rust / Agave)

```bash
# Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env

# Agave-specific: clang-sys / libclang dependency
sudo apt-get install -y clang llvm libclang-dev
export LIBCLANG_PATH=/usr/lib/llvm-21/lib  # adjust version

# Pin to competition toolchain
cat rust-toolchain.toml  # e.g. channel = "1.97.1"

# Compile + test core crates
cargo check -p agave-votor -p agave-votor-messages -p agave-bls-cert-verify
cargo test -p agave-bls-cert-verify  # fast, ~10s
cargo test -p agave-votor -p agave-votor-messages  # slow, 5-10 min
```

If `cargo check` or `cargo test` hangs >10 min, run in background with
`notify_on_complete=true`. Do NOT block the audit pipeline on compilation.

### 14.5 Parallel Subagent Delegation Strategy

Delegate source review to 3 parallel leaf subagents, each covering one layer:

| Subagent | Area | Files |
|----------|------|-------|
| 1 | Consensus core (votor) | `votor/src/**/*.rs` — consensus_pool, vote_pool, parent_ready_tracker, slot_stake_counters, vote_history, voting_utils, event_handler |
| 2 | Messages & crypto | `votor-messages/src/**/*.rs` — certificate, vote, wire, fraction, migration, reward_certificate + `bls-sigverify/src/**/*.rs` + `bls-cert-verify/src/**/*.rs` |
| 3 | Runtime & integration | `runtime/src/validated_reward_certificate.rs`, `validated_block_finalization.rs`, `epoch_stakes.rs`, `block_component_processor/`, `core/src/cluster_info_vote_listener.rs`, `core/src/replay_stage/`, `core/src/block_creation_loop/`, `ledger/src/blockstore_processor.rs` |

Each subagent must return:
- Exact `file:line` for each hypothesis.
- Attacker prerequisites (stake %, leader role, network position).
- Impact category (Safety / Liveness / DoS / Other).
- Adversarial rejection pass (why it might be by-design or unreachable).
- Cross-reference against known-issues JSON.

### 14.6 Deep reference
See [references/solana-alpenglow-bft-audit-2026-08.md](references/solana-alpenglow-bft-audit-2026-08.md) for a worked example of all the above patterns in the Alpenglow codebase.

---

## FOUNDRY POC TEMPLATE

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/VulnerableContract.sol";

contract ExploitTest is Test {
    VulnerableContract target;
    address attacker = makeAddr("attacker");
    address victim = makeAddr("victim");

    function setUp() public {
        // Fork mainnet at specific block
        vm.createSelectFork("mainnet", BLOCK_NUMBER);

        // Deploy or load target
        target = VulnerableContract(TARGET_ADDRESS);

        // Fund accounts
        deal(address(token), attacker, INITIAL_BALANCE);
        deal(address(token), victim, VICTIM_BALANCE);
    }

    function test_exploit() public {
        console.log("Attacker balance before:", token.balanceOf(attacker));

        vm.startPrank(attacker);

        // Step 1: Setup conditions
        // Step 2: Execute exploit
        // Step 3: Verify impact

        vm.stopPrank();

        console.log("Attacker balance after:", token.balanceOf(attacker));
        assertGt(token.balanceOf(attacker), INITIAL_BALANCE, "Exploit failed");
    }
}
```

### Key Foundry Cheatcodes
```solidity
vm.prank(address)           // next call from address
vm.startPrank(address)      // all calls from address until stopPrank()
vm.deal(address, amount)    // set ETH balance
deal(token, address, amount) // set ERC20 balance
vm.warp(timestamp)          // set block.timestamp
vm.roll(blockNumber)        // set block.number
vm.createSelectFork("mainnet", blockNumber)  // fork mainnet
vm.expectRevert(bytes)      // next call should revert
vm.label(address, "name")   // label for trace output
vm.assume(condition)        // fuzz: discard inputs where false
```

### Running Tests
```bash
# Run specific test
forge test --match-test test_exploit -vvvv

# Run with fork
forge test --match-test test_exploit -vvvv --fork-url $MAINNET_RPC

# Gas report
forge test --gas-report

# Coverage
forge coverage --report summary
```
