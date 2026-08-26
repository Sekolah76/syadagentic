# Sails.js Reconnaissance Patterns

Session-specific detail from kuant.ai audit (2026-07-23).
Framework: Sails.js (Node.js Vue SPA backend).

## Detection Signals

### 1. Response Headers
```
X-Powered-By: Sails <sailsjs.com>
```
Always present. If you see this, the backend is Sails.js.

### 2. HTML Source — SAILS_LOCALS
Every page served by Sails embeds a `<script>` block containing:
```javascript
window.SAILS_LOCALS = {
  _environment: unescape('development'),
  // ...
};
```
If `_environment` is `'development'`, the server is running in **development mode**, which:
- Enables Sails blueprint API (auto CRUD routes for every model)
- Shows verbose error pages
- Exposes debug endpoints
- May enable `/csrfToken`, `/routes`, `/_config` debug endpoints

### 3. Session Cookie
```
Set-Cookie: sails.sid=s%3A[...signature]; Path=/; HttpOnly
```
Sails uses signed session cookies via `connect-session`.

### 4. WebSocket — Socket.io
Sails.js always mounts socket.io at the default path. Test:
```bash
# Probe socket.io transport
curl -s "https://target/socket.io/?EIO=4&transport=polling"
# Response: {"code":0,"message":"Transport unknown"} → socket.io detected
```

### 5. Static Assets — sails.io.js
Check for the Sails WebSocket client library:
```bash
curl -sI "https://target/dependencies/sails.io.js"
# 200 OK → Sails app with default asset pipeline
```

## API Endpoint Probing Checklist

After detecting Sails.js, probe these endpoints systematically:

```bash
# 1. Health/status endpoint — often leaks info
curl https://target/api/health
# May leak: environment, memory, DB status, Redis, uptime, version

# 2. CSRF token endpoint (dev mode only)
curl https://target/csrfToken
curl https://target/getCSRFToken

# 3. Blueprint API — auto CRUD routes (dev mode)
# Sails creates GET/POST/PUT/DELETE for every model
# Probe common model names:
for model in user account wallet trade order position pool token transaction admin setting notification kyc referral reward config api integration; do
  echo "GET /${model}: $(curl -so /dev/null -w '%{http_code}' https://target/${model})"
done

# 4. Development debug endpoints
curl https://target/_config
curl https://target/routes
curl https://target/sails/info
curl https://target/sails/routes

# 5. Standard API paths (Sails commonly uses /api prefix)
for path in /api/tokens /api/health /api/leaderboard /api/user /api/account /api/wallet; do
  echo "${path}: $(curl -so /dev/null -w '%{http_code}' https://target${path})"
done
```

## Known Sails.js Leak Patterns

### Pattern A: `/api/health` Info Disclosure
Returns JSON with:
```json
{
  "status": "healthy",
  "environment": "development",
  "memory": { "rss": 696913920, "heapTotal": 594382848, "heapUsed": 404425592 },
  "database": "connected",
  "redis": "connected",
  "uptime": 11129.746,
  "version": "0.0.0.1"
}
```
**Severity**: Medium. Leaks deployment mode, memory pressure, DB type, infrastructure metadata.

### Pattern B: Docker Internal IP Leak
```
X-Server-IP: 172.17.0.2
```
Sails behind ELB leaks the internal Docker container IP in response headers.
**Severity**: Low-Medium. Helps attacker map internal network topology.

### Pattern C: CORS Misconfig
```
Access-Control-Allow-Origin: *
Access-Control-Expose-Headers: Content-Type, Authorization, os, version, sign, language, timezone, embedded, lang, recaptcha, dtoken
```
**Severity**: Medium. Any site can make cross-origin requests with credentials (if `Access-Control-Allow-Credentials: true` is also present).

### Pattern D: User Enumeration via Error Messages
Login form differentiates between:
- "The credentials you entered are not associated with an account" → email not registered
- Generic error → email exists but password wrong
**Severity**: Low-Medium. Enables email enumeration for phishing or credential stuffing.

### Pattern E: Exposed Ex-Headers in CORS
The `Access-Control-Expose-Headers` lists custom headers the server accepts:
- `os`, `version`, `sign`, `language`, `timezone`, `embedded`, `lang`, `recaptcha`, `dtoken`
These reveal the client SDK expects signed requests with auth headers (`sign`, `dtoken`, `recaptcha`).

## Next.js + Sails.js Hybrid Probing

When the frontend is Next.js and backend is Sails.js (separate subdomains):

### Next.js Build Manifest — Find API Rewrites
```bash
# Extract buildId from HTML source, then load manifest:
BUILD_ID=$(curl -s https://frontend.com | grep -oP 'buildId:"[^"]+"' | cut -d'"' -f2)
curl -s "https://frontend.com/_next/static/${BUILD_ID}/_buildManifest.js"
# Look for rewrites/destinations containing API paths
# Example: /api/hyperliquid/:path* → Hyperliquid API proxy
```

### Cross-Subdomain Consistency Check
- Frontend CSP `connect-src` directive lists every API endpoint the app talks to
- Check CSP for hidden subdomains: `*.ak47.ai`, `*.blockrazor.xyz`, `*.privy.io`, etc.
- These are third-party integrations that may have their own bugs
 
## Cloud Backend Detection (Huawei Cloud Specific)

Headers from Huawei Cloud OBS (Object Storage Service):
```
Server: openresty
CloudServiceDiscount: CDN
x-obs-bucket-location: ap-southeast-3
x-obs-storage-class: STANDARD
x-obs-az-redundancy: 3az
x-ccdn-cachettl: 2592000
```
Useful for finding bucket misconfigs, especially if static assets serve user content.

## Severity Calibration for Sails.js Findings

| Finding | Typical Severity | Why |
|---|---|---|
| Dev mode (`_environment`) | Medium | Gives attacker roadmap (blueprint routes, verbose errors) |
| `/api/health` info leak | Medium | Memory/DB/Redis topology data |
| CORS wildcard + custom headers | Medium | Enables CSRF-style attacks |
| User enumeration in login | Low-Medium | Depends on PII sensitivity |
| Docker IP leak | Low | Internal infra mapping |
| Socket.io without auth | High | Real-time data access via RPC |
| Blueprint API accessible | High-Critical | Full CRUD on all models without auth |