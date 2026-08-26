# Next.js Bundle Configuration Extraction

Deep-dive into Next.js webpack chunks to extract API keys, project IDs, base URLs, and auth endpoints that automated scanners (SecretFinder/LinkFinder) miss.

## Technique Overview

Next.js SPAs split code into 100+ `/_next/static/chunks/*.js` files — webpack chunks loaded on demand. Configuration values are often:
1. **Hardcoded fallback strings** when env vars aren't set (e.g. `w="d1f6f05..."`)
2. **Scattered across chunks** — the main bundle may not contain them
3. **Minified and obfuscated** — `appId:"value"` not `apiKey: "value"`
4. **Referenced indirectly** — values assigned to vars, then used later

## Pipeline

### Step 1: Extract All Chunk URLs from the Page

```bash
# From the HTML source, extract every /_next/static/chunks/ URL:
curl -sL "https://target.com/" \
  | grep -oP '/_next/static/chunks/[^"\047]+' \
  | sort -u > chunk_urls.txt
```

Key patterns to extract:
- `<script src="/_next/static/chunks/...js" async="">` — standard chunks
- RSC payload: `self.__next_f.push([1,"...I[...chunk...]..."])` — React Server Components data contains the component-to-chunk mapping and reveals which chunks hold auth/providers

### Step 2: Search RSC Payload for Provider References

The page HTML contains RSC (React Server Components) data in `self.__next_f.push()` calls. These list which modules reference which chunks:

```bash
curl -sL "https://target.com/" | grep -oP 'self\.__next_f\.push\(\[[12],".*?\]\)' > rsc_payload.txt
```

Look for:
- `AuthProvider` — the auth chunk set
- `PrivyProvider`, `createAppKit` — wallet/identity providers
- `thirdweb`, `walletConnect`, `reown` — wallet SDK references

### Step 3: Download All Chunks in Parallel

```bash
cat chunk_urls.txt | xargs -P 20 -I{} sh -c \
  'name=$(echo "{}" | grep -oP "[^/]+\.js$"); \
   curl -sL "https://target.com{}" -o "chunks/$name" 2>/dev/null'
```

### Step 4: Concatenate and Search

```bash
cat chunks/*.js > all_chunks_combined.js
```

Search patterns (in order of effectiveness):

```bash
# 1. Direct string values — appId, projectId, clientId
grep -oP 'appId:"[^"]+"' all_chunks_combined.js | sort -u
grep -oP 'w="[a-f0-9]{32}"' all_chunks_combined.js  # WalletConnect project IDs

# 2. Env variable fallback patterns — hardcoded defaults when NEXT_PUBLIC_* not set
grep -oP '.{0,60}(NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID|NEXT_PUBLIC_PRIVY_APP_ID).{0,100}' all_chunks_combined.js

# 3. API URLs — base URLs and RPC endpoints
grep -oP 'https://[a-z0-9.-]+\.(com|io|ai|app|org)[^"'"'"' )]+' all_chunks_combined.js | sort -u

# 4. Case-insensitive search for provider/service names
strings all_chunks_combined.js | grep -iE '(privy|thirdweb|reown|walletconnect|project.?id|client.?id|app.?id|api.?key)'

# 5. Look for API key patterns in URLs (QuikNode, Infura, Alchemy)
grep -oP 'https://[^/]+\.(quiknode|infura|alchemy)\.(pro|io)[^"'"'"' )]+' all_chunks_combined.js | sort -u
grep -oP 'rpc\.thirdweb\.com' all_chunks_combined.js

# 6. CSS custom properties and branding — reveal Privy, Reown usage
strings all_chunks_combined.js | grep -i 'privy-color\|reown-logo\|walletConnectBrown'
```

### Step 5: Context-Based Extraction

When a match is found, extract surrounding context to understand usage:

```bash
# Show 100 chars before and after match for context
grep -oP '.{0,100}(appId:"[^"]+").{0,100}' all_chunks_combined.js
grep -oP '.{0,100}w="[a-f0-9]{32}".{0,200}' all_chunks_combined.js
```

For API keys in URLs, extract the full URL:
```bash
grep -oP 'https://quiet-fragrant-sailboat[^"'"'"' )]+' all_chunks_combined.js
```

## What to Look For

### 1. Privy Configuration
- **App ID**: `appId:"yFK5FCqYprrXDiVFbhyRx7"` (format: base-52 string, ~22 chars)
- **API URL**: `this.baseUrl = e.baseUrl ?? "https://auth.privy.io"`
- **OAuth transact URL**: `${apiUrl}/oauth/transact`
- **Auth endpoints**: `/api/v1/auth/qr-login/*`, `/api/v1/wallets/*`

### 2. WalletConnect / Reown Configuration
- **Project ID**: `w="d1f6f05b749ec6d832c8951abeca3038"` (32 hex chars, assigned to var then used as `projectId: w`)
- **RPC URL**: `rpc.walletconnect.org/v1/?chainId=eip155:${chain}&projectId=${id}`
- **Dashboard**: `https://dashboard.reown.com`

### 3. Cloud Provider RPC URLs (API keys in URL path)
- **QuikNode**: `https://*.quiknode.pro/<32-hex-api-key>/` — embedded in BSC RPC URL
- **Thirdweb**: `https://<chain-id>.rpc.thirdweb.com` — used as default RPC provider
- **Privy RPC**: `https://<network>.rpc.privy.systems`

### 4. App-Specific API Base URLs
Look in HTML `<link rel="preconnect">` and DNS prefetch tags:
```html
<link rel="preconnect" href="https://api.target.com" crossorigin="anonymous">
<link rel="dns-prefetch" href="https://static.target.com">
```

Also check the API client initialization in JS:
```javascript
let api = r.Z.create({ baseURL: "https://api.target.com/", ... })
```

### 5. Auth Flow Details
- Session management: `getAccessToken()`, `refreshSession()`, `refreshSessionAndUser()`
- HTTP headers: `privy-app-id`, `privy-client-id`
- Storage: `localStorage` under `privy:*` namespace
- OAuth providers: Google, Twitter, Discord, Apple, Telegram, Farcaster, etc.
- Embedded wallet: iframe postMessage protocol — `privy:iframe:ready`, `privy:wallets:rpc`, etc.

## Common Pitfalls

- **Thirdweb client ID** is rarely hardcoded in bundles — it's typically set at runtime. Look for RPC URL patterns instead which reveal Thirdweb *usage* but not the client ID
- **Reown/AppKit project ID** may be set by env var (`NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID`) with a hardcoded fallback that's the *real* value
- **Minified variable names** change per build — search for the *value string* not the variable name
- **Multiple build manifests** — check both `_buildManifest.js` and the RSC `self.__next_f` payload for complete chunk lists
- **Privy `appClientId`** is typically set via env var, not hardcoded — but `appId` is often hardcoded
