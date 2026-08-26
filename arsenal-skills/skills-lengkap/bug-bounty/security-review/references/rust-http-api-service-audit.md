# Rust HTTP/API Service Audit Notes

Use this reference when auditing Rust services built with axum/reqwest/sqlx, especially multi-crate workspaces where route handlers are thin and trust boundaries live in shared libraries.

## Route/Auth Mapping

- Start from router assembly (`Router::new`, `.route`, `.nest`, `.route_layer`, `.layer`) and record which subtrees inherit bearer/signature middleware.
- For axum, middleware order matters: routes added after `.route_layer`/`.layer` may not be protected. Confirm comments with actual construction.
- Map request models separately from handlers. A field like `x25519_noise_key`, `secret`, or `agent_public_key` is not protection unless the handler compares/verifies it.

## High-Signal Checks

- Shared bearer tokens on worker/agent APIs: check whether the token authenticates a class of agents or a specific agent. If specific identity is expected, verify request keys/signatures are bound to stored assignments.
- Assignment workflows: ensure assignment tables store owner identity and result submission checks `(work_id, owner, freshness/nonce)` before accepting results.
- Async result retrieval: if creation includes per-request `secret`, `device_id`, or `credential_id`, retrieval should require the same secret or a caller-scoped principal, not just a global service token plus predictable integer IDs.
- SSRF from node/operator metadata: distinguish direct public fetch endpoints from background scrapers fed by chain/registry data. Report only when exploitability fits the program threat model; otherwise note as rejected/conditional.
- SQL injection in Rust/sqlx: `query!`, `query_as!`, and `.bind()` are usually safe for values. Focus on dynamic SQL strings, identifier/order interpolation, or raw `format!` passed to query execution.

## Reporting Shape

For each concrete finding include:

- File/line refs for route exposure, handler validation, and sink/storage mutation.
- Exploit preconditions (unauthenticated, shared bearer token, registered agent key, bonded node operator, etc.).
- Impact tied to the service purpose (credential material leak, forged monitoring results, contract tx abuse, internal metadata exposure).
- Reproduction approach using endpoint/method/body and expected observable state change.

## Rejection Discipline

Reject weak leads explicitly when asked for an audit: no SQLi if all inputs are bound; no unsafe file handling if no user-controlled path reaches fs; no auth bypass when public routes are intentionally read-only; no SSRF unless attacker-controlled URL/host reaches a server-side client with meaningful network position.