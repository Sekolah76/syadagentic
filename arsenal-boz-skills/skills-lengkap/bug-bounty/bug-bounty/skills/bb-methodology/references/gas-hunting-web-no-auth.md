# Gas Hunting — Web App Recon Without Auth

Quick recon workflow for web app bug bounties when you have zero
credentials but want to map every endpoint and find auth bypasses.

## Phase 1: JS bundle download

```bash
# Fetch SPA HTML, extract all script src
curl -sL "$TARGET" | grep -oP 'src="([^"]*\.js[^"]*)"' | cut -d'"' -f2 | sort -u > /tmp/chunks.txt
# Download all chunks
mkdir /tmp/js_bundles
while IFS= read -r url; do
  curl -sL "$url" -o "/tmp/js_bundles/$(basename $url | cut -d'?' -f1)"
done < /tmp/chunks.txt
```

## Phase 2: Extract API surface

```bash
# API endpoints (internal)
grep -roh 'https://[a-z0-9.-]*\.target-domain\.com' /tmp/js_bundles/ | sort -u
# API paths
grep -roh '"[a-z_]*:"/[^"]*"|'"'"'[a-z_]*:''"'"''/'"'"'[^'"'"'"]*'"'"''" /tmp/js_bundles/ | sort -u
# Auth-related (Turnkey, Particle, OAuth)
grep -rli 'turnkey\|particle\|auth/token\|bearer\|sign-in\|challenge' /tmp/js_bundles/
```

## Phase 3: Probe auth gates

```
GET /api/ua/account → 401 "Missing Authorization" → needs Bearer
POST /users/sign-in → 422 "missing field X" → reveals body shape
GET /users/challenge?wallet=<addr> → 200 message → sign → POST sign-in
```

## Phase 4: Bypass attempts (ordered by priority)

1. **Header spoof:** X-Forwarded-For: 127.0.0.1, X-Original-URL, X-Rewrite-URL
2. **Method override:** X-HTTP-Method-Override, POST→GET
3. **Path tampering:** trailing slash, double slash, dot segment, encoded dot, case variation, semicolon
4. **Auth header variants:** Bearer null, Bearer <empty>, Basic admin:admin
5. **JSON body fuzzing:** add fields one by one (server leaks schema via 422 errors)

## Critical pitfall: Turnkey custodial auth

Some web3 apps (Manic, others) use **Turnkey** for custodial wallet
management. The "Connect Wallet" UI shows EVM/Solana tabs, but auth is NOT
a plain wallet signature — it goes through Turnkey's
`/users/check`→`/users/challenge`→`/users/sign-in` flow, requiring a
Turnkey-registered user. An imported EVM private key cannot log into a
Turnkey-gated backend. The browser must complete Turnkey registration
(Google/Email/Apple OAuth) first. Don't waste time trying to sign
messages from a raw private key against a Turnkey backend — it won't work.

**Detection signal:** `/users/check` returns `sub_org_id is required`,
`user_id is required`, `wallet_solana is required` → Turnkey flow. Move on
or pivot to UI-based registration.

## Phase 5: Public endpoints worth probing

Even without auth, check:
- `/api/assets`, `/api/config`, `/v1/server-time` — info leaks
- WebSocket endpoints (`wss://`...) — may broadcast user data without auth
- CORS headers: `access-control-allow-origin: *` on every endpoint → low-hanging P3
- 405 Method Not Allowed endpoints — try POST with empty body, check response
