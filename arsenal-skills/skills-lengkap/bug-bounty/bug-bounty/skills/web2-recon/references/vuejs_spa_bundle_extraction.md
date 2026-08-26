# Vue.js SPA Bundle Extraction — API Routes, Env Vars, RPC Proxies

## When to Use

Target serves a Vue.js SPA (detected via `<div id="app"></div>`, `/js/app.*.js` bundle, Fomantic-UI/Semantic-UI, or `vue-router`/`vuex` patterns). Common in DeFi/Web3 dApps built with Vue CLI + webpack.

## Detection Signals

```bash
# Check for Vue.js SPA
curl -s "https://target.com" | grep -oP '(id="app"|vue|vuex|vue-router|VUE_APP_)'
# Check for webpack chunk pattern
curl -s "https://target.com" | grep -oP '/js/app\.[a-f0-9]+\.js'
```

## Step 1: Download Main Bundle

```bash
# Extract JS bundle URL from HTML
BUNDLE=$(curl -s "https://target.com" | grep -oP '/js/app\.[a-f0-9]+\.js' | head -1)
curl -s "https://target.com${BUNDLE}" -o /tmp/app.js
echo "Bundle size: $(wc -c < /tmp/app.js) bytes"
```

## Step 2: Extract Full process.env (VUE_APP_* vars)

Vue CLI embeds ALL `VUE_APP_*` environment variables into the bundle via webpack DefinePlugin. Unlike Next.js (which only embeds `NEXT_PUBLIC_*`), Vue CLI dumps EVERYTHING prefixed with `VUE_APP_`.

```bash
# Extract all VUE_APP variables
grep -oP '"VUE_APP_[A-Z_]+":"[^"]*"' /tmp/app.js | sort -u

# Common high-value leaks:
# VUE_APP_WALLET_CONNECT_PROJECT_ID — relay abuse/impersonation
# VUE_APP_ALCHEMY_KEY — RPC key ($$$ if active)
# VUE_APP_WEBPACK_MODE: "development" — signals debug paths
# VUE_APP_BLOCKCHAINS — full chain config with RPC URLs
# VUE_APP_*_API_KEY — any third-party API key
# VUE_APP_PRIVIDIUM_* — KYC/auth provider config

# Extract RPC URLs from blockchain config
grep -oP '"rpc":"[^"]*"' /tmp/app.js | sort -u
```

## Step 3: Extract API Route Map

DeFi dApps often define API routes as constants:

```bash
# Pattern: functionName: BASE_URL + 'path'
grep -oP '[a-zA-Z]+:\s*AWS_API\s*\+\s*['"'"'"]([^'"'"'"]+)['"'"'"]' /tmp/app.js | sort -u

# Pattern: BASE_URL + 'path' (cached/public API)
grep -oP 'AWS_API_CACHED\s*\+\s*['"'"'"]([^'"'"'"]+)['"'"'"]' /tmp/app.js | sort -u

# Generic API path extraction
grep -oP '(baseURL|apiUrl|API_URL|API_BASE)[^}]{0,200}' /tmp/app.js | head -10

# Find connect-src in CSP (reveals ALL backend domains)
grep -oP 'connect-src[^;]+' /tmp/app.js | tr ' ' '\n' | sort -u
```

## Step 4: Identify Auth Mechanism

```bash
# SIWE (Sign-In with Ethereum) pattern
grep -oP '(generateSession|verifyMessage|SIWE|formatMessage|createSIWEConfig)[^;]{0,100}' /tmp/app.js | head -5

# Session token storage
grep -oP '(sessionToken|localStorage|Authorization|Bearer)[^;]{0,100}' /tmp/app.js | head -10

# Auth flow: nonce → sign → generate → store token
# Body format typically: { message, signature, system }
```

## Step 5: RPC Proxy Discovery & Abuse Testing

When RPC URLs point to the target's own domain (e.g., `api.target.com/testnet/ethereum`), test:

```bash
RPC="https://api.target.com/testnet/ethereum"

# 1. Confirm unauthenticated access
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' "$RPC"

# 2. Test batch RPC (amplification)
curl -s -X POST -H "Content-Type: application/json" \
  -d '[{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1},{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":2}]' "$RPC"

# 3. Test transaction relay
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_sendRawTransaction","params":["0x"],"id":1}' "$RPC"

# 4. Probe expensive methods (info leak via error)
for method in debug_traceTransaction trace_block eth_getLogs admin_peers; do
  echo -n "$method: "
  curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"$method\",\"params\":[\"latest\"],\"id\":1}" "$RPC" | grep -oP '"message":"[^"]*"'
done

# 5. Check rate limiting
for i in $(seq 1 10); do
  curl -s -o /dev/null -w "%{http_code} " -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' "$RPC"
done

# 6. CORS on RPC proxy
curl -s -D- -o /dev/null -H "Origin: https://evil.com" -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' "$RPC" | grep "access-control"
```

**What makes this a finding:**
- No authentication required
- No rate limiting
- Batch support = cost amplification
- `eth_sendRawTransaction` = free relay
- Error messages leak provider tier (Infura/Alchemy/QuickNode)
- CORS `*` = any website can use it

## Step 6: Upload Endpoint Pre-signed URL Discovery

```bash
# Look for S3 upload patterns
grep -oP '(upload|presign|s3|signedUrl)[^;]{0,200}' /tmp/app.js | head -10

# Test without auth (check for 401 vs "Invalid request body")
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"filename":"test.png","contentType":"image/png"}' \
  "https://api.target.com/dd/funds/upload-logo-url"
# "Invalid request body" (not 401) = endpoint doesn't check auth first!
```

## Key Patterns (Vue CLI + DeFi)

| Pattern in JS | What It Reveals |
|---|---|
| `AWS_API = \`\${BASE}/${ENV}/\`` | API gateway path structure |
| `AWS_API_CACHED = \`\${BASE}/${ENV}/\`` | Public/cached API path |
| `VUE_APP_BLOCKCHAINS: "[{...}]"` | All supported chains + RPC URLs |
| `SYSTEM = "dapp"` | System identifier for API calls |
| `connect-src` in CSP | Complete backend domain inventory |
| `tmp.upload.*.amazonaws.com` in CSP | S3 upload bucket (test PUT access) |
| `*-staging.supozu.com` | Third-party staging endpoints |

## Pitfalls

- Vue CLI **always** leaks all `VUE_APP_*` vars — this is by design, not a bug per se. The finding is WHAT's in those vars (API keys, dev mode, internal URLs).
- Session/generate returning 500 usually means the wallet isn't registered, not a signature format issue. Need to use a wallet that has interacted with the dApp.
- `/dd/` vs `/dcd/` convention: the path prefix often encodes auth requirement (`dd` = authenticated, `dcd` = cached/public). Test both.
- "Missing required request parameters" ≠ needs auth. It means the endpoint is reachable but you need correct query params.
- "Invalid request body" on POST = endpoint doesn't enforce auth first. Body validation happens BEFORE auth check — potential to interact without session.
