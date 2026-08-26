# Flash Loan Patterns & Audit Techniques

Class-level notes for smart-contract hunting. Flash loan = uncollateralized **same-transaction** liquidity rental. Not a vulnerability by itself.

## Atomic flow

```text
1. Tx starts
2. Lender sends tokens to borrower contract
3. Lender calls borrower callback
4. Borrower acts (swap, liquidate, manipulate, compose protocols)
5. Borrower repays principal + fee (pull approve or push transfer)
6. Commit — or full revert if repay fails
```

## Providers (callback models)

| Provider | Fee (typical) | Callback | Repay style |
|----------|---------------|----------|-------------|
| Aave V2/V3 | ~0.05–0.09% | `executeOperation` | Pull via approve |
| Uniswap V2 | 0.3% path | `uniswapV2Call` | Push to pair |
| Uniswap V3 | pool fee tier | `uniswapV3FlashCallback` | Push to pool |
| Balancer Vault | often 0 | `receiveFlashLoan` | Push to vault |
| dYdX solo | legacy ~0 | `callFunction` | model-specific |

Low/zero fee → lower profit threshold for attacks.

## Borrower skeleton (audit/education)

```solidity
// Conceptual — always require lender + self-initiator
function executeOperation(...) external returns (bool) {
    require(msg.sender == address(LENDER), "only lender");
    require(initiator == address(this), "only self");
    // act...
    // repay principal + premium exactly
    return true;
}
```

Missing callback auth → griefing / forced callback abuse on the receiver.

## Technique catalog

### T1 — Spot price punch
Borrow → large swap on shallow pool → target reads reserves/slot0 → mint/borrow/liquidate on fake price → reverse swap → repay.

**Signals:** `getReserves`, `slot0`, `getAmountsOut`, LP token as collateral price.

### T2 — Donation / balanceOf accounting
Borrow → `transfer` into vault/pair (not deposit) → protocol treats excess balance as yield or share assets → claim/redeem → repay.

Cousin of ERC4626 first-depositor inflation.

### T3 — Read-only reentrancy + size
Enter pool op with external callback window → other protocol reads stale view (virtual price, reserves) → flash-sized action → finish.

### T4 — Governance without snapshot
Borrow gov token → vote/pass in same block → repay. Dead if ERC20Votes checkpoints / snapshot block used.

### T5 — Liquidation engine
Borrow debt asset → liquidate → sell collateral → repay. Often legitimate keeper path; Critical only if combined with manipulable oracle or broken incentive math.

### T6 — Multi-protocol composition
Aave flash → Uni manip → lending/vault extract → repay. Root cause is cross-system assumption, not the loan.

## When flash path works vs dies

**Works if target trusts:** same-block spot price, raw `balanceOf(self)`, empty-vault share math, live voting balances, mid-callback views, missing caps/slippage.

**Dies if:** independent oracle + heartbeat + bounds, long TWAP, virtual shares, internal ledger, snapshot votes, borrow/supply caps, fee+impact > extractable value.

## Audit workflow

1. Map price reads and accounting sources.
2. Ask: changeable in one tx with rented capital?
3. Compare `maxFlashLoan` / pool depth / protocol TVL / caps.
4. Foundry fork PoC: repay exact fee; profit > 0; funds-at-risk realistic.
5. Report **root cause class** (oracle, accounting, access, RO-reentrancy) — not “flash loan attack” as the bug name.

## Grep pack

```bash
rg -n "getReserves|slot0\\b|getAmountsOut|observe\\(" contracts/
rg -n "balanceOf\\(address\\(this\\)\\)|totalAssets\\(|convertToShares" contracts/
rg -n "latestRoundData|getPriceUnsafe|updatedAt|HEARTBEAT" contracts/
rg -n "flashLoan|executeOperation|uniswapV2Call|receiveFlashLoan" contracts/
rg -n "nonReentrant|get_virtual_price|getRate" contracts/
```

## Defense shortlist

- Oracle: Chainlink/Pyth + `updatedAt` + `price > 0` + deviation bounds; avoid sole spot.
- Vaults: virtual shares / dead shares; never donate-affects-share-price without offset.
- Accounting: tracked supply/debt ledger, not raw balances alone.
- Hooks: CEI + reentrancy guard; don’t publish oracle views mid-callback.
- Governance: checkpoints/snapshots, not live balance.
- Risk: caps, pause, circuit breakers.

## Severity hygiene

- Flash loan use alone ≠ Critical.
- Unprofitable after fee/depth/caps → lower or invalid.
- Likelihood drops if multi-block TWAP required without private sequencing assumptions — state that explicitly.
- Bounty writeups: path + PoC + funds-at-risk math; name the broken invariant.

## Related session tooling

- Personal residual recovery (not flash): `wallets` skill + `~/tools/sweep` — separate class from flash-loan abuse.
