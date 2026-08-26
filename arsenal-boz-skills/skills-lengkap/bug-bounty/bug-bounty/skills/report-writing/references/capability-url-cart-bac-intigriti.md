# Capability-URL / GUID-only cart BAC — Intigriti packaging

For anonymous OCC/SAP Commerce (and similar) carts authorized **only by cart GUID**.

## One report, one root cause

Merge into a **single** High BAC/IDOR report (do **not** split):

| Proven surface | Include as |
|----------------|------------|
| Unauth GET cart → guest email (`user.uid`) | Core impact |
| Unauth POST delivery/billing address | Integrity / parcel diversion |
| Unauth entries add/remove + DELETE cart | Tamper + checkout DoS |
| Unauth POST `.../paymentdetails` 201 | Same GUID capability |
| Unauth GET `?fields=paymentInfo(FULL)` → masked PAN/holder/expiry | Payment metadata (not full PAN) |
| Unauth `POST .../orders?cartId={guid}` → **400 validation, never 401/403** | Supporting note only |

## Honest limits block (required in report body)

Always include a short **Honest limits** section:

- UUID v4 → not brute-forceable; needs secondary GUID leak (XSS, shared device, logs, support, third-party script, etc.)
- Full PAN **not** returned if server masks
- **Do not claim free order / T&C bypass** unless placeOrder returns 200/201 paid goods without Adyen/payment
- placeOrder without session is severity **argument** for missing authz, not a separate Critical free-order finding
- Analytics/RUM GUID sightings (e.g. Datadog) = secondary narrative only, not standalone leak finding unless third-party read is proven
- Cross-brand: same stack → de-dupe one report; cart isolation across brands is **good**, not a finding

## CVSS self-score pattern

Optimistic package (GUID + R/W PII + state change):

`CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L` ≈ **7.5 High**

- AC:H = needs GUID (never claim Low to inflate)
- **Adversarial triage often lands Medium** (single-object capability URL, no mass enum, no free order, no full PAN, Hybris guest-cart-by-design defense). Safer self-submit: **Medium**, or High only if program explicitly pays High for checkout BOLA without mass GUID leak.
- Safer alternate vector if C/I contested: `…/C:L/I:L/A:L` or `…/C:L/I:H/A:L` (~5–6.x Medium)
- If user already submitted Medium → do not re-open severity debate; focus on retest/triager replies only

## Evidence set (min)

1. `poc_attacker_read.json` — unauth GET + email
2. `poc_attacker_addr.json` — address overwrite 201
3. `poc_paymentdetails_*.json` — 201 masked card
4. `poc_paymentinfo_*.json` or cart GET with `paymentInfo(FULL)`

Reproduce with `credentials: "omit"` (or no cookies) from a second context. Document exact host + baseSite (`kvn-spa` / `kvb-spa` / `kvtp`).

## Title formula (worked)

Long (docs / disk report):
```
Unauthenticated broken object-level authorization on anonymous OCC carts (GUID-only R/W of guest checkout data)
```

**Short titles for Intigriti form char limit** (offer these first when user complains about length):
```
Unauth GUID-only cart IDOR allows unauth R/W of guest checkout data
Broken authz on anonymous OCC carts — unauth R/W by cart GUID
IDOR on /users/anonymous/carts/{guid} — unauth guest cart R/W
```

## Impact paste shape (NO MARKDOWN TABLES — hard user pref)

Intigriti Description paste: **bullets / short paragraphs only** for Impact.
Pipe `|` Markdown tables **scramble on paste** (user: *"jangan bentuk tabel, berantakan pas di paste"*).
Keep severity / comparison tables only in local `submission-notes.md`, never in paste-ready Impact.

If packaging and user complains about tables → rewrite Impact to bullets **immediately**, do not re-ship table form.

```markdown
## Impact

With only knowledge of the cart GUID (no cookies, no Authorization), an unauthenticated attacker can:

- Disclose guest email (`user.uid`) via unauth cart GET
- Read full cart contents and pricing
- Silently overwrite delivery address (201) → parcel diversion if victim pays
- Overwrite billing address (201)
- Read payment metadata via paymentInfo(FULL): masked PAN, holder, expiry, billing (200)
- Set paymentdetails / payment mode unauthenticated
- Delete the victim cart (200) → checkout DoS
- Call placeOrder without session — 400 validation only, never 401/403
- Same root cause across listed Tier-1 brands (one report)

### Honest limits
- UUID v4 — not brute-forceable; needs secondary GUID leak (not claimed standalone)
- Full PAN not returned if masked
- Free order / T&C bypass / completed order without Adyen not claimed
```

## CVSS calculator UI picks (capability-URL cart BAC)

| Metric | Pick | Why |
|--------|------|-----|
| AV | Network | remote API |
| AC | **High** | needs GUID (do not pick Low to inflate score) |
| PR | None | unauth guest |
| UI | None | attacker hits API; no victim click in exploit path |
| S | Unchanged | same cart/checkout resource |
| C | High | email + address + payment metadata |
| I | High | address/cart/paymentdetails overwrite |
| A | Low | cart delete only, not service-wide |

Vector: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L` ≈ 7.5 High

## Tier / scope type (AS Watson–style programs)

| Question | Answer for this bug class |
|----------|---------------------------|
| Tier? | **Tier 1** e-com main (`api.*`, `www.*` listed assets) |
| Scope type? | **URL** (explicit asset), **not** Tier-5 wildcard `*.domain` |
| Multi-brand | One report; primary asset = main API host; sister brands in body |

## Video PoC (when form says mandatory)

Record 2–4 min: (1) victim creates cart + email + address, show GUID (2) attacker incognito / no cookies (3) GET 200 email → POST delivery 201 → POST paymentdetails 201 → GET paymentInfo 200 → optional DELETE 200 (4) say on-screen: no free-order claim. Attach mp4/Loom → only then answer **Yes** to video question.

## PASTE_FIELDS.txt skeleton

```
TITLE: ...
SEVERITY: High
ASSET: https://api.example.com (+ sister brands, one root cause)
ENDPOINT: GET/POST/DELETE .../users/anonymous/carts/{guid} + sub-resources
PROOF ONE-LINERS:
1) GET cart → 200 user.uid=...
2) POST delivery → 201
3) POST paymentdetails → 201 ************1111
4) GET fields=paymentInfo(FULL) → 200
5) DELETE cart → 200
6) POST orders?cartId= → 400 validation only (not 401)
DO NOT CLAIM: free order, full PAN, UUID brute, analytics standalone
```

## User workflow note

If mid-hunt user says **submit dulu** → package this finding first; defer T&C reverse / register / XSS GUID leak until after package delivery.
