# Browser-side API surface extraction (gas hunting)

Technique used on app.manic.trade — Next.js SPA with no obvious API calls
visible in raw HTML/curl. The JS bundles fetch data via internal API.

## Step 1: Extract API calls already made by the page

```javascript
// Browser console — captures every resource the page loaded
performance.getEntriesByType('resource')
  .map(r => r.name)
  .filter(n => /api|graphql|polymarket|manic/i.test(n))
```

This reveals the backend base URL + exact endpoint patterns without
touching any JS bundle. On Manic: `bo-server-api.manic.trade` surfaced
with `/charts/pm/events`, `/users/asset/status`, etc.

## Step 2: Probe endpoints from curl (auth surface)

```bash
# Quick auth-wall detection — 401 = auth-gated, 200 = public
for ep in "/users/me" "/users/orders" "/users/positions" "/orders" "/trade"; do
  curl -s -m 10 -o /dev/null -w "%{http_code} " "https://BASE$ep"
done
```

401 on `/users/me` = Bearer auth. The gap: need a token to go deeper
(orders, positions, settlement — the P0/P1 surface).

## Step 3: CORS check

```bash
curl -s -m 10 -D - -o /dev/null "https://BASE/some-public-endpoint" | head -25
```

`access-control-allow-origin: *` + `access-control-expose-headers: *` on
all public endpoints. Low impact if data is public read-only; escalate if
it exposes auth-gated data via CORS misconfig.

## Step 4 (optional): JS bundle scraping via subagent

If the app loads many split chunks (Next.js, Vite), delegate JS analysis
since bundle content floods context. Prompt pattern:

```
Download JS chunk list from HTML <script> tags. Curl each chunk. Grep for:
- API keys (apiKey, bearer, sk_, pk_, token)
- Base URLs (https://api.*, https://.*.com/v2/)
- GraphQL endpoints (/graphql, gql)
- WebSocket URLs (wss://)
- RPC endpoints (helius, quicknode, alchemy URLs)
```

## What to look for after API surface is mapped

- Endpoints that return user-specific data without proper auth (IDOR)
- Auth tokens passed as URL params (logged in browser history / referrer)
- Debug/verbose query params (?debug=true, ?verbose=1)
- Unused or undocumented endpoints (versioned paths, /admin/, /internal/)

## Auth flow reverse-engineering from JS bundles

When all auth-gated endpoints return 401 and no auth bypass works, reverse the
login flow from the JS bundles to obtain a valid token.

### Step 1: Map the auth endpoints from JS

```bash
cd /tmp/js_bundles
grep -oh 'users_[a-z_]*:"[^"]*"' *.js | sort -u | grep -iE 'challenge|sign|login|check|logout'
# Typical: users_challenge:"/users/challenge", users_sign_in:"/users/sign-in"
```

### Step 2: Probe the challenge endpoint

```bash
curl -s "https://api.target.com/users/challenge?wallet=0xYOUR_ADDRESS"
# Returns: {"message":"Sign this to authenticate... Nonce: ABC123"}
```

### Step 3: Sign and submit (EVM)

The flow: `GET /challenge` -> get message -> sign with private key ->
`POST /sign-in` with `{address, message, signed_message, auth_channel}`.

```python
from eth_account import Account
from eth_account.messages import encode_defunct
import json, urllib.request

acct = Account.from_key('0xYOUR_PRIVATE_KEY')
addr = acct.address  # checksum case matters

# Get challenge
req = urllib.request.Request(
    f'https://api.target.com/users/challenge?wallet={addr}',
    headers={'User-Agent': 'Mozilla/5.0'})
msg = json.loads(urllib.request.urlopen(req, timeout=12).read())['message']

# Sign EIP-191 personal message
sig = acct.sign_message(encode_defunct(text=msg))

# Submit sign-in
data = {
    'message': msg,
    'signed_message': sig.signature.hex(),
    'address': addr,
    'auth_channel': 'wallet'  # critical — server rejects without this
}
req2 = urllib.request.Request(
    'https://api.target.com/users/sign-in',
    data=json.dumps(data).encode(),
    headers={'Content-Type': 'application/json'}, method='POST')
token = json.loads(urllib.request.urlopen(req2, timeout=12).read())['token']
```

### Step 4: Extract token from browser (alternative)

If the JS sign-in is too complex (Turnkey custodial wallet, Particle Network),
have the user log in on their device and extract the app access token from
localStorage:

```js
// In browser console on the target app:
JSON.parse(localStorage.getItem('user-store')).state.accessToken
// or
Object.entries(localStorage).map(([k,v])=>k+': '+v.slice(0,80))
```

Decode JWT payload to confirm user ID and address:

```python
import base64, json
hdr, payload, sig = token.split('.')
# address field may be a byte array, not a hex string
print(json.loads(base64.urlsafe_b64decode(payload + '===')))
# {"exp": ..., "address": [149,52,66,...], "id": 19635, "iat": ...}
```

### Pitfall: Custodial vs self-custody wallet

Some apps use Turnkey (custodial wallet infrastructure) for auth. The sign-in
flow requires a Turnkey session token, not a raw EVM signature. Signs:
- JS bundles reference `@turnkey/core`, `authproxy.turnkey.com`
- `/users/check` requires `sub_org_id`, `user_id`, `wallet_solana`
- Login UI offers Google/X/Email; wallet connect is secondary
- App creates a branded custodial wallet with both Solana and EVM addresses

In this case, the user must log in via the app UI and extract the access token
from localStorage. The Turnkey session token (from `@turnkey/session/v3` in
localStorage) is NOT the app access token. The app token is in `user-store`
(or similar Zustand persist key).

### Pitfall: Address format validation

Servers may validate address format strictly. If sign-in returns "Invalid
address format" despite a valid EVM address:
- Try checksum case (`acct.address` from eth_account)
- Try lowercase (`acct.address.lower()`)
- The challenge endpoint may accept one format but sign-in requires another
- Some servers register the address with the exact case from first login

## Cloudflare WARP for IP rotation

When the target API blocks the VPS IP (returns 403/301/redirect-loop from VPS
but works from mobile browser), use Cloudflare WARP to get a different IP:

```bash
# Install WARP (Ubuntu/Debian)
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | \
  sudo gpg --yes --dearmor -o /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] \
  https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/cloudflare-client.list
sudo apt-get update -qq && sudo apt-get install -y -qq cloudflare-warp

# Register + connect (proxy mode = SOCKS5 on localhost:40000)
warp-cli --accept-tos registration new
warp-cli --accept-tos mode proxy
warp-cli --accept-tos connect

# Verify IP changed
curl -s --proxy socks5h://127.0.0.1:40000 https://ifconfig.me

# Probe API via WARP proxy
curl -s --proxy socks5h://127.0.0.1:40000 \
  -H "Authorization: Bearer TOKEN" \
  https://api.target.com/users/me
```

Note: WARP may not help if the block is server-side (e.g. nginx redirect loop
on the target itself). Verify by checking if the response differs from the
direct VPS request. If both return the same error, it is a server issue, not
an IP block. When the app works from the user mobile browser but not from VPS
or WARP, the block may be region/device-fingerprint based, not pure IP.

## Terminal output encoding workaround

On some VPS environments, terminal output above ~200 bytes gets compressed into
an unreadable `<<ccr>>` format. This affects `execute_code`, `terminal`, and
multi-line `cat` output. Workarounds:

1. Write results to a file, then use `read_file` (which handles encoding
   correctly).
2. For per-line output, split into individual files and `cat` one at a time:
   ```python
   lines = open('/tmp/results.txt').read().split('\n')
   for i, line in enumerate(lines):
       open(f'/tmp/r{i}.txt', 'w').write(line)
   ```
   Then `cat /tmp/r0.txt`, `cat /tmp/r1.txt`, etc.
3. Use `execute_code` with `from hermes_tools import terminal` and print only
   short single-line summaries (< 200 chars).
4. For JSON, write to file and use `read_file` with offset/limit pagination.
