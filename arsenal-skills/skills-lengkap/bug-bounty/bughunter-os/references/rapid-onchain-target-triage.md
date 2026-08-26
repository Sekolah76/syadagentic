# Rapid On-Chain Target Triage

Reusable workflow for taking a contract address (from DexScreener, Twitter, Telegram, etc.) and rapidly determining whether it's exploitable — all via RPC, no BscScan/Etherscan dependency.

## When to Use

- User drops a DexScreener link or contract address and says "drain this"
- Need to quickly assess TVL, activity, contract type, and exploit potential
- BscScan/Etherscan is Cloudflare-blocked and Camoufox unavailable

## Pipeline

### Step 0: Accept the address

Accept whatever form the user gives (raw address, DexScreener URL, Etherscan URL). If it's a URL, extract the address from the path:

```
https://dexscreener.com/bsc/0x...  → path last segment
https://bscscan.com/address/0x...  → path second-to-last segment
```

Always call `w3.to_checksum_address()` — some users paste non-checksum addresses.

### Step 1: BSC RPC Setup (BSC only)

BSC uses POA consensus; web3.py needs the extra-data middleware:

```python
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.binance.org"))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
```

Fallback RPCs if primary is rate-limited or down:
- `bsc-dataseed2.binance.org`
- `bsc-dataseed3.binance.org`
- `bsc-dataseed4.binance.org`
- `rpc.ankr.com/bsc` (requires API key)

### Step 2: Basic Contract Check

```python
code = w3.eth.get_code(checksum_addr)
balance = w3.eth.get_balance(checksum_addr)
tx_count = w3.eth.get_transaction_count(checksum_addr)
```

**Dead pool detection**: `tx_count == 1` means the pool was created, initial LP minted, and NEVER used again. No swaps = no active liquidity = almost certainly not exploitable via pool logic.

**Code size heuristic**:
- 0 bytes: EOA (externally owned account), not a contract
- < 500 bytes: minimal proxy (EIP-1167) or stub
- 2k-8k: standard ERC20
- 10k-14k: UniswapV2 pair
- 15k+: complex protocol (router, vault, bridge)

### Step 3: Contract Type Identification (no ABI)

Scan bytecode for known function selectors to identify the contract type:

```python
selectors = {
    "0x0902f1ac": "getReserves()",           # UniswapV2 pair
    "0x0dfe1681": "token0()",                # UniswapV2 pair
    "0xd21220a7": "token1()",                # UniswapV2 pair
    "0x38ed1154": "swap(uint256,uint256,address,bytes)",  # UniswapV2 pair
    "0x022c0d9f": "swapExactTokensForTokens",  # Router
    "0x7ff36ab5": "swapExactETHForTokens",    # Router
    "0x40c10f19": "mint(address,uint256)",    # ERC20 with mint
    "0x42966c68": "burn(uint256)",            # ERC20 burnable
    "0x8da5cb5b": "owner()",                 # Ownable
    "0xf2fde38b": "transferOwnership(address)",  # Ownable
    "0x715018a6": "renounceOwnership()",      # Ownable
    "0x3659cfe6": "upgradeTo(address)",       # UUPS proxy
    "0x4f1ef286": "upgradeToAndCall(address,bytes)",  # UUPS proxy
}
```

Count ERC20 selectors found: name(), symbol(), decimals(), totalSupply(), balanceOf(), transfer(), transferFrom(), approve() — if ≥ 5 present, it's a token.

### Step 4: UniswapV2 Pair Analysis

If `getReserves()`, `token0()`, `token1()`, and `factory()` selectors are present, use the minimal pair ABI to read:

| Call | What it tells you |
|---|---|
| `token0()` | First token address → identify via balanceOf |
| `token1()` | Second token address → identify via balanceOf |
| `getReserves()` | reserve0, reserve1 (uint112 each) |
| `factory()` | Factory that created this pair |
| `totalSupply()` | Total LP tokens minted |

**Storage-based fallback** (if ABI calls fail): In UniswapV2 pairs, token0 is usually at storage slot 0 (packed with reserve data) and token1 at slot 1 or later. Read raw storage and extract address from last 20 bytes.

### Step 5: Token Identification

For each token address returned:

```python
# Read symbol, name, decimals via raw eth_call
symbol = w3.eth.call({'to': token_addr, 'data': '0x95d89b41'})
name   = w3.eth.call({'to': token_addr, 'data': '0x06fdde03'})
```

Decode the ABI-encoded string responses:
- First 32 bytes = offset to data
- Next 32 bytes = string length
- Remaining bytes = UTF-8 string

### Step 6: Economic State

| Metric | How | Signal |
|---|---|---|
| TVL | reserve0 + reserve1 at market price (reserve0 for USDT pairs) | TVL ≈ reserve0 × 2 if USDT-denominated |
| Token price | reserve0 / reserve1 (adjusted for decimals) | Compare to CEX/DEX price |
| Activity | TX count + recent Transfer events | 0 recent events = dead pool |
| LP distribution | Check if LP is held by single address vs distributed | Single holder = rug risk |
| Owner balance | Check `owner()` → check their token balance | 0 = dev dumped; high = dev controls |
| Token distribution | Check dead address, burn events | High % burned = deflationary |

### Step 7: Exploit Surface Scan

**For standard UniswapV2 pairs** (no custom logic):

| Check | Method | Verdict if exploitable |
|---|---|---|
| Skim | Compare `balanceOf(token0/1, pair)` vs `getReserves()` | Diff > 0 → skim excess |
| Sync | Same as above | Off by one → sync then swap |
| Reentrancy | Standard pair uses CEI → not vulnerable | Standard pair: clean |
| Flash loan | Pool has no custom flash loan function | Standard pair: no |
| Mint-burn custom | Check bytecode for custom mint/burn selectors | If absent → no desync |

**For tokens** (NMX, custom ERC20):

| Function | Risk |
|---|---|
| `mint(address,uint256)` | Owner can inflate supply at will |
| `burn(uint256)` / `burnFrom(address,uint256)` | May deflate supply |
| `blacklist(address)` | Can freeze holder funds |
| `pause()` | Can halt all transfers |
| `excludeFromFee(address)` | Can manipulate transfer fees |
| `upgradeTo(address)` | Can change implementation = total control |

**For owner contracts / proxy detection**:

```python
EIP1967_LOGIC_SLOT = 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc
impl = w3.eth.get_storage_at(addr, EIP1967_LOGIC_SLOT)
# Count delegatecall opcodes (0xf4) in bytecode
delegatecall_count = code_hex.count('f4')
```

### Step 8: Deliver Verdict

**If exploitable**: Provide the exploit path, estimated profit, and PoC code.

**If not exploitable** (dead pool): Provide a concise table showing:
- TVL (with dollar amount)
- TX count (proof of no activity)
- Token distribution (locked vs burned vs held)
- Each attempted exploit vector → why it failed
- Alternative suggestion (next target type)

## Common Dead Pool Patterns

| Pattern | Signature | Action |
|---|---|---|
| 1 TX count | `tx_count == 1` | Created + initial LP minted, never used |
| Zero recent events | No Transfer/swap logs in last 50k blocks | No activity |
| Balances == Reserves | `balanceOf(token, pair) == reserve` | No skim opportunity |
| Owner zero balance | `balanceOf(token, owner()) == 0` | Dev already dumped |
| Standard bytecode | No custom selectors beyond standard ERC20/pair | No custom logic to exploit |

## BSC-Specific Pitfalls

- **web3.py v6**: `ExtraDataToPOAMiddleware` (not `geth_poa_middleware` which was v5)
- **RPC rate limits**: BSC dataseed RPCs return `limit exceeded` above ~100 log queries in range — use tighter block ranges or cache results
- **Etherscan API v2**: V1 is deprecated, V2 migration required
- **Cloudflare**: BscScan and DexScreener both Cloudflare-gated from headless browsers without residential proxies
