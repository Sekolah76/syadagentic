# Authenticated Program Baseline

Use this before authorization, OAuth/SSO, API, or RCE-oriented testing on a bounty program that permits a researcher-owned account.

## 1. Treat program rules as executable preconditions

1. Snapshot the live program page and create `SCOPE_FENCE.md`.
2. Record mandatory traffic identification, account-alias rules, prohibited automation, and data-handling limits.
3. Do not use a personal or third-party account where the program mandates program-issued aliases.

## 2. Secret handling

- Never paste, echo, log, commit, or include a password/OTP/cookie/token in evidence.
- Use a named auth profile whose password is an environment or vault reference.
- Profile creation alone is insufficient: verify only that the reference is available to the *agent process*, without printing its value.
- If an environment variable was added after the gateway started, reload/restart the gateway/service so its process inherits the secret. Re-check presence only.

## 3. Minimal login proof

Perform one controlled login against the researcher-owned account:

1. GET the login page and inspect its actual anti-CSRF mechanism from page/bundle behavior.
2. Mirror the legitimate XSRF cookie/header convention and submit exactly one normal login request.
3. Record status, cookie-presence booleans, and response field names only—never response values.
4. Use one harmless session oracle (for example, the first authenticated redirect or dashboard landing) and record status, host/path with query strings and owned-account IDs redacted.
5. Map the real logout/revocation flow statically before exercising it; a guessed `logout` route returning `404` is neither evidence of a vulnerability nor proof a session is persistent.

## 4. SSO/OAuth interpretation

- A 302 through login/authorize/callback endpoints is often expected. Follow it only inside the owned test session and retain a redacted redirect-chain topology.
- Do not interpret an accepted URI parameter, an OAuth redirect, or a non-default chain/context as a finding until it produces a second-principal session, authorization-code leak, token disclosure, or protected-action confusion.
- Preserve low-signal primitives as chain candidates: origin/URI mismatches, postMessage, callback handling, session rotation, and entitlement reads.

## 5. Next move

Only after this baseline, enumerate owned-resource objects and role boundaries. For RCE research, begin with owned deployment/build/import/webhook/template primitives and use harmless proof commands or callback-only validation; do not run broad automated scanners when program rules prohibit them.
