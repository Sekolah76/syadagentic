# Retroactive Reward Smearing in Epoch-Based Distribution

This vulnerability occurs when a protocol uses a "Point-in-Time" guard to protect an "Interval-Based" accounting logic. It is common in rewards-distribution contracts (FeeDistributors) that track "last reward time" and distribute balance deltas retroactively across elapsed time.

## The Pattern

1. **The Guard:** A function (like `deposit`) checks if the current `totalSupply > 0` to prevent funding a dead contract.
2. **The Logic:** The contract calculates the time elapsed since the last checkpoint and distributes tokens proportionally across that time (often snapped to weekly epochs).
3. **The Flaw:** If the last checkpoint was long ago, the distribution interval may include past epochs where `totalSupply` was 0.
4. **The Result:** Rewards are "smeared" into zero-supply epochs and permanently trapped/burned, even if the current epoch is fully staked.

## Stake DAO Example (vlSDT Galaxy)

In `FeeDistributor.sol`:
```solidity
function deposit(uint256 amount) external {
    require(VLSDT.totalSupply() > 0, NoStakers()); // Passes if supply is 100 NOW
    _checkpointToken(); // Calculates time since lastTokenTime (e.g., 2 weeks ago)
}
```

If Week 1 had 0 supply and Week 2 has 100 supply:
1. Caller calls `deposit` in Week 2.
2. `require` passes.
3. `_checkpointToken` sees 2 weeks elapsed.
4. It allocates 50% to Week 1 (empty) and 50% to Week 2.
5. 50% is permanently trapped.

## Foundry Verification Pattern

Use `vm.mockCall` to simulate historical epoch states without complex staking setups:

```solidity
function test_Reward_Smear() public {
    // 1. Setup initial empty state
    vm.warp(distributor.START_TIME());
    
    // 2. Advance to Week 2 and simulate supply
    vm.warp(block.timestamp + 1 weeks);
    vm.mockCall(address(vlsdt), abi.encodeWithSelector(vlsdt.totalSupply.selector), abi.encode(100 ether));
    
    // 3. Deposit (Guard passes)
    distributor.deposit(1000 ether);
    
    // 4. Verify Week 1 (empty) trapped the smear
    uint256 trapped = distributor.getTokensForEpoch(startTs);
    assertGt(trapped, 0);
}
```

## Remediation

The checkpoint loop must verify supply for **each epoch bucket** before allocating:

```solidity
for (uint256 i; i < MAX_CHECKPOINT_EPOCHS; i++) {
    uint256 epochSupply = VLSDT.totalSupplyAt(thisEpoch);
    if (epochSupply > 0) {
        tokensPerEpoch[thisEpoch] += epochShare;
        distributed += epochShare;
    } else {
        // Option A: Skip and let tokens remain in 'toDistribute'
        time = nextEpoch; 
    }
}
```
