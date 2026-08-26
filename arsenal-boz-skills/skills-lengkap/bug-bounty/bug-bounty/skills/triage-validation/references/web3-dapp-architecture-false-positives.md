# Reference: Web3 dApp Architecture — Common False Positives

> Kill findings that describe standard, expected architecture of any Web3 SPA.
> These consistently get N/A'd or marked Informational.

## Context

Every DeFi dApp (Uniswap, Aave, Compound, Memento, etc.) shares the same fundamental
architecture. The patterns below are NOT vulnerabilities — they are the baseline design.

## ALWAYS-KILL LIST for Web3 dApps

### 1. "Open RPC Endpoint" / "Unauthenticated RPC Proxy"

**Why it's not a bug:**
- The dApp's frontend MUST talk to a blockchain node. This is the fundamental requirement.
- RPC URLs are always in the JS bundle — that's how the browser connects to the chain.
- Testnet nodes (Sepolia, Fuji, Amoy, etc.) are free and public anyway.
- Rate limiting is handled by the upstream provider (Infura/Alchemy/QuickNode), not the dApp.
- `eth_sendRawTransaction` on testnet has zero monetary value.
- Batch RPC is standard JSON-RPC spec behavior.

**Kill signals:**
- Endpoint is `/testnet/*` (free tier, no financial impact)
- Provider error messages mention "Free tier" (no billing abuse possible)
- Same pattern visible in every major DeFi dApp's frontend
- CORS `*` is required for the SPA to function (different origin for API vs frontend)

**Only survives if:**
- **Mainnet** RPC with a **paid** provider key embedded in URL (actual API key leak)
- RPC proxy accepts `admin_*` / `debug_*` methods that expose node internals
- No upstream rate limiting AND mainnet with real cost
- RPC endpoint proxies to internal infrastructure beyond the blockchain node

### 2. "VUE_APP_* / NEXT_PUBLIC_* / REACT_APP_* Environment Variables in JS Bundle"

**Why it's not a bug:**
- These prefixed env vars are CLIENT-SIDE by framework design (Vue, Next.js, React).
- They are intentionally embedded in the production bundle for the browser to use.
- They are NOT secrets — they are public configuration.

**Specific non-secrets commonly reported:**
| Variable | Why it's not sensitive |
|----------|----------------------|
| WalletConnect Project ID | Public identifier, visible in every WC-integrated dApp |
| Chain IDs, RPC URLs | Public blockchain infrastructure data |
| Explorer URLs | Public knowledge |
| SDK version numbers | Available via npm registry |
| Support email | Usually on the website already |
| Notion/wiki URLs | Often public documentation |

**Kill signals:**
- Variable has `VUE_APP_` / `NEXT_PUBLIC_` / `REACT_APP_` prefix
- No actual credential/secret value (no API key with write access, no private key)
- Values are publicly available elsewhere (website, npm, blockchain explorers)
- `WEBPACK_MODE: "development"` is just a label — check if bundle is actually minified

**Only survives if:**
- Actual secret leaked: API key with billing/write access, private key, JWT secret
- Internal-only URLs that reveal undocumented admin panels or staging environments
- Database credentials, AWS secret keys, or other backend secrets accidentally included

### 3. "CORS Access-Control-Allow-Origin: * on API"

**Why it's not a bug (for Web3 dApps with token-based auth):**
- Auth is header-based (Bearer token), NOT cookie-based
- CORS `*` with token auth = no credential forwarding possible cross-origin
- `Access-Control-Allow-Credentials: true` is NOT set (browsers won't send cookies)
- SPA on `app.example.com` calling API on `api.example.com` = cross-origin by definition
- They NEED permissive CORS for the dApp to function

**Kill signals:**
- Auth mechanism is `Authorization: Bearer <token>` (header-based)
- No `Access-Control-Allow-Credentials: true` in response
- Public data endpoints that are meant to be readable
- Standard SPA + API gateway architecture

**Only survives if:**
- Auth is cookie-based AND `Access-Control-Allow-Credentials: true` is set
- Combined with demonstrated token theft (XSS → exfil → cross-origin replay)
- Reflects arbitrary Origin in `Access-Control-Allow-Origin` (not just `*`) WITH credentials

### 4. "Information Disclosure via Error Messages" (from RPC/API)

**Why it's usually not a bug:**
- Provider tier info ("Free tier - upgrade to Pay As You Go") = no actionable secret
- Generic error codes (I013, E404) without stack traces = low/no impact
- Framework version in headers (e.g., `X-Powered-By: Express`) = informational only

**Only survives if:**
- Stack trace with file paths, internal IPs, or database connection strings
- Error response reveals other users' data (actual data leak)
- Debug mode exposes request/response logging with sensitive payloads

---

## Decision Framework for Web3 dApp Findings

Before writing any report on a Web3 dApp, ask:

```
1. Would this same "finding" apply to Uniswap, Aave, or Compound?
   → If YES: it's standard architecture, not a bug. KILL.

2. Is the "sensitive" data actually needed by the browser to function?
   → If YES: it's client config by design. KILL.

3. Does the CORS + auth mechanism combo actually allow cross-origin credential theft?
   → If token-based (not cookie): no cross-origin attack. KILL.

4. Is the "financial impact" claim based on testnet/free-tier resources?
   → If YES: zero real cost. KILL.
```

## What DOES Work on Web3 dApps

Focus testing on:
- **Business logic** in smart contracts (reentrancy, oracle manipulation, access control)
- **IDOR** on user-specific data (fund details, order history, portfolio)
- **Stored XSS** that can steal session tokens → chain to account takeover
- **SSRF** via image/URL processing endpoints (e.g., `/images/analyze`)
- **Auth bypass** that allows accessing/modifying other users' funds or configurations
- **Race conditions** in redemption/deposit flows
- **Pre-signed URL abuse** if upload endpoints generate S3 URLs without proper auth

---

## Real Example: Memento DFM (July 2026)

Three findings were prepared and ALL killed by adversarial review:

| Finding | Kill Reason |
|---------|-------------|
| Open RPC Proxy (6 testnet chains) | Standard Web3 arch; testnet = free; no financial impact |
| Env leak in JS bundle (WalletConnect ID, etc.) | VUE_APP_* = public client config by design |
| CORS `*` on API | Token-based auth; no credential forwarding; needed for SPA |

**What DID survive:** Missing auth on 23+ state-changing endpoints (inconsistent API Gateway
authorizer enforcement). Proven via:
1. `referral/code/generate` returns 200 OK with data for any wallet — zero auth
2. Fake Bearer token on `maker/add-order` → "Invalid request body" (no authorizer)
3. Fake Bearer token on `funds/delete` → "Unauthorized" (has authorizer)
4. Framed as **business logic / inconsistent enforcement**, not "API Authorization"

**Lesson:** Apply adversarial review BEFORE writing reports. The 3 arch-level false positives
consumed 45+ minutes. The real finding (auth mapping) was discovered by pivoting to
differential testing (which endpoints check auth vs which don't).

**Workflow correction:** On Web3 dApps, skip RPC/CORS/env findings entirely. Start with:
1. Enumerate all API endpoints from JS bundle (`grep -oP "AWS_API\s*\+\s*'[^']+'" app.js`)
2. Map auth enforcement via fake-token probe (see below and `web-pentest-toolkit/references/aws-apigw-spa-endpoint-discovery.md`)
3. Focus on endpoints that process requests without auth
4. Find correct body format for at least one exploitable endpoint (anchor proof)

## Auth Mapping Technique (Proven on Memento DFM 2026-07)

Send the same fake Bearer token to ALL endpoints. Classify by response:

```python
body = {'wallet': '0x...', 'chainId': 11155111}
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer faketoken123'}
for endpoint in endpoints:
    resp = requests.post(f'{base}/{endpoint}', json=body, headers=headers)
    if 'Missing Authentication Token' in resp.text:
        status = 'NONEXISTENT (route not configured for this method)'
    elif 'Unauthorized' in resp.text:
        status = 'PROTECTED (Lambda authorizer present)'
    elif 'Invalid request body' in resp.text:
        status = '*** UNPROTECTED (no authorizer, body processed) ***'
    elif resp.status_code == 200:
        status = '*** EXPLOITABLE (no auth, returns data) ***'
    print(f'{endpoint}: {status}')
```

Key insight for reports: If you find BOTH protected and unprotected endpoints on the same API, the inconsistency IS the finding. Frame as "Inconsistent API Gateway Authorizer Enforcement" not "Missing Authentication" (which may be explicitly excluded by the program).

## SIWE Login (EIP-4361) Crash as a Separate Finding

If `POST /session/generate` returns 500 ISE for ALL wallets across ALL chain IDs:
- This is a valid **Availability** finding (DoS on authentication)
- Prove with 5+ unique freshly-generated wallets (not wallet-specific)
- Include error UUID from each attempt (shows server processing, not network failure)
- Frame as "Unhandled Exception in SIWE Authentication Flow" — not an "API Authorization" issue
- Secondary impact: prevents ALL security researchers from testing authenticated surface

## X-Custom-Header Identity Pattern

Some AWS APIGW + Lambda apps pass user identity via a custom header like:
```
X-Custom-Header: wallet_address#system#chainId
```
If endpoints without a Lambda authorizer trust this header for identity, an attacker can impersonate any user by setting the header. Test by:
1. Sending requests to unprotected endpoints WITH X-Custom-Header set to a victim's wallet
2. Checking if returned data changes based on the header value
3. If the backend uses this header to scope queries → BOLA / impersonation finding
