# Live dApp Deployment Provenance and Custom-Chain Forking

Use this when a dApp's public repository, checked-in deployment manifest, docs, and currently served frontend may describe different deployments.

## Provenance-first workflow

1. **Treat the active frontend bundle as the first deployment index.** Extract chain ID, RPC, explorer, deployment block/time, feature flags, and every contract address from the currently served bundle/network trace.
2. **Verify live state before source conclusions.** For each address, check runtime bytecode and critical wiring accessors. Record owner/admin state, especially after one-time initialization and ownership renunciation.
3. **Classify every artifact explicitly:**
   - `current`: loaded by the active app and backed by live bytecode;
   - `legacy`: older chain/manifest still publicly reachable;
   - `candidate source`: architecture-correlated but not yet proven equivalent.
4. **Never let a checked-in manifest outrank the active app.** If the app moved chains, preserve earlier findings under a clearly named `legacy-<chain>/` directory and rewrite the primary summary immediately.
5. **Establish source equivalence per contract.** Compare deployed runtime with the compiled artifact exactly, then metadata-stripped. Do not infer equivalence for sibling contracts merely because one contract matches.
6. **Use live accessors plus execution.** Confirm that vulnerable component addresses are actually consumed by core contracts. A complete proof should mutate the candidate component on a pinned fork and reach the business impact through actual deployed contracts.

## Minimal evidence package

- Active bundle URL/hash and extracted deployment JSON.
- Live chain ID and pinned fork block.
- Runtime byte length and `keccak256` for live and compiled bytecode.
- Exact or metadata-stripped equality result.
- Critical wiring/accessor output and owner/admin state.
- Arbitrary-caller `eth_call` or `eth_estimateGas` reachability check.
- Full fork transaction sequence with local transaction hashes, balance deltas, post-state, and assertions.
- Public explorer transaction history when it independently demonstrates real caller reachability.

For Blockscout-family explorers, the useful endpoint is often:

```text
/api/v2/addresses/<contract>/transactions
```

Filter by method selector/decoded method, caller, value, block, and transaction status. Existing transactions prove reachability but do not by themselves prove malicious intent.

## Pinned custom-chain fork fallback

Some custom EVM chains do not expose hardfork activation metadata in a form the local Hardhat execution engine can infer. Do not weaken the proof or switch to a local re-deployment. Use a pinned Ganache fork and run the Hardhat test against its JSON-RPC endpoint:

```bash
npx --yes ganache@7.9.2 \
  --fork.url "$RPC_URL" \
  --fork.blockNumber "$BLOCK" \
  --chain.chainId "$CHAIN_ID" \
  --server.host 127.0.0.1 \
  --server.port 8545 \
  --wallet.totalAccounts 10 \
  --wallet.defaultBalance 10000 \
  --wallet.deterministic
```

Add a localhost network entry to Hardhat and run:

```bash
npx hardhat test test/poc.js --network localhost
```

Before each run, verify which process owns port 8545 and start from a fresh fork. Otherwise a previous run's state can make an attacker position already active and invalidate reproducibility.

## PoC quality rules

- Pin the source block.
- Await transaction receipts.
- Print local fork transaction hashes and state deltas.
- Assert the attacker outcome and corresponding protocol-side state change.
- Distinguish fork transaction hashes from public-chain hashes.
- State whether any public transaction was broadcast.
- If a fixture is intentionally marked dev/testnet, preserve that counterargument. Report demonstrated public-testnet integrity impact, not unproven mainnet loss.

## Session-derived example

In the Instaliquid review, the public repositories described an older Sepolia Hoodlend deployment while the active app loaded a Robinhood Chain Testnet Instaliquid deployment. Re-scoping to the active bundle exposed an exact-match `PriceFeedTestnet` whose unrestricted setter was wired permanently into live BorrowerOperations and TroveManager. A pinned custom-chain fork proved `setPrice -> openTrove -> IUSD mint` using the actual deployed contracts. The earlier Sepolia findings remained valid only as legacy deployment results.
