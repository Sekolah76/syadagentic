---
name: triage-validation
description: Finding validation before writing any report — 7-Question Gate (all 7 questions), 4 pre-submission gates, always-rejected list, conditionally valid with chain table, CVSS 3.1 quick reference, severity decision guide, report title formula, 60-second pre-submit checklist. Use BEFORE writing any report. One wrong answer = kill the finding and move on. Saves N/A ratio.
---

# TRIAGE & VALIDATION

One wrong answer = STOP. Kill it. Move on.

> "N/A hurts your validity ratio. Informative is neutral. Only submit what passes all 7 questions."

---

## THE 7-QUESTION GATE

Ask IN ORDER. One wrong answer = STOP immediately.

---

### Q1: Can an attacker use this RIGHT NOW, step by step?

Complete this template:
```
1. Setup:   I need [own account / another user's ID / no account]
2. Request: [exact HTTP method, URL, headers, body — copy-paste ready]
3. Result:  I can [read / modify / delete] [exact data shown in response]
4. Impact:  The real-world consequence is [account takeover / PII read / money stolen]
5. Cost:    Time: [X minutes], Capital: [$0 / $X subscription required]
```

**If you CANNOT write step 2 as a real HTTP request → KILL IT.**

#### Capability-URL / GUID-only objects (anonymous carts, guest orders, share tokens)

When the object ID is a **UUID** and unauth R/W is proven (`credentials: omit`):

| Claim | Gate |
|-------|------|
| Unauth GET leaks guest email / cart contents by GUID | Survives Q1 if HTTP 200 + body proof |
| Unauth overwrite delivery address / DELETE cart | Survives — state change without session binding |
| Unauth POST paymentdetails 201 + GET paymentInfo (masked PAN/holder/expiry) | Survives — **same root cause** as cart GUID BAC; **merge** into one report, do not open a second ticket |
| Unauth `POST .../orders?cartId={guid}` returns **400 validation** (T&C/slot/address), never 401/403 | Survives as **supporting severity note only** — proves missing authz on placeOrder surface |
| Free order / paid goods without payment / T&C bypass | **Kill** unless placeOrder (or payment capture) succeeds end-to-end without victim payment — SPA `termsChecked` query often still server-rejected |
| "Mass customer dump" / "anyone's cart" | **Kill unless** GUID enumerable or you prove a leak primitive |
| Analytics/RUM (e.g. Datadog) sees cart GUID in browser → vendor | Secondary narrative only — **kill standalone** without proof third parties/attackers can read that data |
| Severity High vs Medium | **Default ship Medium** when UUID-only + single cart + no free order + no full PAN. High only if program critical scenarios (mass PII / free product) are met OR policy explicitly pays High for checkout BOLA. Optimistic self-score 7.5 AC:H often gets triaged to Medium — document entropy, do not claim brute-force |
| Hybris/OCC "guest cart by design" | Soft kill risk (Informative/N/A). Survive by centering **state-changing** ops (delivery overwrite, DELETE, paymentdetails) not mere read-by-token |
| Video PoC mandatory on form | **Process FAIL** until video attached — technical HTTP proof ≠ form Yes |

**Adversarial self-review (assume report wrong)** before submit for this class:

1. Kill free-order / full PAN / mass dump / UUID brute claims
2. Prefer **Medium** framing over High if Likelihood = secondary GUID disclosure
3. Prove **two contexts** (victim email ≠ attacker; empty cookie jar) — own-cart PoC dies on Q8
4. Drop OOS token-leak-to-third-party (RUM) as primary impact
5. One multi-brand report only

**Do not kill** solely because "attacker must know the GUID." Capability URL without binding cookie/HMAC is still broken object-level authorization. **Do kill** inflated impact that implies brute-forcing UUID v4, free-order without proof, or full PAN when only masked.

**Shared OCC multi-brand** (same Hybris stack, different baseSite): one finding, list all in-scope hosts; isolation of GUIDs across brands is expected, not a separate positive finding.

**Submit priority:** if user says **submit dulu**, freeze further T&C/register/XSS chains and package the validated GUID BAC first (see `report-writing` Intigriti submit package + `references/capability-url-cart-bac-intigriti.md`). After user says **submitted Medium** + **skip to other bounty** → cancel residual todos on that target; do not re-open High debate.

---

### Q2: Is the impact on the program's accepted impact list?

Go to the program page. Find "Vulnerability Types" or "Out of Scope."

Common tiers:
- **Critical**: Any-user ATO without interaction, RCE, SQLi with data exfil, admin auth bypass
- **High**: Mass PII exfil, privilege escalation, internal SSRF with data, stored XSS all users
- **Medium**: IDOR on specific user non-critical data, XSS on sensitive page requiring click
- **Low**: Non-sensitive info disclosure, clickjacking with PoC

**If your bug maps to a listed exclusion → KILL IT.**

#### Network-perspective programs (L1 / validator / "network safety")

Some programs score **Risk = Impact × Likelihood** with **Impact from a network perspective**. High/Critical need **network-wide** effects (halt, module theft, wrong rewards for all, full network control). Issues affecting **only one participant/node** usually **cap at Low or Medium**.

| Claim | Typical max under network bar |
|-------|-------------------------------|
| Unauth admin on one join node / secret leak on one host | **Medium** |
| Forge **this node's** vote / first-write-wins single validator | **Medium** |
| DNS SSRF requiring selected executor | **Medium** (High only if proven sensitive network-wide effect) |
| Wrong rewards for all / chain halt | High/Critical |

Do **not** promote single-node full compromise to High just because secrets + re-sign are scary. Read the program formula first (see `report-writing/references/network-perspective-severity.md`).

---

### Q3: Is the root cause in an in-scope asset?

Confirm:
- Vulnerable domain is on the in-scope list (not `*.internal.target.com`)
- It's a production asset (not staging/dev unless explicitly in scope)
- It's not a third-party service the company just uses (not Stripe, Salesforce, Google Auth)

**If out-of-scope → KILL IT.**

---

### Q4: Does it require privileged access that an attacker can't realistically get?

- "Admin can do X" = centralization risk = **KILL IT** (on 99% of programs)
- "Non-admin can do X that only admin should do" = valid
- "Requires physical access / MFA device" = usually invalid
- "Requires compromised victim account to work" = questionable, low severity at best

---

### Q5: Is this already known or accepted behavior?

Search:
1. Program's HackerOne/Bugcrowd disclosed reports: Ctrl+F endpoint name + bug class
2. GitHub issues on target repo: `is:issue label:security ENDPOINT_NAME`
3. Changelog/CHANGELOG.md — does it mention this behavior?
4. API docs / design docs — is it documented as intended?

**If acknowledged/design decision → KILL IT.**

---

### Q6: Can you prove impact beyond "technically possible"?

- XSS → show actual cookie theft or session hijack, not just `alert(1)` or `alert(document.domain)`
- SSRF → hit an internal endpoint that returns data, not just DNS ping
- SQLi → show actual data exfil from a real table, not just error message
- IDOR → show actual other-user's data in response, not just a 200 status code

**If you can only show "technically possible" → DOWNGRADE severity, not kill.**

---

### Q7: Is this a known-invalid bug class?

Check the NEVER SUBMIT list below. If it's on this list without a chain → **KILL IT.**

---

### Q8: Identity check — which session found this, and does it survive?

For any finding made under an authenticated hunt, record the answer to each:

```
1. Session ID:        [12-char BBHUNT_SESSION_ID hash from audit.jsonl]
2. Identity:          [low-priv user A / high-priv user B / API key / etc.]
3. Anonymous repro:   Does the same request work with NO auth header?
4. Cross-identity:    Does it work under session B with the same data scope?
5. Stale-cred repro:  Does a logged-out / expired session still get the data?
```

Why this matters:
- **IDOR / BOLA**: must work with session A reading session B's data — if it
  only works with no auth, that's "missing auth" not IDOR (different bug,
  different severity).
- **Priv-esc**: must work with low-priv session reading high-priv data — if
  both sessions can already see it, no bug.
- **Auth bypass**: must work *without* a valid session — if it stops working
  when you log out, you've found a permissions issue, not a bypass.
- **Always check both directions**: a finding that only reproduces under
  one identity is often a real, scoped permission boundary, not a vuln.

`audit.jsonl` entries are tagged with `session_id`. Re-run the request
under each identity and confirm the bug holds before writing the report.
This is the most common reason "confirmed IDOR" findings come back as N/A.

If you cannot answer the identity questions, treat the finding as unproven.
Blank answers auto-fail on auth-related findings.

---

### Q9: Deployment-Time / Setup-Only Window Check

If a vulnerability relies on a race condition or access-control bypass that occurs **strictly during the deployment or setup phase** of a contract/system (e.g. frontrunning initializers on a contract deployed without an atomic factory):

```
1. Live Status:       Is the contract already initialized on-chain?
2. Post-Setup:        Does the vulnerability persist after setup is complete?
3. Attacker Action:   Does the exploit require timing a setup transaction?
```

- **If the contract/system is already initialized/configured on-chain:** The live impact is zero. An attacker cannot exploit it on the running target.
- **If the vulnerability is setup-only and has closed:** It is a **Low/Informational** design defect. It does not warrant a High/Critical submission.
- **Decision Rule:** Kill the finding for the active target if the setup window has already closed. Document only as informational code quality feedback.

---

---

## 4 PRE-SUBMISSION GATES

Run in sequence. ALL 4 must PASS.

### Gate 0: Reality Check (30 seconds)
```
[ ] Bug is REAL — confirmed with actual HTTP requests, not code reading alone
[ ] Bug is IN SCOPE — checked program scope page explicitly
[ ] Reproducible from scratch — can reproduce starting from fresh session
[ ] Evidence ready — screenshot, response body, or video
```

### Gate 1: Impact Validation (2 minutes)
```
[ ] Can answer: "What can attacker DO that they couldn't before?"
[ ] Answer is more than "see non-sensitive data" (unless program pays for info disclosure)
[ ] Real victim: another user's data, company's data, financial loss
[ ] Not relying on victim doing something unlikely
```

### Gate 2: Deduplication Check (5 minutes)
```
[ ] Searched HackerOne Hacktivity for this program + similar bug title/endpoint
[ ] Searched GitHub issues for target repo
[ ] Read most recent 5 disclosed reports for this program
[ ] Not a "known issue" in their changelog or public docs
[ ] Google: "TARGET_NAME ENDPOINT_NAME bug bounty"
```

### Gate 3: Report Quality (10 minutes)
```
[ ] Title: [Bug Class] in [Endpoint] allows [actor] to [impact]
[ ] Steps to Reproduce: copy-pasteable HTTP request
[ ] Evidence: screenshot/video of actual impact (not just 200 status)
[ ] Severity: matches CVSS 3.1 score AND program's severity definitions
[ ] Remediation: 1-2 sentences of concrete fix
[ ] NEVER used "could potentially" or "may allow"
```

---

## NEVER SUBMIT LIST

Submitting these destroys your validity ratio.

```
Missing CSP / HSTS / security headers
Missing SPF / DKIM / DMARC
GraphQL introspection alone (no auth bypass, no IDOR demonstrated)
Banner / version disclosure without working CVE exploit
Clickjacking on non-sensitive pages (no sensitive action PoC)
Tabnabbing
CSV injection (no actual code execution shown)
CORS wildcard (*) without credential exfil proof of concept
Logout CSRF
Self-XSS (only exploits own account)
Open redirect alone (no ATO or OAuth theft chain)
OAuth client_secret in mobile app (known, expected)
SSRF DNS callback only (no internal service access or data)
Host header injection alone (no password reset poisoning PoC)
Rate limit on non-critical forms (search, contact, login with Cloudflare)
Session not invalidated on logout
Concurrent sessions
Internal IP in error message
Mixed content
SSL weak ciphers
Missing HttpOnly / Secure cookie flags alone
Broken external links
Autocomplete on password fields
Pre-account takeover (usually — very specific conditions required)
Web3: "Open RPC proxy" on testnet endpoints (standard dApp architecture)
Web3: VUE_APP_*/NEXT_PUBLIC_*/REACT_APP_* env vars in JS bundle (client config by design)
Web3: CORS * on API with token-based auth (no credential forwarding possible)
Web3: WalletConnect Project ID "leaked" in frontend (public identifier by design)
Web3: "No rate limiting on RPC" when upstream provider handles limits
Web3: "Missing Authentication Token" on AWS API Gateway (means route not found, NOT auth missing)
```

---

## COMMON N/A CLASSES — KILL SIGNALS

These pass basic gut-check but consistently come back N/A. Each row has a **specific signal** that tells you to kill it *before* writing the report.

| Finding | Why it N/As | Kill signal — if you see this, stop |
|---|---|---|
| Reflected XSS | CSP blocks execution; sandbox context; no session access | Dalfox found `alert(1)` but no cookie in response; `Content-Security-Policy` header present |
| SSRF — DNS callback only | No internal data reached; programs require HTTP response with data | Interactsh/Collaborator got DNS ping but no HTTP reply with internal content |
| IDOR — own data only | Attacker == victim; no cross-account access proven | User ID in response matches your own test account |
| SQLi — error message only | WAF filtered or error is cosmetic; no data exfiltrated | Got DB error string but no actual table rows returned |
| CORS wildcard `*` | `*` blocks `withCredentials`; no PII actually exfiltrated | `Access-Control-Allow-Credentials: true` absent; credentialed request returns 403 |
| Web3 dApp "open RPC endpoint" | Testnet nodes are free+public; SPA must talk to node; upstream rate-limits exist | Endpoint is `/testnet/*`; provider on Free tier; same pattern as Uniswap/Aave |
| Web3 dApp "env vars in JS bundle" | `VUE_APP_*`/`NEXT_PUBLIC_*` are CLIENT config by framework design | No actual secret (no API key w/ write access, no private key); values publicly available elsewhere |
| Web3 dApp "CORS * on API" | Token-based auth (Bearer header) means no cross-origin credential theft | Auth is `Authorization: Bearer`; no `Allow-Credentials: true`; SPA needs CORS to function |
| Rate limit missing — non-sensitive endpoint | Program only pays for rate-limit on auth/payment/OTP surfaces | Endpoint handles search, contact form, or sits behind Cloudflare |
| Nuclei `info` template match | Version detection, not exploitation | Template severity is `info`; no CVE PoC executed against live service |
| MFA rate limit (no lockout) | Impact depends on OTP brute-force succeeding — it usually doesn't | 15 requests returned 200 but no OTP code was accepted |
| Open redirect alone | Redirect is informational without token theft chain | No OAuth `redirect_uri` parameter; no auth code or token in the redirected URL |
| Auth bypass — admin precondition | Requires compromised admin to trigger; attacker can't get there | "Admin can do X on behalf of user" — attacker must already be admin |
| XSS via `alert(document.domain)` | Not proof of session theft | PoC shows domain popup only; no `document.cookie` exfil, no event listener |
| SAML metadata exposed | Disclosure only — aids attack but is not standalone impact | No private key or signing cert extracted; metadata is publicly documented by IdP |

**Decision rule:** if your finding matches a kill signal → classify as `[INFORMATIONAL]`, do **not** run `/validate`, move on.

---

### SSRF — constrained loopback proxy / request-ID routing

A URL construction defect can look like SSRF even when the attacker controls only a numeric backend port and a path-like request ID. Validate the **actual request capability**, not string interpolation alone:

1. Identify the fixed host, attacker-controlled components (port/path/query/method/body/headers), and any server-side allowlist of active backends.
2. Test parser/normalization behavior separately: a framework `:path` parameter plus encoded `../` may be decoded and normalized by the HTTP client before the upstream fetch. Record the exact final URL observed by a controlled loopback listener.
3. Confirm response semantics: status codes, JSON-only parsing, response reflection, redirect behavior, and whether a non-200 response is discarded.
4. Map namespace boundaries: `127.0.0.1` inside a container is normally that container, not the Docker host; `ipc: host` does not establish host networking. Do not claim host-local access without `network_mode: host` or equivalent proof.
5. Inventory only compatible targets under the fixed path prefix. A GET-only proxy with a fixed prefix is **not** arbitrary SSRF, port scanning, arbitrary HTTP-method access, or cloud-metadata access unless each additional capability is demonstrated.

**Novelty / duplicate gate:** Before packaging a constrained loopback primitive, compare it against every historical finding's root cause, surface, and blast radius. If a prior report already covers unauthenticated exposure of the same MLNode/control-plane surface and SSRF-class callback/proxy behavior, a newly discovered route is supporting evidence or a report update—not a second submission—unless it crosses a distinct authorization boundary or proves materially independent impact.

**Safe wording:** “unauthenticated callers can cause a loopback GET to an attacker-selected port and reflect successful JSON under a fixed path constraint.”

**Never claim without direct evidence:** arbitrary host/network SSRF, Docker-host access, raw-response exfiltration, secret/metadata access, RCE, network-wide impact, or High/Critical severity.

## MIXED-DNS ROUTE-CONFUSION FINDINGS

For VPN/proxy code that resolves one hostname to multiple addresses, trace the full pipeline: resolver order → vector-wide route decision → filtering/partitioning → per-address connection attempts → firewall enforcement. A scalar `any(excluded) => direct` decision is a candidate only if the unchanged mixed vector is later attempted under that decision.

Require production reachability and connector evidence before claiming clearnet exposure. A routing-unit test proves policy collapse, not packets leaving the default interface. When filtering Rust tests, verify output says `running 1 test`; `--exact` with an incomplete module path can return success after running zero tests.

Detailed checklist and worked NymVPN case: `references/mixed-dns-route-confusion.md`.

## CONDITIONALLY VALID — CHAIN REQUIRED

Build the chain first, prove it works end to end, THEN report.

| Standalone Finding | Chain Required | Valid Result |
|---|---|---|
| Open redirect | + OAuth redirect_uri → auth code theft | ATO (Critical) |
| Clickjacking | + sensitive action + working PoC | Medium |
| CORS wildcard | + credentialed request exfils user PII | High |
| CSRF | + sensitive action (transfer funds, change email, delete account) | High |
| Rate limit bypass | + OTP/reset token brute force succeeds | Medium/High |
| SSRF DNS-only | + internal service access + data returned | Medium |
| Host header injection | + password reset email uses injected host | High |
| Prompt injection | + reads other user's data (IDOR) | High |
| S3 bucket listing | + JS bundles contain API keys or OAuth secrets | Medium/High |
| Self-XSS | + CSRF to trigger it on victim without their knowledge | Medium |
| Subdomain takeover | + OAuth redirect_uri registered at that subdomain | Critical |
| GraphQL introspection | + auth bypass mutation or IDOR on node() | High |

---

## CVSS 3.1 QUICK REFERENCE

### Common Score Examples

| Finding | Score | Severity | Vector |
|---|---|---|---|
| IDOR read PII, any user, auth required | 6.5 | Medium | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N |
| IDOR write/delete, any user | 7.5 | High | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N |
| Auth bypass → admin panel | 9.8 | Critical | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |
| Stored XSS → cookie theft, stored | 8.8 | High | AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N |
| SQLi → full DB dump | 8.6 | High | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N |
| SSRF → cloud metadata | 9.1 | Critical | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N |
| Race → double spend | 7.5 | High | AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N |
| GraphQL auth bypass | 8.7 | High | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N |
| JWT none algorithm | 9.1 | Critical | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |

### Metric Quick Guide

| What you have | Metric | Value |
|---|---|---|
| Exploitable over internet | AV | Network (N) |
| No special timing or race | AC | Low (L) |
| Free account needed | PR | Low (L) |
| No login needed | PR | None (N) |
| Admin needed | PR | High (H) |
| No victim action | UI | None (N) |
| Victim must click | UI | Required (R) |
| Reads all data | C | High (H) |
| Reads some data | C | Low (L) |
| Modifies all data | I | High (H) |
| Crashes service | A | High (H) |
| Affects only app | S | Unchanged (U) |
| Affects browser/OS/cloud | S | Changed (C) |

---

## KILL FAST RULES

The goal is to QUICKLY disqualify bad leads so you hunt real bugs:

1. **5-minute rule**: If you can't fill in Q1's template in 5 minutes → move on
2. **Precondition count**: More than 2 preconditions simultaneously required → kill it
3. **Impact test**: "What does attacker walk away with?" — if nothing tangible → kill it
4. **Admin bypass**: "Admin can do X" is NEVER a bug → kill it immediately
5. **Design doc test**: If it's documented behavior → kill it immediately
6. **Rabbit hole signal**: 30+ min on Q6 with no reproducible PoC → kill it

---

## ANTI-PATTERNS THAT LOSE MONEY

```
Writing a report before confirming the bug exists (most common)
Submitting theoretical impact without proof
"The API returns more fields than necessary" (sensitivity matters — is it actually sensitive?)
Chaining A+B into one report when they're separate bugs (two separate payouts)
Reporting B saying "similar to A in my other report" — fresh Gate 0 for every bug
- Overclaiming severity — triagers trust you less next time
- Under-describing impact — triager doesn't understand why it matters

## REPORT WRITING MISTAKES THAT GET REPORTS REJECTED

### Never Include Reward Amounts in Reports

The program's reward table is **for you, the hunter**, to know what to expect. It is **not** for the report.

- ❌ "Critical severity (up to $50,000 per Obol's bounty table)"
- ❌ "High — $5,000-2,000 USDT per Rolly's scale"
- ❌ "Medium — likely $1,000 payout based on program"
- ✅ "Critical severity per Obol's bounty table classification"
- ✅ "High severity per Rolly's scale"
- ✅ "Medium severity based on the program's tier definitions"

Let the program tier the finding themselves. Mentioning amounts:
- Comes across as presumptuous ("I want the max")
- Looks like you're shopping for max payout
- Triggers pushback when the program downgrades your severity
- Wastes the program's time on a meta-discussion

**Title pattern**: Always use the **tier name** ("Critical", "High", "Medium") not the **amount** ("$50K", "$5K").

**Adversarial review section**: Same rule — discuss tier placement, not dollar amounts.

### Overstating Severity Kills Credibility

Across multiple programs in a single session, a pattern emerged: subagents find real
observations, but report them as Critical/High when the evidence only supports
Medium/Informational. The verifier-agent catches most of these, but **prevent overstating
in the first place** by running the adversarial review section before submission.

**Self-correction**: If your report has more "likely" / "may allow" / "could potentially" than
"confirmed" / "demonstrated" / "verified" — DOWNGRADE before submitting.

### Self-Critique Without External Verification = Insufficient

ai-quality skill (self-critique) is good for catching obvious false positives. But it cannot
catch the **program-specific threat model** and **out-of-scope category** issues. Always
run a separate external LLM verification pass before submission:

1. Self-critique via ai-quality (catches internal logic errors)
2. External LLM verifier (catches overstated severity, out-of-scope claims, missing evidence)
3. Manual adversarial review per this skill

If only self-critique, expect ~30% of findings to be downgraded or rejected by the program.
If external LLM verification is added, expect ~5-10% rejection rate.

## EXTERNAL LLM VERIFICATION WORKFLOW

For high-stakes findings (Critical/High or >$1K potential bounty), use a **second-opinion
LLM as a verifier**. This is a separate LLM (not the one that found the bug) tasked with
adversarially reviewing the report as if they were the program triager.

**Why this works**:
- The finding model has confirmation bias (it found the bug, so it defends it)
- A verifier model has no emotional attachment to the finding
- Different LLMs have different training biases — they catch different mistakes
- Cost: ~$0.001-0.01 per verification call

**Setup (do once)**:
1. Choose a verifier model different from your hunter model. Free/cheap options:
   - `vpsnodelab/claude-opus-4-8` via xah.io (current primary)
   - `openai/minimax-m3` via xah.io (fallback)
   - OpenAI API: `gpt-4o`, `o1-mini`
   - Anthropic API: `claude-3-5-sonnet`
2. The verifier's role is **verification only**, NOT bug hunting. It must NOT
   suggest new bugs or expand scope.

**Verifier system prompt**:
```
You are an adversarial bug bounty reviewer. Assume every finding is incorrect
until proven otherwise. Your job is to reject weak findings, verify strong ones.
Evidence overrides assumptions. Never guess.
```

**Verifier output format** (request this explicitly):
```
VERDICT: [CONFIRMED | NEEDS_MORE_EVIDENCE | REJECTED]
SEVERITY_ASSESSMENT: [OK | SUGGEST: <new severity> because ...]
POC_ASSESSMENT: [OK | IMPROVEMENTS: ...]
ISSUES: [bullet list of weaknesses]
REASONING: [paragraph explaining verdict]
CONFIDENCE: [0-100%]
```

**When to use the verifier**:
- ✅ Always: Critical severity findings
- ✅ Always: Findings where severity is contested
- ✅ Always: Findings on unfamiliar/rare bug classes
- ⚠️ Optional: Medium severity findings
- ❌ Skip: Low severity / Informational (overkill)

**Pattern from real sessions**: Across 8+ verification calls in a single session,
the verifier rejected 6 findings as overstated, accepted 1 as confirmed, and
required more evidence on 1. The pattern: subagents are good at finding surface
issues, but they default to Critical/High when Medium/Informational is more
accurate. The verifier catches this consistently.

**Decision matrix after verification**:
| Verdict | Action |
|---|---|
| CONFIRMED | Submit at claimed severity |
| NEEDS_MORE_EVIDENCE | Dig more **code/unit/static** evidence (and PoC if feasible); re-verify; then submit at **evidence-backed** severity |
| REJECTED | Kill the finding (don't submit even with "small" tier) |
| SUGGEST severity change | Adjust report to suggested tier before submitting |

**NEEDS_MORE_EVIDENCE → report hygiene:** gather the missing proof or **lower severity**. Never leave verifier residual language (`NEEDS_MORE_EVIDENCE`, confidence %, "wants live E2E") inside the final H1 body. Verifier outputs stay in internal `findings/verifier-*.json` only.

See `references/external-verification-pattern.md` for full setup details, model
recommendations, and worked examples of how the verifier catches overstated findings.

### External verifier prompt — historical duplicate review

When the question is whether a newly proven variant deserves a *second* report, do not ask the verifier merely “is this code vulnerable?” Supply:

- the historical report title, affected routes/files, and claimed weakness;
- the new route’s exact request capability and bounded PoC result;
- an explicit three-part test: same exposed surface, same root-cause class, same blast radius;
- deployment and namespace limits (for example, fixed loopback host is not arbitrary network SSRF).

Ask for a submission disposition, not an abstract severity score. If the verifier returns **REJECTED / duplicate**, retain the PoC only in the original finding or closure record; do not create a new report merely because the new route provides stronger mechanical evidence.

For source-only SSRF verification, a controlled ASGI/mock harness can establish parser → URL-construction → response-reflection behavior, but it does **not** establish sensitive-service exposure. State that boundary directly in the verifier input.

For source-only re-hunts that close without a new submission, use
`references/scoped-rehunt-disposition.md` for novelty, reachability, threat-model,
and evidence gates plus a concise closure-artifact format.

```

---

## ADVERSARIAL SELF-REVIEW (POST-REWRITE)

After writing the report, **assume it is wrong**. Your job is to prove it wrong. Use the **"Zero-Trust Rebuttal"** workflow:
1. **Instruction:** "Assume this report is incorrect. Find hidden assumptions, protocol invariants, deployment constraints, privilege requirements, unrealistic attacker capabilities, policy conflicts, and any reason why this report should be downgraded or rejected."
2. **Analyze:** If the rebuttal identifies a missing link (e.g., "plain transfers are user error"), pivot the attack vector to a more robust one (e.g., "retroactive smearing during valid `deposit()` calls").

The user's own adversarial review caught a Critical overclaim during the Obol Charon audit...

### 1. Code Path Reachability
- Is the vulnerable function actually called by an external attacker? Or only by an internal/admin function?
- Is there a flag or mode that bypasses the code path? (e.g. `if admin || user` — the admin branch may be the only reachable one)
- Is the call site behind a check that an attacker can't realistically satisfy?

### 2. Operator/User Opt-In Requirements
- Does the bug require the operator/user to set a specific flag, config, approval, delegate, or `setOperator`/API-token sharing relationship to be exploitable?
- If yes: was that approval documented as broad authority? Can the approved actor already perform equivalent harm through the intended delegation surface?
- **User-approved operator theft is usually downgrade/kill material**: if the attacker must first be explicitly approved by the victim as an operator/delegate/spender, treat it like a malicious delegate or approval-risk finding unless there is a clear confused-deputy boundary violation that exceeds the granted authority.
- If the report says "approved operator can steal," include a counterargument section explaining why this is not merely user error; otherwise downgrade to Low/Informational or kill.
- The Obol bounty explicitly says: *"we deliberately don't over-reward findings that depend on a member being maliciously incompetent against their own stake."* Operator opt-in reduces severity.

### 3. Cryptographic / Protocol Invariants
- EIP-2335 keystore is encrypted — but if the **decryption password is sent in the same request**, the encryption is meaningless.
- TLS protects in transit — but if the client allows `http://` without error, MITM or operator misconfig defeats TLS.
- Threshold signatures are secure — but only if shares don't leak.
- **Pattern**: encryption/MITM/etc. provides X protection, but if a design flaw defeats the protection, the report should explain HOW.

### 3b. Bridge / cross-chain claim windows (design SLA ≠ High brick)
Kill or downgrade “epoch key deleted → permanent fund lock High” unless **all** fail:
- **Documented retention** (`MAX_STORED_EPOCHS`, “N epochs = N days”) → intentional claim window, not silent CWE-404
- **No attacker force-cleanup** — next key needs sequential transition BLS and/or owner+admin; time + honest rotation is not an exploit primitive
- **`epochId` protocol-bound** — signing uses *current* epoch on request; user cannot mint under soon-deleted ancient epochs
- **Wall-clock length** — map epochs → days (genesis `epoch_length`); year-scale → Likelihood Low (rational capital claims in hours/days)
- **Counterpart refunds** — fail/expire → auto-refund; complete → claim-or-lose on destination; cancel-after-complete often rejected. “Always permanent loss” is false if fail-path refunds
- **Network-wide High bar** — stale unclaimed tickets ≠ network liveness failure
- **Owner epoch jump** wiping old keys = trust/centralization (separate), not unauth High

Static PoC that “epoch 366 deletes key 1” only proves design. Full kill list: `verifier-agent/references/design_sla_claim_window.md` (Gonka G5 pattern).

### 3c. Multi-package disprove → final disposition (do before any re-submit)

When user says **disprove semua / report final / kill then ship**, do **not** re-open hunt. Adversarially invalidate **every** packaged report, then one consolidated disposition.

| Outcome | Meaning | Submit? |
|---------|---------|---------|
| **INVALID / REJECTED** | Framing fails (wrong severity, design SLA, no attacker path) | **No** at claimed tier |
| **SCOPE KILL** | Root cause in OOS asset (even if code real) | **No** on this program |
| **SURVIVE tempered** | Code real; drop overclaims; keep honest severity | **Yes** after rewrite |
| **NEEDS_MORE_EVIDENCE** | Sub-claim (e.g. metadata SSRF E2E) unproven | Split: ship proven half only |

**Mandatory splits:** unauth control vs callback/SSRF completion (batch/GPU may be required); incomplete SSRF validation (no LookupIP) vs proven rebind→metadata; OOS feeder vs in-scope root.

**Final report must:** disposition table · supersede stale submit maps · submit queue = survivors only · PoC re-run status. See `references/multi_finding_disprove_disposition.md`.

### 3d. Private-network intent vs stock public bind (missing-auth nodes)

Do **not** full-kill unauth management solely because README says “private network”:
- Stock compose publishes port (`0.0.0.0` / `${PORT}:8080`) → defect **survives** as single-node ≤ Medium
- Stock is loopback-only (`127.0.0.1:9200`) → Likelihood collapses (Low/Info or misconfig)
- Never upgrade single-node DoS/control to High without network-wide effect

### 4. External Attacker vs. Insider Framing
- Most bounty programs prefer "external attacker" framings. If your attack requires:
  - Operator running a misconfigured flag, OR
  - Insider with elevated privileges, OR
  - Physical access, OR
  - Compromised host
- Then the bug is **less likely** to qualify for Critical/High, even if impact is severe.
- Reformulate the report to show how an **external attacker** exploits the bug. If you can't, downgrade severity.

### 5. Severity Tier Alignment
- The program's specific tier definitions matter. Read them carefully.
- Common tier-elevation patterns (DON'T DO):
  - "Operator misconfig + cluster keyshare recovery" = Medium, not Critical (no external attacker)
  - "Admin can do X on behalf of user" = always kills the bug
  - "Requires MFA bypass" = usually low/info
  - "Internal IP in error message" = information disclosure tier, not critical
- Common tier-elevation patterns (OK TO DO):
  - Show how the external attack works step by step
  - Prove the impact with actual evidence (response body, exfiltrated data, not just 200 status)
  - Cite the program's exact tier definition and explain why your bug matches

### 6. Counter-Argument Documentation
If you DO downgrade, document the counter-arguments considered in the report itself. This:
- Shows the program you understand their threat model
- Helps them understand your reasoning
- Reduces follow-up emails asking "why isn't this Critical?"
- Preserves your credibility (shows you did the work)

Template for the report's "Adversarial Review" section:
```markdown
## Adversarial Review

I considered these counter-arguments before submission:

| Counter-argument | Status |
|---|---|
| 1. [Counter-1] | [Acknowledged/Refuted] — [brief reason] |
| 2. [Counter-2] | [Acknowledged/Refuted] — [brief reason] |
| ... | ... |

**Conclusion**: [Why the bug stands / why the severity was downgraded]
```

### 7. The "Operator Configured Wrong" Rule of Thumb
A useful heuristic:
- **Critical**: bug is exploitable by external attacker with **zero operator opt-in** (e.g. default config is vulnerable)
- **High**: bug is exploitable by external attacker with **operator misconfig** (e.g. wrong flag, weak password)
- **Medium**: bug requires **insider action** (insider with elevated privileges)
- **Low/Info**: bug is informational or requires multiple unlikely conditions

Test your bug against this. If it falls in High (operator misconfig), do NOT claim Critical. Programs will downgrade you.

### 8. The Obol-Specific Tier Mapping (Real Example)
The Obol Charon BLS keymanager bug (operator sets `http://attacker` for `--keymanager-address`):
- **Original claim**: Critical ($50K) — because BLS exfil is a Critical tier item
- **Adversarial review found**: requires operator to set `http://` URL, which is operator opt-in
- **Obol's own threat model says**: don't over-reward findings that require "member being maliciously incompetent against their own stake"
- **Honest severity**: High ($5K) — matches the High tier's "exfiltrate operator key material" line
- **Fix**: change report from Critical to High with explicit "Adversarial Review" section
- **Result**: faster triage, higher credibility, still eligible for payout

This is a reusable pattern: **claim the highest tier your evidence supports, but not higher**. Overclaiming hurts your long-term reputation more than underclaiming.

---

## EXAMPLES — REAL ADVERSARIAL REVIEWS

### Example 0: User-Initiated Verification ("Sudah yakin? Sudah verify ulang? PoC nya jalan?")

When the user asks "are you sure about the findings? did you re-verify? does the PoC actually work?" — assume they are **right** to ask. Replay the candidate PoC from a fresh session before answering yes. This pattern was observed during Memento DFM and Maya recon: the assistant had written reports for findings whose actual exploitation was unverified or blocked by missing inputs. The honest answer was "I haven't proven this yet" — not "yes, submit it."

**Concrete self-check protocol before claiming any finding is "ready to submit":**

```
1. Re-run the exact exploit PoC from a clean state right now.
2. Confirm the response body still shows the bug (not just HTTP 200/400/etc).
3. Confirm the impact claim survives the proof (does 200 actually leak data? does 400 actually skip auth?).
4. If any step fails → DOWNGRADE or KILL the finding. Do not submit unverified claims.
5. If the user pushes back asking why PoC didn't work → ADMIT IT. Don't pretend success.
```

A report that says "Invalid request body returned, body validation runs before auth" is **observation, not exploit**. Submission-ready requires either:
- A 200 OK with actual data (or write side-effect) on the unauth endpoint
- A concrete chain demonstrated end-to-end (e.g., OIDC `none` alg → forged token → userinfo returns victim data)

### Example 1: Obol Charon BLS Keymanager (High after downgrade)

**Original claim**: Critical ($50K)

**Counter-arguments considered**:
1. Code path is reachable: ✅ Yes, when `KeymanagerAddr != ""`
2. Operator opt-in: ⚠️ Yes — operator must set the flag
3. External attacker: ⚠️ Partial — needs operator misconfig OR MITM
4. Cryptographic invariant: ❌ EIP-2335 keystore encryption defeated by sending password in same request
placeholder
