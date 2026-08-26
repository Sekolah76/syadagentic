# Payment Platform Recon via Public Clients and SDKs

Use this workflow when a payment platform exposes web apps plus public mobile/React Native SDKs. Public SDKs often provide a cleaner and more authoritative API map than minified web bundles.

## 1. Capture the live policy exactly

Dynamic policy pages may expose headings but omit list-item text in accessibility snapshots. Extract both:

- `document.body.innerText`
- all anchors as `{text, href}`

Write a scope fence before probing. Separate:

- primary wildcard roots;
- secondary assets requiring a specific impact condition;
- explicitly retired contracts/services;
- unlisted staging/test systems.

Inventory excluded staging hosts, but do not probe them unless the policy expressly permits it.

## 2. Use multiple passive certificate sources

If `crt.sh` returns zero or malformed JSON, do not infer that the root has no subdomains. Pivot to:

```bash
curl -sS 'https://api.certspotter.com/v1/issuances?domain=target.com&include_subdomains=true&expand=dns_names' \
  | jq -r '.[].dns_names[]?' | sort -u

curl -sS 'https://api.hackertarget.com/hostsearch/?q=target.com'
```

Merge, normalize wildcard names, resolve DNS, then probe only policy-compliant production hosts.

## 3. Build a web-bundle manifest

For each high-value app:

1. Save HTML.
2. Resolve every `<script src>` to an absolute URL.
3. Fetch bundles concurrently at low volume.
4. Extract:
   - absolute URLs;
   - API-like paths;
   - environment-variable names;
   - auth header construction;
   - route methods, bodies, and state transitions.
5. Save concise extracts separately from raw bundles.

Prioritize application chunks (`app/.../page-*.js`, auth routes, protected layouts) over framework/vendor chunks.

## 4. Treat public SDKs as protocol documentation

Clone only current public repositories. Search platform-native API resource definitions and network interceptors:

- iOS: `APIResource`, `path`, `method`, `bodyParams`, `authToken`;
- Android: `HttpUrl.Builder`, interceptors, request bodies, token providers;
- React Native: initialization parameters and native bridge calls.

Build a method/path/auth/body matrix. Cross-check implementations to distinguish intentional public endpoints from missing authorization.

High-value classes commonly exposed by SDKs:

- token create/verify/refresh/delete;
- account create/read/delete;
- OTP or passkey verification;
- payment/commerce-session create/read/mutate/close/approve;
- transaction-signature submission;
- SSE/event subscriptions;
- one-time-key synchronization.

## 5. Convert the map into owned-account experiments

Do not test object authorization using unrelated users. Prepare two researcher-owned accounts and two independent device/verifier pairs.

Primary experiments:

1. Cross-swap token IDs, OTPs, links, PKCE verifiers, challenges, device IDs, and email identities.
2. Cross-account read/mutate/close/approve payment-session IDs.
3. Replay stale OTPs, signed payloads, or revoked tokens.
4. Mutate amount, asset, brand, or destination after approval/signature generation.
5. Test profile updates for undocumented writable fields.

A result is reportable only when the response proves unauthorized account control, cross-account data access, or payment-state integrity impact.

## 6. Kill common false positives early

Do not report these without an exploit chain:

- client-side publishable keys;
- WalletConnect project IDs, Infura IDs, or public RPC identifiers;
- wildcard CORS on intentionally public/on-chain-derived data;
- public collateral or wallet-indexed blockchain data;
- internal service names embedded in server-rendered config without reachability or trust-boundary impact;
- missing hardening headers without a concrete XSS/clickjacking/data-impact path;
- bugs tied only to contracts explicitly retired or excluded by policy.

## Deliverables

Store:

- `SCOPE_FENCE.md`
- `ENDPOINT_MAP.md`
- `RECON_SUMMARY.md`
- raw HTML/bundles and concise extraction files
- safe unauthenticated baseline request/response captures

State clearly whether any submission-ready vulnerability is confirmed. Recon artifacts and hypotheses are not findings.
