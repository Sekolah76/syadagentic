# Web3 dApp Frontend Recon: Bundle-to-RPC Mapping and Oracle Simulation

Use this reference when a React/Vite/Next dApp talks directly to an EVM RPC and exposes no conventional first-party API.

## Goal

Map the real trust boundaries without reporting expected Web3 architecture as vulnerabilities:

- Browser routes and hidden UI states
- Static and dynamic JS chunks
- Wallet connectors and chain switching
- RPC, explorer, telemetry, and WalletConnect endpoints
- Deployment metadata and contract addresses
- Contract write/read functions surfaced by the frontend
- Safe, non-broadcast simulations of high-impact hypotheses

## Workflow

### 1. Capture both static and runtime assets

Static HTML only shows eagerly loaded chunks. Also capture browser resource timing/network entries after the app renders and after opening the wallet modal.

Record:

- initial module scripts and modulepreloads
- lazy wallet connector chunks
- RPC requests
- WalletConnect/AppKit configuration and telemetry
- image/CSS assets

Do not infer that a lazy chunk is absent merely because a direct downloader later receives a WAF response; browser-observed network entries are still valid evidence that the app requested it.

### 2. Distinguish URL routes from React state

Search for router construction (`BrowserRouter`, `createBrowserRouter`, route objects) and separately search for local nav state such as:

```js
[{ key: "borrow", label: "Borrow" }, { key: "liquidate", label: "Liquidate" }]
```

A UI tab is not necessarily a URL route. Conversely, components referenced in conditional branches but omitted from visible nav can reveal hidden or unfinished protocol functions (`stability`, `stake`, `redeem`) even if they are not directly routable.

### 3. Extract deployed configuration from the built bundle

Prioritize exact literals near chain and deployment objects:

- `chainId`, chain name, RPC URL, explorer URL
- `_priceFeedIsTestnet`, `_isDev`, `startBlock`, bootstrap period
- `addresses: { ... }`
- `projectId`, app name, wallet connector list
- ABI function names used in `readContract` / `writeContract`

Filter address extraction: dependency constants, predeploys, bytecode prefixes, zero address, and Ethereum mainnet helper addresses are not protocol deployments. Require nearby semantic labels or a deployment object.

### 4. Verify every mapped contract exists

Batch `eth_getCode(address, "latest")` against the configured RPC and record runtime byte length. This verifies that the frontend addresses are live contracts without changing state.

Do not treat public RPC URLs, contract addresses, ABIs, explorer URLs, WalletConnect project IDs, Sentry DSNs, or analytics client IDs as secrets by default.

### 5. Map wallet/auth flow accurately

For a direct-to-contract dApp, determine whether there is any application authentication at all:

- nonce endpoint
- SIWE challenge/verify endpoint
- JWT/cookie/session creation
- bearer token use
- application local-storage token

If none is observed, describe authority as wallet/EOA plus contract-level `msg.sender`; do not invent an auth backend. Client-side chain gating and disabled buttons are UX controls, not authorization boundaries.

### 6. Safe state-change simulation

For a suspected dangerous write function, use `eth_call` and `eth_estimateGas` with an arbitrary unprivileged `from` address. Never broadcast unless the rules and user explicitly require it.

Evidence hierarchy:

1. ABI/source suggests a callable function — hypothesis.
2. `eth_call` succeeds from arbitrary EOA — strong evidence.
3. `eth_estimateGas` succeeds rather than reverting — confirms transaction acceptance path.
4. Local fork shows downstream state/impact — end-to-end proof.
5. Broadcast testnet transaction — only when explicitly authorized and safe.

Include the exact calldata, caller, target, block tag, response, and decoded value.

## High-signal pattern: test price feed deployed as the live oracle

If the bundle says `_priceFeedIsTestnet: true`, inspect the live price-feed ABI for `setPrice(uint256)` and verify access control non-destructively.

Example simulation:

```json
{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"from":"0x1111111111111111111111111111111111111111","to":"<PRICE_FEED>","data":"<setPrice calldata>"},"latest"]}
```

A successful ABI `true` result plus a successful gas estimate strongly indicates a permissionless setter. Build hypotheses around all consumers of that price: borrowing capacity, ICR/TCR, recovery mode, liquidations, and redemptions. Prefer a local fork for end-to-end impact proof.

## CORS and header interpretation

- No ACAO on the static app for an attacker origin means no first-party readable CORS issue.
- `Access-Control-Allow-Origin: *` on a public JSON-RPC endpoint is normally required for browser dApps and is not a vulnerability by itself.
- Missing CSP, Referrer-Policy, and Permissions-Policy are hardening gaps unless chained to a concrete exploit.
- Missing `X-XSS-Protection` is not a modern finding; the header is obsolete.

## Source maps

Probe `bundle.js.map` for every initial and runtime chunk before request volume triggers rate controls. Record status and content type. A generic WAF `403` does not prove a map or protected file exists; only a valid source-map JSON response is exposure.

## Scanner false-positive gate

Reject findings when:

- the alleged endpoint is absent from bundle and runtime network traces
- the evidence body is a generic WAF/challenge/SPA HTML page
- `403` is interpreted as proof that `/.git/*` exists
- status or `poc_status` says confirmed but the machine verdict remains `candidate` and has no oracle receipt
- response differences are caused by rate limiting rather than the tested input

For SQLi specifically, require a reproducible boolean/error/time oracle against a real parameterized endpoint, with matched baseline/control requests and stable bodies.

## Deliverables

Produce:

1. Route/UI-state map
2. Initial and runtime chunk list
3. API/RPC/third-party endpoint map
4. Wallet/auth flow
5. Deployment metadata and labeled contract addresses
6. `eth_getCode` verification table
7. CORS/security-header/source-map results
8. Exact safe-simulation evidence
9. Candidate hypotheses ranked by confidence
10. Explicit false-positive exclusions
