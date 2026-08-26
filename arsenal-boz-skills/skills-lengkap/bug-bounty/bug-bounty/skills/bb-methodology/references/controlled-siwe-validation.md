# Controlled SIWE / wallet-auth validation

Use this when a scoped dApp exposes a SIWE-style flow and a real proof requires a signed message. This is a **researcher-owned identity** test only: never use a third-party address, signature, cookie, referral code, or account.

## Preconditions

1. Confirm the program permits authentication testing and no mutation is needed for the hypothesis.
2. Map the frontend's **exact** SIWE construction before testing. Record only non-sensitive fields: domain, URI, statement, chain ID, issued-at/expiry policy, and auth endpoints.
3. Use a fresh random EOA per test run, generated in process memory (e.g. `ethers.Wallet.createRandom()`). Never print, persist, commit, or send its private key.
4. Keep all test output redacted: no raw private key, nonce, signature, SIWE message, session cookie, wallet address, or referral value.

## Minimal replay differential

1. `GET /auth/nonce` with cookie jar A.
2. Build the exact SIWE message used by the frontend and sign it with ephemeral wallet A.
3. `POST /auth/login` from jar A; use `/auth/me` only as a session oracle.
4. From a new, cookie-free jar B, submit the *identical* message and signature once.
5. Query `/auth/me` for jar B.
6. Log out every session created by the test.

Expected secure behavior: initial login and its session oracle succeed; replay is rejected and jar B remains unauthenticated.

A replay of a researcher's own signature is **not** reportable on its own. To become a report, show that an attacker can realistically obtain a victim signature and use it to access or change a victim-scoped function.

## Controlled BOLA differential

Only after separate researcher-owned wallets can authenticate without registering or mutating app state:

- Wallet A requests an object it owns.
- Wallet B requests the same A object using its own fresh session.
- Do not enumerate addresses, register accounts, consume referrals, mint, or create business objects solely to make the test possible.

A cross-account `200` is only a candidate. Stop after the first controlled disclosure and establish whether the disclosed field is non-public and has concrete confidentiality or economic impact. A referral code alone is commonly informational unless it enables reward diversion or a further privilege/data impact.

## Evidence format

Persist only statuses and boolean controls, e.g. `addressMatchesWallet`, `sessionCookieSet`, `responseContainsRefCode`. Hash the redacted result artifact. Keep the test script separate from program source, mark it researcher-only, and destroy/logout sessions at the end.

## Common false positives

- Public nonce issuance.
- Successful login for the wallet that created the signature.
- Browser/client-side referral format validation.
- Public GraphQL, CORS, route discovery, or frontend API URLs.
- A user-controlled own-session replay with no victim acquisition or impact.
- `403` on unregistered test wallets: this is only an unregistered control, not proof of registered-object authorization.
