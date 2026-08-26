# Cosmos SDK / EVM fork precompile authorization audit

## Core pattern: custom precompile wrappers over x/bank
Many Cosmos SDK chains add custom EVM precompiles that wrap `x/bank` mint/burn/transfer
with a "backed ERC-20" pattern. These are high-value targets because they introduce
new trust boundaries not present in upstream Evmos. The fork delta is small, so every
custom file matters.

## High-signal bug: missing authz on Mint/Burn/Transfer
The canonical bug: guard = `requireContractCaller(IsContract)` + `resolveDenom(TokenPair[caller])`.
No check that caller is authorized to mint, no check that `from == caller` on Transfer.

Attack chain:
1. Deploy contract (permissionless).
2. Register TokenPair for valuable denom via custom `RegisterERC20WithDenom` (if permissionless — must verify against upstream `PermissionlessRegistration` param).
3. Call precompile `Mint(to=attacker, amount=unlimited)` — mint from thin air.
4. Dump on AMM → drain reserve.
Severity: Critical if denom binding is permissionless; Medium if gov-gated.

## Precisebank fractional reserve (Evmos fork)
`x/precisebank` tracks integer + fractional balances with a reserve module account.
Invariant: `total extended supply == integer supply + fractional remainder`.
Mint/burn asymmetry (burn.go Case #1-#4) can steal integer coins from reserve.
Requires fork PoC (anvil fork + forge test) to confirm.

## Audit approach for Cosmos chain forks
1. `git log --oneline` — confirm fork depth. Shallow clone = 1 commit = all custom.
2. Focus on files NOT in upstream `cosmos/evm`: precompiles/, custom keeper methods, x/ module additions.
3. SECURITY.md is typically upstream-standard — no chain-specific bounty. Contact via repo/Discord.
4. Safe areas (don't waste time): scaling.go (ConversionFactor < 2^64), vm msg_server (authority gated), bank.go wrappers (denom-safe).

## Reference: SVP Chain audit (2026-08-06) — CONCLUDED

**Targets:** `svpchain/evm` (cosmos/evm fork), `svpchain-agent`
**Scope:** custom delta from upstream — precompiles, keeper funcs, x/ module additions

### Findings

| # | Finding | Severity | Verdict |
|---|---------|----------|---------|
| 1 | BankERC20 precompile — missing authz on mint/burn/transfer | Medium | Confirmed; escalation to Critical blocked |
| 2 | SIGNER_KEY_HEX env fallback (svpchain-agent) | Low | Confirmed |
| 3 | RegisterERC20WithDenom permissionless | N/A | **Refuted** — `validateAuthority` gov-gated |
| 4 | precisebank fractional reserve asymmetry | N/A | **Refuted** — invariant holds, tests cover |
| 5 | scaling.go Uint64 overflow | Info | No overflow (ConversionFactor max 1e17)

### Finding 1 detail — BankERC20 precompile

`precompiles/bankerc20/tx.go`: Mint/Burn/Transfer guarded only by
`requireContractCaller(IsContract)`. No minter whitelist, no `from == caller`
check. Any deployed contract can mint/transfer for whatever denom its own
TokenPair resolves to.

**Why Medium, not Critical:** `RegisterERC20WithDenom` (the path to bind a
valuable denom) is gov-gated via `validateAuthority(req.Authority)`.
`RegisterERC20` (permissionless) only auto-generates worthless denoms
(`erc20/0x...`). To escalate: attacker needs governance to bind a valuable
denom to their contract, which is out of reach without a separate governance
compromise.

**Files:** PoC at `poc/BankERC20MintPoC.sol`, report at
`01-bankerc20-missing-authz.md`, full bundle at `REPORT.md`.

### Finding 2 detail — SIGNER_KEY_HEX

`svpchain-agent/internal/manage/manage.go:140`: `SelectKey` falls back to
`SIGNER_KEY_HEX` env var when OS keyring is nil. Process-env read = private
key compromise. Remediation: remove env fallback, require keyring or
encrypted `0600` file.

### Cleared areas
- `x/vm/types/scaling.go` — ConversionFactor < 2^64
- `x/vm/keeper/msg_server.go` — authority checks OK
- `x/precisebank/keeper/burn.go,mint.go,send.go` — reserve invariant holds
- `x/erc20/keeper/msg_server.go` — `RegisterERC20WithDenom` gov-gated

### Not reviewed (blocked)
- `svpchain-agent/internal/signer/eip712.go` (369L) — signature replay/domain separator
  Blocked by output encoding limits on analysis box.

### Disclosure path
`SECURITY.md` is standard Cosmos upstream — no separate SVP bounty program.
Contact via repo / Discord / security@interchain.io.
