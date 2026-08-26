# Express / NestJS API Probing

Pattern for probing Express.js and NestJS backends found during web recon.

## Primary Detection

```bash
# Express/NestJS typically returns JSON at root
curl -sI https://target.com/api/something
# Look for: X-Powered-By: Express

# NestJS root endpoint leaks environment info
curl -s "https://target.com/bot-api/" -H "Accept: application/json"
# → {"environment":"production","mode":"production","version":"1.0.0"}
```

## Swagger / OpenAPI Discovery

Express/NestJS apps often expose interactive API docs even in production:

```bash
# Try these paths in order:
curl -s "https://target.com/bot-api/docs"              # Swagger UI HTML
curl -s "https://target.com/bot-api/docs/json"          # OpenAPI JSON spec
curl -s "https://target.com/bot-api/api-docs"           # Alternate path
curl -s "https://target.com/bot-api/swagger.json"       # Swagger 2.0
curl -s "https://target.com/bot-api/openapi.json"       # OpenAPI 3.0
curl -s "https://target.com/bot-api/v2/api-docs"        # SpringDoc
curl -s "https://target.com/bot-api/v3/api-docs"        # OpenAPI 3
```

**Real example (Clore.ai):** `/bot-api/docs/json` exposed 8 endpoints
including `message/send`, `email/send`, `account/link/unlink/info`.

## Root Endpoint Info Disclosure

```bash
# NestJS returns version info at root
curl -s "https://target.com/bot-api/"
# → {"environment":"production","mode":"production","version":"1.0.0"}

# NestJS sub-apps (poh-api, bot-api, etc.) often share same pattern
curl -s "https://target.com/poh-api/"
# → {"environment":"production","mode":"production","version":"1.0.0"}
```

## Common Endpoint Pattern

Express/NestJS apps typically use structured JSON request/response:

```bash
# POST endpoints with JSON body — token in body, NOT in header
curl -X POST "https://target.com/bot-api/message/send" \
  -H "Content-Type: application/json" \
  -d '{"token":"some_token","message":"test"}'
# → {"error":"Permission denied"}  (token validated)
# → {"error":"Internal Server Error"}  (missing dependency)

# All endpoints share same auth pattern:
# /account/link, /account/unlink, /account/info
# /message/send, /email/send
```

**Critical pattern:** Auth token is a **field in the request body**, not a proper
`Authorization` header. If a token can be found/guessed, full API access is open
with no real auth layer.

## Sub-app Structure

NestJS apps often expose multiple sub-applications under different base paths:

```bash
# Typical: /bot-api, /poh-api, /webapi, /service_api, /api/v1
curl -s "https://target.com/{sub-app}/"    # root info
curl -s "https://target.com/{sub-app}/docs"  # swagger
```

## Authentication Bypass Vectors

- **Empty token:** `{"token":""}` — some frameworks treat empty string as "no auth"
- **Skeleton key:** Try `"admin"`, `"test"`, `"root"`, `"token"`, `"api_key"`
- **Numeric token:** `{"token":1}` — type coercion bypass
- **Boolean token:** `{"token":true}` — maybe bypasses `if(!token)` check
- **Null token:** `{"token":null}` — some Node.js ORMs skip auth on null
- **Extra fields:** Some apps ignore the token field altogether if other fields present
- **JWT in token field:** If they forgot to switch from JWT header to body auth

## Error Message Analysis

Different error messages reveal server implementation:

| Error | Meaning |
|-------|---------|
| `"Permission denied"` | Token validated and rejected → endpoint works |
| `"Internal Server Error"` | Token skipped or missing dependency → endpoint partially works |
| `"Route GET:/... not found"` | Wrong HTTP method or path |
| `{"statusCode":404,"error":"Not Found"}` | Standard NestJS 404 |
| `{"message":"Validation failed"}` | Input validation active → try different payload shapes |
| HTML response | SPA fallback, not API → look for real API elsewhere |

## Response Structure

NestJS standard error format:
```json
{"message":"Route GET:/path not found","error":"Not Found","statusCode":404}
```

Standard success format (varies by app):
```json
{"success": true}
{"ok": true}
{"environment":"production","mode":"production","version":"1.0.0"}
```
