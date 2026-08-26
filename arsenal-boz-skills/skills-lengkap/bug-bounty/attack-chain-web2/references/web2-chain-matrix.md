# Web2 Chain Matrix

| Primitive output | Possible next precondition | Mandatory proof |
|---|---|---|
| User identifier | Object lookup or recovery input | Exact identifier accepted and security-relevant |
| Reset token | Password/session reset endpoint | Purpose, audience, expiry, single-use behavior |
| Auth cookie | Authenticated request | Domain/path/SameSite/binding and server acceptance |
| XSS execution | Privileged browser action | Victim context, CSRF/re-auth, accessible authority |
| SSRF request | Internal endpoint access | Routing, method/headers, response visibility |
| Cloud credential | IAM action | Principal identity, validity, exact allowed action |
| Uploaded file URL | Parser/execution sink | Transformation, delivery origin, handler invocation |
| Cross-tenant object ID | Cross-tenant read/write | Backend ownership check absent on exact action |
| Cacheable response control | Victim influence | Shared cache key, persistence, victim route |
| Race window | Invariant violation | Concurrent schedule attainable and durable result |
