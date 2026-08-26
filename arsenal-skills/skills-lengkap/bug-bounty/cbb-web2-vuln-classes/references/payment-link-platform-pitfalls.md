# Payment-link / x402 platform pitfalls (class)

From PayRequest.me combat 2026-07-18. Applies to Laravel+Livewire creator payment pages, multi-rail checkout (Mollie/iDEAL/Stripe), crypto custody invoices, x402 manifests.

## By-design public (not vuln alone)

| Surface | Notes |
|---------|-------|
| `/{handle}/payments.txt` | IBAN / EVM / Solana — merchant rails |
| `GET /api/v1/x402/{handle}` | Discovery; `accepts[].payTo` public |
| `POST …/x402/…/pay` → 402 | Payment required; body amount often ignored |
| Marketplace products | Public catalog · sequential `product_id` |
| `wallet-assets?address=` | Chain balance proxy for any addr |
| Crypto `to_address` on initiate | Custody/deposit addr for that invoice — not secret key |

Finding only after **misuse**: dashboard IDOR, free digital goods, webhook forge → paid, payment hijack, auth bypass.

## Probe order (efficient)

```text
1. Public handle + payments.txt + x402 discovery
2. POST /{h}/pay fiat (ideal/creditcard) → decode checkoutUrl (unescape \/)
3. Product price: client amount=0.01 vs list price → read provider checkout HTML amount
4. POST /{h}/crypto/initiate → sequential invoice_id
5. GET  /{h}/crypto/status?invoice_id=N unauth + cross-handle
6. POST /{h}/crypto/submit fake tx → must NOT reach invoice_status=paid
7. Webhooks: form vs JSON Content-Type matrix (Mollie often differs)
8. Register/onboarding → authed /invoices/{id} IDOR
9. manual-payment/confirm platforms (wire/binancepay/…)
```

## Hardening patterns already seen

| Probe | Typical result |
|-------|----------------|
| Livewire snapshot `userId` tamper | **419** checksum |
| amount 0 / negative free pay | **422** min floor |
| **Product `amount` client override** | Server uses catalog price (Mollie shows list €) |
| Fake invoice_id missing crypto row | **404** |
| Fake on-chain submit | `pending_confirmation` only · not paid |
| Storage listing | **403** |
| sk_live/whsec in main JS | often absent |
| App `GET /invoices/{foreign}` | **403** when authz holds |

## High-value signals (need impact before severity)

| Signal | Why not auto-CRITICAL |
|--------|------------------------|
| Unauth sequential `crypto/status` | Often status/tx/explorer only — no amount/payer; free goods unproven |
| Cross-handle status same ID | Same as above unless paid mark / PII |
| Mollie form webhook 200 `processing_in_progress` on garbage `id` | Async accept ≠ mark paid — prove invoice paid / goods delivered |
| Register without Turnstile in CLI | Weak bot friction — not fund loss alone |
| Customer magic-link `ok:true` for any email | Need link leak / host header / open redirect |

## Economic / report gate (SYADAGENTIC)

```text
profit = stolen_value - attack_cost
paid spoof / free product → measure real credit or download unlock
status leak pending only → usually INFO/LOW or discard
no CRITICAL verified → no formal report
```

## JS asset tips

- Search app bundle for: `crypto/initiate`, `crypto/submit`, `solana/initiate`, `manual-payment/confirm`, `checkoutUrl`
- Idempotency: `pay_{timestamp}_{random}` pattern in page JS
- Product field: hidden `product_id` + `amount` — always retest server price on provider page

## Live notes

`references/payrequest-me-recon-2026-07-18.md`  
Public rails: `honest-bug-bounty-reporting/references/intentional-public-data-not-vuln.md`
