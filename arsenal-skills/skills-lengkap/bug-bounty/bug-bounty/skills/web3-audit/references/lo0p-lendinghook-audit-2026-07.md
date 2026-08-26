# LO0P LendingHookV2 Audit Reference — 2026-07-25

## Target
- **LendingHookV2**: `0xB0cc755B03aBf0b981Dd57A0FB12b8a54E08facc` (Ethereum)
- **LO0P Token**: `0x00000000000050806673B532D7486ac114c1De3F`
- **PoolManager**: `0x000000000004444c5dc75cB358380D2e3dE08A90`
- **FeeCollector**: `0x6beAc0dd77044A9B6D290efC8Fb95D1fd670a415`
- **Deployer**: `0xec697fedf608bf4b9f81d490a645246c5c20e908`
- **Compiler**: Solidity v0.8.26, deployed block 25076250 (2026-05-11)
- **IPFS CID**: `QmX5Nse67xCaGWhsKy7bpPFgCW8ApSi7iwSxeEptyZnuzC` (metadata not widely pinned)

## Protocol
- Uniswap V4 hook lending AMM (lo0p.io)
- Buy LOOP on bonding curve → lock as collateral → borrow ETH from LP bands
- 100 LDF bands × 30 ETH = 3,000 ETH capacity
- 40% LTV, 150% liq threshold, 1% orig fee, 1% liq bounty (max 0.01 ETH)
- 2-block repay cooldown, min 0.1 ETH collateral
- Immutable — no proxies, no upgrade paths, no governance

## Bugsy Program
- DM on X (@lo0pio) — no platform
- Up to $10,000 critical

## Key Selectors
```
0x023f3a55 = LIQUIDATION_BOUNTY_BPS()
0x0c6d5a58 = LIQUIDATION_THRESHOLD_BPS()
0xfae3706f = LTV_BPS()
0x59309d9f = MAX_LIQUIDATION_BOUNTY()
0xfb7949b6 = MIN_COLLATERAL_VALUE()
0x670587fa = NUM_INITIAL_BANDS()
0xc35293cc = ORIG_FEE_BPS()
0x30d682b0 = REPAY_COOLDOWN_BLOCKS()
0xa92100cb = loop()
0xc5ebeaec = borrow(uint256)
0x371fd8e6 = repay(uint256)
0xbcbaf487 = liquidate(address,uint256)
0xbe9a6555 = start()
0x0b0d9c09 = take(address,address,uint256)
0xc1be6677 = positions(address,uint256)
0x480e1949 = getBand(uint256)
0x91dd7346 = unlockCallback(bytes)
```

## Findings
1. Cross-Block Oracle Manipulation (Med)
2. Liquidation Incentive Gap (Med)
3. V4 Hook Callback Reentrancy Surface (Med-High)
4. Spot Price Oracle Dependency (Med)
5. Band Calculation Edge Cases (Low-Med)

## PoC
- `~/lo0p-audit/test/Lo0pAudit.t.sol` — 6 tests passing on fork
- Run: `forge test --fork-url https://ethereum-rpc.publicnode.com --fork-block-number 25609000 -vvv`
