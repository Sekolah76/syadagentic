# Cosmos SDK Chain Audit (EVM-integrated)

Auditing a Cosmos SDK chain (e.g. `x/` modules + EVM precompiles) differs from
pure Solidity audits. Attack surface lives in Go, not just `.sol`.

## Recon order
1. `git clone --depth 1` the chain repo. Count `.sol` — on an EVM-integrated
   Cosmos chain most are **testdata/suites**, not live contracts. Don't fixate there.
2. `ls x/` — list modules. High-value: `vm`, `bank`, `feemarket`, `precisebank`,
   `erc20`, any `auth`/`acl`/`permission`.
3. `find x/ -name '*.go' | grep -v _test` — map the Go surface.
4. Precompile wrappers: `x/vm/wrappers/*.go` bridge EVM <-> Cosmos modules.

## High-value bug classes (Cosmos-specific)
- **Denom / decimal scaling** — EVM works in 18 decimals, bank module may use
  6 or 18. `ConvertEvmCoinDenomToExtendedDenom` / `ConversionFactor()` /
  `TruncateInt()` are the classic rounding/truncation spot. A scaling bug =
  mint/burn wrong amount. Check `x/vm/types/scaling.go` and its `_test.go`.
- **Bank wrapper** — `MintAmountToAccount` / `BurnAmountFromAccount` /
  `SendCoinsFromAccountToModule` convert denom then move coins. Verify
  zero-amount no-op guards (`convertedCoins.IsZero()`), and that only
  authorized callers reach mint/burn.
- **Fee market** — `GetBaseFee` does `MulInt(ConversionFactor()).TruncateInt()`.
  Truncation = minor fee discrepancy (low severity, but note it).
- **Key escrow / signer** — Go agents often hold signing keys. Check:
  - OS keyring (`99designs/keyring`) with env-var fallback (e.g. `SIGNER_KEY_HEX`).
    Env fallback = key compromise if env leaks. Confirm format validation lives
    at the trust boundary, not assumed by caller.
  - EIP-712 signing (`signer/eip712.go`) — signature replay, missing domain
    separator, malleability.

## Pitfall
- `skills_list`/`skill_view` may return `<<ccr:...>>` encoded blobs when output is
  large. Read files via `read_file`/`grep` in small chunks, or `git clone` + local
  grep, instead of trusting truncated snapshots.
