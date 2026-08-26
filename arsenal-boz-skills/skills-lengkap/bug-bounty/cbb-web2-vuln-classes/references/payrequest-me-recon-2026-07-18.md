# PayRequest.me recon notes (2026-07-18)

**Target:** `https://payrequest.me/` (+ `payrequest.app`, `payrequest.io`)  
**Stack:** Laravel + Livewire + Flux · Cloudflare · nginx origin · Stripe/Mollie/PayPal/MoonPay · EVM Base + Solana · x402  
**Critical verified this session:** none → **no formal report** (BOZ gate)

## Quick map

```text
/{handle}                              public payment page
/{handle}/payments.txt                 x402 manifest (IBAN/EVM/Sol by design)
/api/v1/x402/{handle}                  discovery JSON
POST /api/v1/x402/{handle}/pay         402 payment_required (amount body ignored)
POST /{handle}/pay                     fiat create → iDEAL/Mollie redirect HTML
POST /{handle}/crypto/initiate         JSON → invoice_id sequential + to_address
GET  /{handle}/crypto/status?invoice_id=N   UNAUTH status (cross-handle)
POST /{handle}/crypto/submit           {invoice_id,tx_hash,from_address}
POST /{handle}/crypto/abort            {invoice_id,message}
POST /{handle}/solana/initiate         needs from_address
POST /{handle}/solana/submit
GET  /{handle}/solana/status?invoice_id=
POST /{handle}/manual-payment/confirm  {platform,amount,currency,...}
POST /{handle}/customer/login          magic link customer ("ok":true)
POST /webhooks/mollie                  form id=… vs JSON id
POST /webhooks/paypal                  401 invalid signature
POST /register                         password+confirm → 302 dashboard (Turnstile often not enforced CLI)
/{handle}/crypto/wallet-assets?address=
/{handle}/solana/usdc-balance?address=
/login/wallet/nonce|verify|register
/csrf-token                            JSON csrf
/marketplace                           public products (?product=N sequential)
```

## Sister hosts

| Host | Role |
|------|------|
| payrequest.me | Public payment links · crypto initiate/status |
| payrequest.app | App session · onboarding · /invoices /products /customers /settings |
| payrequest.io | Marketing |
| dashboard.payrequest.io | Dashboard |
| media.payrequest.nl / assets.payreque.st | Media CDN |

## Session facts (tool-backed only)

### Hardened / fail exploit

| Observation | Result |
|-------------|--------|
| Livewire snapshot tamper `userId` | **419** checksum |
| amount 0 / negative on free pay | **422** min 0.01 |
| **Product price override** (`product_id=2093` list €5, client `amount=0.01`) | Mollie checkout still **€5.00** — server enforces list price |
| x402 pay without payment / amount override | **402** · accepts amount stays `"1000"` |
| Fake crypto `tx_hash` submit | `pending_confirmation` · **invoice_status stays pending** (no free paid) |
| App authed `GET /invoices/14145` | **403** (sample) |
| storage listing | **403** |
| sk_live/whsec in main JS | not found |
| Freename/claim PUT unauth | **401** |

### Signals (not critical without impact chain)

| Observation | Result |
|-------------|--------|
| `POST /{h}/crypto/initiate` | Unauth+CSRF → sequential `invoice_id` (e.g. 14137–14146) + custody `to_address` |
| `GET /{h}/crypto/status?invoice_id=N` | **Unauth** · works **cross-handle** · fields: status, tx_hash, explorer_url, invoice_status only (no payer/amount leak in sample) |
| Mollie form webhook `id=tr_fake` | **200** `{"status":"processing_in_progress"}` · JSON same id → **404** Transaction not found · **no proof** marks paid |
| Register free CLI without Turnstile token | **302** onboarding · `api/landing-status` `loggedIn:true` on app |
| `manual-payment/confirm` platform=wire | **200** pending merchant verify (not auto-credit) |
| payments.txt IBAN/wallets | public by design |
| wallet-assets any 0x | Base balances (chain read-proxy) |
| laravel_session | HttpOnly Secure **SameSite=None** |

### Auth / app surface (authed free account)

| Path | Note |
|------|------|
| `/onboarding` Livewire | step snapshot: plan free, companyName, salesPageHandle |
| app `/products` `/customers` `/invoices` `/settings` | 200 shell while logged in |
| app `/api/user` | often 401 even when landing-status loggedIn (cookie/API split) |
| `/horizon` | 403 |

## Crypto flow (JS-derived)

```text
initiate → invoice_id, usdc_amount, to_address (custody), merchant_address
wallet pays on-chain
submit {invoice_id, tx_hash, from_address} → pending_confirmation + explorer_url
poll status until completed/paid  (server verifies chain — fake hash does not complete)
abort {invoice_id, message}
```

Solana parallel: `solana/initiate` (from_address required) → `solana/submit` → `solana/status`.

## Fiat create quirks

- Success body is HTML spinner with `const checkoutUrl = "https:\/\/…"` — decode `\/` before curl follow.
- iDEAL Wero page needs JS (curl alone shows enable-JS friction).
- Creditcard → `mollie.com/checkout/credit-card/session/…` — amount visible in HTML (€5 enforced for product).

## Next probes (if seeking critical)

1. Finish Livewire onboarding → claim handle → full dashboard IDOR (invoices/customers/API v1)
2. Real Mollie `tr_*` from live checkout → webhook race / mark-paid spoof
3. `crypto/submit` race vs chain verifier edge cases
4. Solana submit signature spoof
5. Customer magic-link takeover / open redirect
6. SIWE nonce reuse / wallet account linking
7. Webhook Stripe (405/404 variants) · PayPal signature edge

## Do not report as vuln by default

- IBAN/wallet in `payments.txt` / x402 `payTo`
- Unauth status with only pending|tx_hash|explorer (no PII/funds)
- Mollie `processing_in_progress` without paid state change
- Product amount client field when server re-prices

See `honest-bug-bounty-reporting/references/intentional-public-data-not-vuln.md`  
Class pitfalls: `references/payment-link-platform-pitfalls.md`
