# Case Study: Initializer Frontrunning on Onyx Chain (StakedXCNDirect)

This document preserves the exact reproduction case, threat model analysis, and mitigation strategy for the initializer frontrunning vulnerability discovered in the `StakedXCNDirect` contract during the Onyx Protocol audit.

---

## The Vulnerability

In `StakedXCNDirect.sol`:
```solidity
/// @title StakedXCNDirect - Non-proxy deployment for Goliath Mainnet
/// @notice Identical to StakedXCN but uses a direct `init()` function with explicit owner parameter.
///         This is needed because Goliath mainnet's relay sets msg.sender=address(0) in ContractCreate.
/// @dev Deploy this contract, then call `init(owner, rewardRateRay, treasury, feeBps)` in a separate tx.
constructor() {} // constructor leaves state uninitialized

function init(
    address owner_,
    uint256 rewardRateRay,
    address treasury,
    uint256 feeBps
) external initializer {
    // anyone can call this if they frontrun the deployer!
```

---

## Why Constructor Initialization Failed
On the custom Goliath L2 chain, deploying a contract with `ContractCreate` executes in a context where `msg.sender` is evaluated as `address(0)`. Therefore, using the standard OpenZeppelin pattern of assigning `owner = msg.sender` inside the constructor sets `owner` to the zero address, immediately bricking the contract.

To circumvent this, the developers moved initialization to a public `init(...)` function to be called in a separate transaction immediately following deployment.

---

## The Threat Model
Because `init()` is public, lacks caller restrictions, and the `initializer` modifier locks the contract after a single call, it is vulnerable to MEV/mempool frontrunning:
1. Attacker monitors L2 mempool for the deployment transaction.
2. Attacker waits for the subsequent `init()` call from the deployer.
3. Attacker broadcasts their own `init(attacker, ...)` call with a higher gas price (or via private RPC channels).
4. Attacker becomes the owner of the token contract, gets the fees, and can pause/unpause staking at will.

---

## The Mitigation

### Option 1: Capture Deployer in Constructor (Immutable variable)
Even if `msg.sender` is `address(0)`, the transaction origin (`tx.origin`) or a constructor argument representing the deployer can be stored as an `immutable` state variable. Since immutable variables are written directly into the bytecode, they do not require proxy storage slots.

```solidity
address private immutable _deployer;

constructor(address deployer_) {
    _deployer = deployer_; // or tx.origin if constructor args are restricted
}

function init(...) external initializer {
    require(msg.sender == _deployer, "StakedXCNDirect: only deployer can initialize");
    ...
}
```

### Option 2: Atomic Deployment & Initialization via Factory
Deploy the contract using a factory contract that performs the `new StakedXCNDirect()` deployment and immediately calls `.init(...)` in the same transaction execution frame. This makes the deployment and initialization atomic, preventing any mempool frontrunning.
