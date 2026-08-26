# Multi-server HTTP surface audit (API + admin + callback)

Class-level playbook for Go/Echo (and similar) services that split **public**, **admin**, and **worker/callback** HTTP listeners. Derived from decentralized-API style audits (transfer→executor proxy, PoC callbacks, compose bind mitigations).

## 0. Surface map first (do not deep-dive handlers yet)

Build a table before writing findings:

| Server | Code bind | Deploy publish | Middleware | Auth in handlers |
|--------|-----------|----------------|------------|------------------|
| Public | `:%port` / host | nginx / host port | logging? auth? | per-route |
| Admin | often `:%admin` = 0.0.0.0 | compose may be `127.0.0.1:port` | often logging only | often **none** |
| ML/callback | `:%ml` | often **world-open** | often logging only | often **none** |
| gRPC node-manager | `:%grpc` | may be unpublished | n/a | check |

**Code anchors (search):**
```bash
rg -n 'e\.Start\(|\.Start\(addr\)|AdminServerPort|PublicServerPort|MLServerPort|Group\("/admin|HTTPErrorHandler|Use\(' path/
rg -n 'ports:|127\.0\.0\.1:|ADMIN|ML_SERVER|PUBLIC_SERVER' deploy/ -g '*.yml' -g '*.yaml'
```

Severity of unauth admin/callback **depends on deploy bind**. Always pair:
- Application: no middleware auth
- Deploy: compose `127.0.0.1:9200:9200` vs `"9100:9100"` public

Frame admin as Critical **if exposed**, Medium as defense-in-depth failure when localhost-only.

## 1. SSRF on participant-controlled / chain-stored URLs

### Registration-time validation ≠ request-time safety

Common pattern: on-chain `InferenceUrl` / webhook URL validated once:

```go
// Anti-pattern: only literal IPs checked
ip := net.ParseIP(host)
if ip != nil && isPrivateIP(ip) { reject }
// DNS names fall through → return nil
```

**Bypass:** register `http://ssrf.attacker.tld` (public A record passes ValidateBasic). At proxy time, DNS (or rebinding) → `127.0.0.1` / `169.254.169.254` / docker bridge.

**Redirect client:** `CheckRedirect → http.ErrUseLastResponse` (`NoRedirectClient`) blocks **follow-up** redirect SSRF only. Does **not** fix initial resolve-to-private. Tests that only cover redirects are incomplete.

### Proxy construction

```go
// Dangerous: string concat path onto untrusted base
http.NewRequest(POST, executor.Url+forwardPath, body)
// Prefer JoinPath + scheme/host allowlist + dialer that pins resolved public IPs
```

Check what headers are forwarded (`Authorization`, signatures, prompt hashes) — header leakage is impact even without metadata RCE.

### Fix bar for findings
- DNS resolve in validator **and** runtime dial guard (reject private after resolve)
- Re-validate URL at selection/proxy time, not only registration
- Document TOCTOU for DNS rebinding

## 2. Admin surfaces without application auth

Typical high-value routes:
- `GET .../config` **unsanitized** (private keys) — contrast any `Sanitize` path that zeros `WorkerPrivateKey`
- `POST .../tx/send` → process signs/broadcasts as node
- Node CRUD, DB export, payload store (test hooks left on), BLS request

**Grep:**
```bash
rg -n 'getConfig|GetConfig\(\)|unsanitized|WorkerPrivateKey|SendTransaction|exportDb|storePayload' path/
```

**Fixes:** bind loopback in **code**, shared secret/mTLS middleware, never return raw config, feature-flag test hooks.

## 3. Unauthenticated worker/callback ports

ML/PoC/webhook listeners often:
- Phase-gate only (`ShouldAccept*`)
- Submit chain msgs **as the node** from attacker-supplied body
- Published publicly in stock compose

Impact: forged fraud flags / weight, fee drain, local store pollution. Network-wide effect may need honest-majority aggregation — still valid **per-node integrity** bug.

**Fixes:** docker-internal or localhost bind; HMAC/mTLS from workers; verify worker key on callback.

## 4. Authz that is usually solid (document as mitigated)

Do not report as bugs without bypass:
- Payload fetch requiring **active participant at inference epoch** + grantee signature + short timestamp window (header epoch forced to inference epoch before sig verify)
- Dual-context AuthKey replay maps (transfer vs executor)
- Developer + transfer signature re-check on executor path

## 5. Economic / estimation footguns (usually Low)

`getPromptTokenEstimation → len(text)` style estimates: flag only with billing impact path and note if chain reconciles later.

## 6. Tooling when large Go files block re-reads

- Prefer single-range `sed -n 'A,Bp'` / `rg -n 'func ...' -A N` over repeated `read_file` on same range (dedup/block risk)
- Batch independent surface maps (server.go + compose + middleware) in one turn
- Write findings only after route→auth map is complete

## 7. Finding card shape

```
Severity + Confidence
Location: path:line (and consumer path:line)
Issue: root cause in one paragraph
Repro: curl or conceptual multi-step
Impact: attacker capability + conditions
Fix: concrete
Mitigations: deploy bind / existing tests (honest)
```

## Related

- SSRF IP bypass tables → `web2-vuln-classes` SSRF section
- Live pentest recon → `web-pentest-toolkit`
- Report tone/severity gates → `report-writing` / `triage-validation`
