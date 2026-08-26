# Rust Ecash/Credential Issuance Audit Notes

Use this reference when auditing Rust ecash, credential proxy, blinded-signature, or async credential issuance flows across axum services, shared crates, and wasm client helpers.

## Entry Points to Map

- Issuance creation: synchronous `POST /obtain`, async `POST /obtain-async`, signer `POST /blind-sign`, or any handler constructing a blinded signing request.
- Result retrieval: `GET /shares/{id}`, `GET /device/{device_id}/credential/{credential_id}`, webhook delivery, polling APIs, and any client/wasm wrapper that stores retrieval identifiers.
- Signer-side replay gates: `already_issued(deposit_id)`, deposit validation, storage uniqueness, and whether replay returns a previously issued blinded share before proving ownership of the deposit.
- Background issuance: queued rows, status updates, spawned tasks, webhooks, and retry paths that may run after the HTTP request returns.

## High-Signal Checks

- Per-user retrieval proof: if async creation accepts a `secret`, `device_id`, `credential_id`, wallet key, or public key, ensure result retrieval requires the same secret or a caller-scoped principal. A global service bearer plus integer `id` or caller-supplied identifiers is not per-user ownership.
- Replay/double issuance: verify both code and migrations enforce uniqueness/idempotency for `(device_id, credential_id)`, deposit IDs, request UUIDs, and signer node IDs. Do not trust comments or OpenAPI `409` docs; check the final migration state.
- Migration regressions: watch for `DROP TABLE`/recreate migrations that silently lose indexes. Search all migrations for the original unique index and confirm it is recreated after every table rebuild.
- Status corruption with duplicates: if uniqueness is absent, `UPDATE ... WHERE device_id = ? AND credential_id = ?` updates multiple rows and retrieval joins may mix shares from several deposits/credentials.
- Signer replay leakage: if `already_issued(deposit_id)` returns a stored blinded signature before validating the current request, only report as credential theft if the returned material is actually usable by the attacker; blinded shares may be cross-user disclosure without unblinding capability.

## Logging Checks

- Auth middleware must never log raw `Authorization` headers or parsed bearer tokens, even at debug/trace level.
- Blind-sign request bodies often include user-linking material: withdrawal request, deposit ID, deposit ownership signature, ecash public key, expiration, and ticketbook type. Treat full request-body trace logs as sensitive even if blinding openings are absent.
- Webhook code should not log request payloads, response bodies containing secrets, or bearer secrets in formatted client/debug output.

## Reporting Shape

For concrete findings, include file/line evidence for all three layers:

- Route exposure/auth: where the endpoint is mounted and which middleware applies.
- Missing proof/idempotency: handler/model/storage code showing no per-user secret check or no uniqueness conflict handling.
- Impact sink: DB insert/update, deposit consumption, signer request, response construction, or webhook payload that leaks or issues credential material.

## Rejection Discipline

- Reject generic `weak auth` if a route has a single bearer but no multi-user threat model or sensitive cross-tenant data path.
- Reject double-issuance claims when a DB primary key/unique index and conflict handling prove idempotency in the final schema.
- Reject log-leak claims for public verification keys, aggregated signatures, or intentionally public epoch data.