---
name: report-writing
description: Bug bounty report writing for H1/Bugcrowd/Intigriti/Immunefi — report templates, human tone guidelines, impact-first writing, CVSS 3.1 scoring, title formula, impact statement formula, severity decision guide, downgrade counters, pre-submit checklist. Use after validating a finding and before submitting. Never use "could potentially" — prove it or don't report.
---

# REPORT WRITING

Impact-first. Human tone. No theoretical language. Triagers are people.

## Output rules — strip severity labels and symbols (this user)

User (Yudha) corrected this twice in one session — hard rule, not style
nicety. Before delivering ANY report (summary or per-finding detail):

- No severity words: Critical, High, Medium, Low, Info, P0/P1/P2, "not
  Critical", "escalates to Critical". Reword to impact language: "Impact
  ceiling:", "full reserve drain", "full account compromise".
- No symbols/emoji: no 🟥🟨🟦⬜🟩, no em-dash, no decorative glyphs.
- No "Not yet reviewed" / "not yet reviewed" sections. Internal follow-up
  notes are not findings — strip them before delivery. A report should
  only contain confirmed findings and "Reviewed and cleared" items.
- Verify with a grep before shipping:
  `grep -rn 'Critical\|Medium\|Low\|Info\|severity\|Severity\|not yet reviewed' <dir>`
- Deliver as individual MEDIA: links and one ZIP bundle (no nested zip).

The CVSS templates and severity decision guide below still use severity
labels for reference — those are internal scoring artifacts. The
deliverable report strips them. When in doubt, re-read this section
and run the grep.

## THE MOST IMPORTANT RULE

> **Never use "could potentially" or "could be used to" or "may allow".**
> Either it does the thing or it doesn't. If you haven't proved it, don't claim it.

```
BAD:  "This vulnerability could potentially allow an attacker to access user data."
GOOD: "An attacker can access any user's order history by changing the user_id
       parameter to the target user's ID. I confirmed this using two test accounts:
       attacker@test.com (ID 123) successfully retrieved victim@test.com (ID 456)
       orders, including their shipping address and payment method last 4 digits."
```

### No verifier-gate / doubt language in final report body

When external verifier returns `NEEDS_MORE_EVIDENCE`, dig more static/unit/PoC evidence — do **not** paste residual doubt into the H1 body.

| Forbidden in final report body | Allowed |
|---|---|
| `NEEDS_MORE_EVIDENCE` | Proven code citations + unit-test names |
| `Verifier gate` / confidence % blocks | Clean severity = Impact × Likelihood |
| "not fully proven", "wants live E2E" | Scoped impact ("this node's vote") |
| Hedge that weakens a claim you still submit | Downgrade severity if evidence is thin |

Keep verifier JSON under `findings/verifier-*.json` as internal artifacts only.

### Program-specific severity formulas beat generic CVSS

Before scoring, read the program's severity page. Some programs (e.g. **Gonka network safety**) define:

```
Risk = Impact × Likelihood
Impact = network perspective
High/Critical require network-wide effects
Issues affecting only one participant usually cap at Low or Medium
```

| Impact guide (network) | Example |
|---|---|
| Critical | Full network control hijack |
| High | Chain halt, module theft, wrong rewards for **all** participants |
| Medium | Moderate disruption, **bounded** blast radius |
| Low | Isolated, no chain impact |

Likelihood: Organic | Intentional profitable | Intentional griefing.

**Process tip:** Low/Medium + straightforward fix → public PR OK; High/Critical → private to trusted contributors.

Never label single-node admin compromise or single-validator vote forge as High/Critical under a network-wide bar. See `references/network-perspective-severity.md`.

## PERSISTENCE RULE

Every report-writing session must leave a complete finding folder on disk. Save
the report draft, pre-submit checklist, references, downgrade counters, and final
submission note under `findings/<target-or-program>-<bug-class>/`. Never rely on
terminal or tmux scrollback for content the hunter needs later.

Minimum files:

```text
findings/<target-or-program>-<bug-class>/
├── hackerone-report.md       # or bugcrowd-report.md / intigriti-report.md / immunefi-report.md
├── submission-notes.md       # final checklist, references, caveats, next action
└── evidence/                 # screenshots, curl output, response bodies when available
```

Multi-finding package (preferred for monorepo node/API audits):

```text
findings/
├── <PROGRAM>-H1-DISCLOSURE.md   # package: exec summary, severity table, rejected residuals
├── G1-H1.md                     # one submit-ready report per finding
├── G2-H1.md
├── G3-H1.md
└── ../pocs/                     # runnable scripts next to findings
```

Each per-finding file should include a short **Program severity mapping** table
(Impact / Likelihood / Risk) when the program defines non-CVSS rules.

### dApp deployment provenance boundary

Before naming a chain, contract, or deployment as affected, re-resolve the deployment loaded by the currently served frontend bundle. Public repositories and checked-in manifests may describe an older chain. In every Web3 report package:

- state the active chain ID, RPC/explorer, deployment block, and exact affected addresses;
- distinguish `current deployment`, `legacy deployment`, and `candidate source` explicitly;
- prove source equivalence per affected contract with live/compiled runtime hashes when the explorer source is unverified;
- never extrapolate a legacy-chain PoC into current-app or mainnet impact;
- if active-deployment discovery changes, move prior artifacts under `legacy-<chain>/` and rewrite the primary report/summary immediately rather than appending a footnote.

See the `bb-methodology` reference `references/live-dapp-deployment-provenance.md` for the pinned-fork and bytecode-verification workflow.

If `tools/validate.py` already wrote `submission-notes.md`, append/update it
instead of creating a duplicate.

---

## TITLE FORMULA

```
[Bug Class] in [Exact Endpoint/Feature] allows [attacker role] to [impact] [victim scope]
```

**Good titles (specific, impact-first):**
```
IDOR in /api/v2/invoices/{id} allows authenticated user to read any customer's invoice data
Missing auth on POST /api/admin/users allows unauthenticated attacker to create admin accounts
Stored XSS in profile bio field executes in admin panel — allows privilege escalation
SSRF via image import URL parameter reaches AWS EC2 metadata service
Race condition in coupon redemption allows same code to be used unlimited times
```

**Bad titles (vague, useless to triager):**
```
IDOR vulnerability found
Broken access control
XSS in user input
Security issue in API
Unauthorized access to user data
```

---

## HACKERONE REPORT TEMPLATE

```markdown
## Summary

[One paragraph: what the bug is, where it is, what an attacker can do. Be specific.
Include: endpoint, method, parameter, data exposed, required access level.]

Example: "The `/api/users/{user_id}/orders` endpoint does not verify that the
authenticated user owns the requested user_id. An attacker can enumerate any
user's order history, including PII (email, address, phone) and purchase history,
by incrementing the user_id parameter. No privileges beyond a standard free
account are required."

## Vulnerability Details

**Vulnerability Type:** IDOR / Broken Object Level Authorization
**CVSS 3.1 Score:** 6.5 (Medium) — AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N
**Affected Endpoint:** GET /api/users/{user_id}/orders

## Steps to Reproduce

**Environment:**
- Attacker account: attacker@test.com, user_id = 123
- Victim account: victim@test.com, user_id = 456
- Target: https://target.com

**Steps:**

1. Log in as attacker@test.com, obtain Bearer token

2. Send the following request:

```
GET /api/users/456/orders HTTP/1.1
Host: target.com
Authorization: Bearer ATTACKER_TOKEN_HERE
```

3. Observe response:

```json
{
  "orders": [
    {"id": 789, "items": [...], "email": "victim@test.com", "address": "123 Main St..."}
  ]
}
```

The response contains victim's full order history and PII despite being requested
by a different user.

## Impact

An authenticated attacker can enumerate all user orders by iterating user_id values.
This exposes: full name, email, shipping address, purchase history, and payment
method (last 4). With ~100K users, this represents a mass PII breach affecting
all registered users. Exploitation requires only a free account and takes minutes
with a simple loop.

## Recommended Fix

Add server-side ownership verification:
```python
if order.user_id != current_user.id:
    raise Forbidden()
```

## Supporting Materials

[Screenshot showing attacker's session returning victim's order data]
[Video walkthrough if available]
```

---

## BUGCROWD REPORT TEMPLATE

```markdown
# [IDOR] User order history accessible without authorization via /api/users/{id}/orders

**VRT Category:** Broken Access Control > IDOR > P2

## Description

[Same impact-first paragraph as HackerOne summary]

## Steps to Reproduce

[Same structured steps — exact HTTP requests, exact responses]

## Proof of Concept

[Screenshot/video showing the actual impact]

## Expected vs Actual Behavior

**Expected:** 403 Forbidden when user_id does not match authenticated user
**Actual:** 200 OK with victim's full order data

## Severity Justification

P2 (High) — Direct read access to other users' PII. Affects all user accounts.
No user interaction required. Exploitable by any authenticated user.
Automated enumeration could exfil all [N] user records in minutes.

## Remediation

Add ownership verification: `if order.user_id != current_user.id: raise 403`
```

---

## INTIGRITI REPORT TEMPLATE

```markdown
# [Bug Class]: [Exact Impact] in [Endpoint/Feature]

## Description

[Impact-first paragraph. Start with what an attacker can do, not with how you found it.
Include: endpoint, method, parameter, data exposed, required privileges.]

## Steps to Reproduce

**Environment:**
- Attacker: email=attacker@test.com (standard account, no special role)
- Victim: email=victim@test.com
- Tested: [date]

**Reproduction steps:**

1. [Login as attacker / visit URL / send request]

2. Send the following HTTP request:

\```http
METHOD /endpoint HTTP/1.1
Host: target.com
Authorization: Bearer ATTACKER_TOKEN
Content-Type: application/json

{"param": "victim_id_here"}
\```

3. Observe response contains victim's private data:

\```json
{"email": "victim@test.com", "address": "123 Main St", ...}
\```

## Impact

[Specific, quantified impact. What data, how many users, what can attacker do.]

CVSS 3.1 Score: X.X ([Severity]) — AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N

## Remediation

[1-3 sentence concrete fix. Include code if helpful.]

## Attachments

[Screenshot or Loom video showing the impact — Intigriti triagers prefer video for complex bugs]
```

**Intigriti-specific notes (this user — hard prefs):**
- Title format: `[Bug Class]: [One-line impact]` — keep **short** (form often has a hard char limit; long titles get truncated). Prefer ≤90–100 chars; offer 2–3 short alternatives when packaging.
- Severity is set by you: Critical/High/Medium/Low/Exceptional. If user self-selects **Medium** on a High-framed package, **accept** — do not re-argue High after submit.
- CVSS 3.1 is standard (CVSS 4.0 also accepted on newer programs). When user shares the CVSS calculator UI, answer with a **pick table** (metric → value → one-line reason), not only the vector string.
- **Video PoC:** if the form asks *"Did you include a video PoC… (video proof is mandatory)"* / *"gimana ini"*, treat as **hard gate**. Answer honestly: **No until video is attached**. JSON/HTTP dumps are not substitutes. Ship a 2–4 min on-screen script (victim context → attacker empty cookies → 200/201s) before Yes. Never tell user to check Yes without video.
- Asset/tier: pick the **listed Tier-1/2 URL asset** (e.g. `https://api.brand.com`), **not** Tier-5 `*.domain` wildcard — wrong tier tanks bounty. State tier + URL-vs-wildcard explicitly in chat when user asks.
- **Paste hygiene — NO markdown tables in Impact (or any paste body):** user feedback *"jangan bentuk tabel, berantakan pas di paste"*. Use **bullets / short paragraphs only** in Description Impact. Keep comparison tables only in local `submission-notes.md`, never in paste blocks.
- Bug type dropdown: map IDOR/BOLA → **Broken Access Control** or **IDOR** (whichever exists); include CWE-639 / CWE-284 in body.
- Post-submit: if user says *"oke udah aku submit"* → short ack + wait guidance only; if *"skip dulu… bounty lain"* → **stop residual hunt on that target** (cancel residual todos), do not push more probes unless they re-open.
- Safe harbor: Intigriti enforces it, be comfortable going slightly aggressive with testing

---

## INTERCOM / SUPPORT-CHAT SUBMISSION FLOW (casinos without a triage platform)

Some bug bounties (Rolly, other casinos in beta) take reports **through the in-product support chat (Intercom)**, not a triage platform. There is no HackerOne-style form — the support team runs a 5-question scripted intake. Adapt to the script; do **not** paste a full H1 template.

### How it flows

1. User opens the support chat on the target site and types a short opening ("I found a bug, where do I report?"). The support agent replies with a numbered question script (typically: *1. What went wrong? / 2. What you did right before it happened / 3. What you expected instead / 4. Where it happened + device/browser / 5. Anything you can attach*).
2. For each numbered question, **answer that one question only**, paste-ready, in the user's voice. Do not dump the whole report at once — the agent pastes each answer into a ticket field and the long block breaks the flow.
3. Keep each answer tight: 1 short paragraph for Q1/Q3, an ordered step list for Q2, a location+device block for Q4, and a single attachment for Q5.

### Answer shape per question (Rolly script — adapt names to the target)

- **Q1 "What went wrong?"** — 1 paragraph: the bug class, the affected function/endpoint, the observed-vs-expected behavior, and the impact in one sentence. No severity label, no reward tier.
- **Q2 "Steps in order"** — numbered list of exactly what you did. For a provably-fair math bug: install the verifier package, read the spec, run the probe, report the three output lines. For a web bug: the exact HTTP request + the response that shows the bug.
- **Q3 "What you expected instead"** — 1 paragraph: the invariant that should hold (e.g. "crash floor should equal the minimum cashout") and, if the behavior is intentional-but-undisclosed, say "if X is intentional, it should be disclosed in the UI."
- **Q4 "Where + device"** — the game/page URL, the canonical artifact you tested against (e.g. `@rolly-dev/wasm-signer@1.28.1`), and the runtime (Node version, OS). No login required for a math-bug PoC — say so.
- **Q5 "Anything to attach"** — a single PoC file. See the attachment rules below.

### Attachment format — confirm what the chat accepts before generating

Intercom's file picker accepts a limited set of extensions. **Before writing the attachment file, ask the user which extensions the picker accepts** (or have them try a `.md` first). Rolly's Intercom rejected `.md` and `.mjs`; it accepted `.pdf` and `.txt`. Generate accordingly:

- **If `.md`/`.mjs` rejected, `.pdf` accepted:** generate the PoC + report as PDF. Use `fpdf2` (`pip install fpdf2 --break-system-packages`); built-in Helvetica/Courier fonts are enough. `markdown` is usually installed; `reportlab`/`weasyprint` are not. Wrap long code lines with `textwrap` (Courier 7pt fits ~125 chars on A4 with 10mm margins) and use `pdf.cell(0, lh, chunk, new_x="LMARGIN", new_y="NEXT")` per wrapped line — `multi_cell` raises `Not enough horizontal space to render a single character` on long unbreakable tokens. Strip non-ASCII (em-dash → `--`, smart quotes → ASCII) before writing.
- **If `.txt` accepted:** write the PoC as plain `.txt` with `====` section banners; Intercom treats it as a text attachment and the agent can read it inline.
- **Always also keep a `.md` on disk** for your own record even if it's not the submitted format.

### Report-body rules specific to chat-submitted reports

- **No reward tier / dollar amount in the body.** (This is already a global rule, but doubly important here: the support agent is not the triager who sets payout — quoting a tier reads as a demand and can bias the handoff.) If the user asks you to remove a `Reward tier: 750–2,000 USDT` line, remove it; keep only `Severity: High` and the bug-class label.
- **Front-load a novelty question.** Chat-submitted reports to a casino in beta often come back **duplicate** because another researcher hit the same clamp pattern in a sibling game. End the report (or the Q1 answer) with: *"Was [specific function/bug] reported in any prior submission? [Function X] is separate from [sibling function Y] but shares the same clamp pattern."* This gives triage a chance to say "already known" before you sink more time, and signals you've already considered the duplicate risk.
- **When the user reports the finding came back duplicate**, do not keep probing that same bug class on that target — the pattern is likely reported across all sibling games. Move to a different bug class or a different target. A short "sayar" + pivot is correct; do not commiserate at length.

---

## IMMUNEFI REPORT TEMPLATE

```markdown
# [Bug Class] — [Protocol Name] — [Severity]

## Summary

[One paragraph with: root cause, affected function, economic impact, attack cost.
Include numbers where possible: "attacker can drain $X in Y transactions."]

## Vulnerability Details

**Contract:** `VulnerableContract.sol`
**Function:** `claimRedemption()`
**Bug Class:** Accounting State Desynchronization
**Severity:** Critical

### Root Cause

[Exact code snippet showing the vulnerable code with comments]

## Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
// Foundry PoC — run: forge test --match-test test_exploit -vvvv

contract ExploitTest is Test {
    // ... full working exploit
}
```

## Impact

[Quantified: "Attacker can drain X% of TVL = $Y at current rates.
Requires $Z gas. Attack is repeatable."]

## Recommended Fix

[Specific code change with before/after]
```

---

## CVSS 3.1 QUICK SCORING

### Formula
```
CVSS = f(AV, AC, PR, UI, S, C, I, A)
```

### Metric Quick Picks

| Metric | Value | Weight | When |
|---|---|---|---|
| **Attack Vector (AV)** | Network | +0.85 | Via internet |
| | Local | +0.55 | Local access needed |
| **Attack Complexity (AC)** | Low | +0.77 | Repeatable |
| | High | +0.44 | Race/timing needed |
| **Privileges Required (PR)** | None | +0.85 | No login |
| | Low | +0.62 | Regular user account |
| | High | +0.27 | Admin account |
| **User Interaction (UI)** | None | +0.85 | No victim action |
| | Required | +0.62 | Victim must click |
| **Scope (S)** | Changed | higher | Affects browser/OS/other |
| | Unchanged | lower | Stays in app |
| **Confidentiality (C)** | High | +0.56 | All data exposed |
| | Low | +0.22 | Limited data |
| **Integrity (I)** | High | +0.56 | Can modify any data |
| **Availability (A)** | High | +0.56 | Crashes service |

### Typical Scores by Bug Class

| Bug | Typical CVSS | Severity |
|---|---|---|
| IDOR (read PII) | 6.5 | Medium |
| IDOR (write/delete) | 7.5 | High |
| Auth bypass → admin | 9.8 | Critical |
| Stored XSS (any user) | 5.4–8.8 | Med–High |
| SQLi (data exfil) | 8.6 | High |
| SSRF (cloud metadata) | 9.1 | Critical |
| Race condition (double spend) | 7.5 | High |
| GraphQL auth bypass | 8.7 | High |
| JWT none algorithm | 9.1 | Critical |

---

## SEVERITY DECISION GUIDE

### Critical (P1)
- Full account takeover of any user without interaction
- Remote code execution
- SQLi with ability to dump/modify entire DB
- Auth bypass to admin panel
- SSRF to cloud metadata → IAM credentials exfil

### High (P2)
- Mass PII exposure (email, phone, SSN, payment data)
- Privilege escalation from user to admin
- SSRF reaching internal services (data returned)
- Stored XSS executing for all users of sensitive feature
- Payment bypass / financial loss without limit

### Medium (P3)
- IDOR on specific user's non-critical data
- XSS on low-sensitivity page requiring victim interaction
- CSRF on important but non-critical action
- Rate limit bypass on OTP (with effort demonstrated)

### Low (P4)
- Information disclosure (non-sensitive, no PII)
- Clickjacking on sensitive action WITH working PoC
- CORS on limited data

---

## SEVERITY SELF-ASSESSMENT

Each YES raises severity:
```
1. Exposes PII / health / financial data of other users?        → +1 severity
2. Allows account takeover or privilege escalation?             → +2 severity
3. Requires ZERO user interaction from victim?                  → +1 severity
4. Affects ALL users (not specific condition)?                  → +1 severity
5. Remotely exploitable with no internal network access?        → baseline for High+
```

---

## DOWNGRADE COUNTERS

| Program Says | Counter With |
|---|---|
| "Requires authentication" | "Attacker needs only a free account — no special role or permission" |
| "Limited impact" | "Affects [N] users / exposes [PII type] / $[amount] at risk" |
| "Already known" | "Show me the report number — I searched hacktivity and found none" |
| "By design" | "Show me the documentation stating this is intended behavior" |
| "Low CVSS" | "CVSS doesn't capture business impact — attacker can extract [X] in [Y] minutes" |
| "Not exploitable" | "Here is the exact response showing victim's data returned to attacker session" |

---

## THE 60-SECOND PRE-SUBMIT CHECKLIST

```
[ ] Title follows formula: [Class] in [endpoint] allows [actor] to [impact]
[ ] Title short enough for platform char limit (≤~100 chars for Intigriti forms)
[ ] First sentence states exact impact in plain English
[ ] Steps to Reproduce has exact HTTP request (copy-paste ready)
[ ] Response showing the bug is included (screenshot or JSON body)
[ ] Two test accounts used — not just one account testing itself
[ ] CVSS score calculated and included (metric pick table if user is on calculator UI)
[ ] Recommended fix is 1-2 sentences (not a lecture)
[ ] No typos in endpoint paths or parameter names
[ ] Report is < 600 words — triagers skim long reports
[ ] Severity claimed matches impact described — don't overclaim
[ ] Never used "could potentially" or "may allow"
[ ] PoC is reproducible by triager from a fresh state
[ ] Web3/dApp: active frontend deployment re-resolved; chain/address is current, not a legacy manifest
[ ] Web3/dApp: source equivalence and pinned fork block are stated when contracts are unverified
[ ] H1 single-asset: correct tree selected (not Bridge/devshard by default)
[ ] Attachments are finding-scoped only (no combined / wrong-G PoCs)
[ ] Telegram: if .py fails download → secret gist + tar.gz (see references/telegram-h1-attachments.md
references/telegram-delivery-preferences.md — this user's hard report-format rules: no severity words, no symbols/em-dashes, no internal status notes, grep-verify before sending.)
[ ] Intigriti: Impact uses bullets (no wide markdown tables that break on paste)
[ ] Intigriti: asset is Tier-1/2 URL list item, not wildcard Tier-5 unless bug is only on wildcard host
[ ] Intigriti: if form marks video PoC mandatory → video attached before answering Yes
[ ] Intercom/support-chat: confirm accepted attachment extension before generating (.md/.mjs often rejected; .pdf/.txt usually accepted)
[ ] Intercom/support-chat: report body has NO reward tier / dollar amount (support agent ≠ triager)
[ ] Intercom/support-chat: front-load a novelty question if target has sibling games sharing the bug pattern
```
### H1 form coaching + Telegram attachments (this user)

- Field-by-field paste mode (`Description*`, mid-stream `eh salah maksud aku G2`): re-anchor immediately; answer with **copy-paste field blocks only**. See `references/h1-single-asset-form-fill.md`.
- Attachment delivery recovery (MEDIA → secret gist + tar.gz, no `$` in gists): `references/telegram-h1-attachments.md
references/telegram-delivery-preferences.md — this user's hard report-format rules: no severity words, no symbols/em-dashes, no internal status notes, grep-verify before sending.`.

---

## TELEGRAM DIRECT DELIVERY PREFERENCES (this user)

When delivering reports/PoCs via Telegram (this user):
- **Send files individually:** Use `MEDIA:/path/to/file` for each file. Do not zip unless explicitly requested or when handling 5+ files.
- **No Severity/Bounty in report:** Strip severity labels (Critical/High/Medium) and bounty amounts from the report body, title, and file names unless authorized.
- **Standalone PoC:** Always provide the Proof of Concept as a separate `.t.sol` or `.py` file, not embedded in the report markdown.
- **Concise Summaries:** accompany the files with a 2-3 line executive summary of the finding.

---

## CVSS 4.0 QUICK REFERENCE (newer programs)

CVSS 4.0 replaced CVSS 3.1 in November 2023. Some newer programs require it.

### Key Differences from CVSS 3.1

| Metric | CVSS 3.1 | CVSS 4.0 |
|---|---|---|
| Attack Vector | Network/Adjacent/Local/Physical | Same |
| Attack Complexity | Low/High | Low/High |
| **NEW**: Attack Requirements | (didn't exist) | None/Present (replaces some PR/UI) |
| Privileges Required | None/Low/High | Same |
| User Interaction | None/Required | None/Passive/Active |
| Scope | Unchanged/Changed | REMOVED |
| **NEW**: Sub-Impact metrics | (didn't exist) | Vulnerable/Subsequent system impact |

### CVSS 4.0 Score Examples

| Finding | CVSS 4.0 Score | Vector |
|---|---|---|
| Unauthenticated RCE | 10.0 | CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H |
| IDOR read PII, auth required | 6.9 | CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N |
| Stored XSS, admin views it | 8.2 | CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N |
| SSRF → cloud metadata | 8.7 | CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:N |

### Quick CVSS 4.0 Calculator
```
Use: https://www.first.org/cvss/calculator/4.0
Key fields:
  VC/VI/VA = Vulnerable System Confidentiality/Integrity/Availability
  SC/SI/SA = Subsequent System (downstream impact)
  AT = None (no special condition) | Present (race/specific config needed)
  UI = None | Passive (victim visits URL) | Active (victim takes explicit action)
```

**Practical rule**: If program uses CVSS 4.0 and you don't know the vector, use the calculator and include the full string starting with `CVSS:4.0/AV:...`. Programs cannot dispute a valid vector string.

---

## HUMANIZER PASS (this user — hard pref)

User explicitly asks for a humanizer pass on reports/PoCs ("jangan lupa pakai humanizer"). Before finalizing any report, run the text through the `creative/humanizer` skill's 29-pattern checklist. Concretely, strip:
- AI-vocab filler: `delve`, `moreover`, `furthermore`, `crucial`, `leverage`, `utilize`, `robust`, `seamless`, `landscape`, `tapestry`, `in conclusion`, `it is worth noting`, `notably`, `underscore`, `foster`, `harness`, `cutting-edge`, `game-changer`, `unlock`, `elevate`, `supercharge`.
- Copula avoidance ("serves as / stands as / marks") → plain `is`/`are`.
- Em-dash overuse, boldface headers, emojis, title-case headings, rule-of-three, negative parallelism ("not just X, it's Y"), passive voice, filler phrases ("in order to", "due to the fact that").
- Significance inflation ("pivotal", "testament", "evolving landscape", "broader movement").
- Generic positive conclusions ("the future looks bright").

Keep the report factual and technical — humanize the *voice*, not the substance. Vary sentence length, use active voice, be specific. The finding's technical accuracy is untouched; only the prose is de-slopped. Run the final anti-AI pass: "what makes this read as AI-generated?" then revise once more.

## HUMAN TONE GUIDELINES

**Write to a person, not a system:**
- Triagers are tired. Get to the impact in sentence 1.
- Use "I" not "the researcher" — you found it, own it
- Short paragraphs, bullet points for steps
- Hyperlink relevant docs if needed

**Escalation language (when payout is being downgraded):**
```
"This vulnerability does not require any special privileges — only a free account."
"The exposed data includes [PII type], which is subject to GDPR requirements."
"An attacker can automate this with a simple loop — all [N] records in minutes."
"This is exploitable externally without network access to any internal system."
"The impact is equivalent to a full data breach of [feature/data type]."
```

**Avoid:**
- Jargon the triager might not know
- 5-paragraph explanations of what IDOR is (they know)
- Theoretical chains ("could be combined with X to...")
- Passive voice ("it was observed that...")
- Qualifying language ("seems to," "appears to")

---

## REPORT HYGIENE — non-negotiable rules

These rules come from real submission feedback and protect the researcher's credibility.

### Never include monetary reward amounts in the report

The program decides the payout, not the researcher. Including `$X,000` or `Up to $Y` in the report body, the title, or the email body signals overconfidence and burns credibility when the triage team downgrades the tier. Lead with **severity name** (`Critical` / `High` / `Medium` / `Low`) and the bug's **exploitability class**, never the dollar amount.

| Wrong | Right |
|---|---|
| `[Critical — $50,000] BLS key exfil...` | `[Critical] BLS key exfil...` |
| `Up to $5,000 (High)` | `High` |
| `The original report claimed $50,000` | `The original report claimed Critical` |

This rule applies to the report body, the email subject, the email body, **and PoC gists** — $ amounts in a PoC also leak budget expectations, don't include them either.

### Match the report's stated severity to the demonstrated exploit

If the report claims `Critical` but the PoC only shows a `Medium` impact path, the triage team will downgrade and lose trust. The severity must be defensible against the strictest reasonable reader. Use the `triage-validation` skill's 7-Question Gate to self-check.

### Run an adversarial self-review before submit

Before sending, attempt to disprove the finding. Generate 5-10 counter-arguments (e.g. "operator opt-in required", "requires social engineering", "TLS protects it", "EIP-2335 keystore is strong"). For each one, check the code to confirm the counter-argument fails. If a counter-argument actually holds, downgrade the severity or kill the finding.

This practice catches overstated Critical claims. A Medium finding with a clean narrative is paid faster than a Critical finding that gets downgraded.

### Send a brief check-in email first when the program recommends it

Several programs (Obol, others) explicitly recommend sending a brief triage email first before the full PoC:

```
Subject: [Triage check] Potential issue in <component> (<bug class>)

Hi <program> Security,

I've found a potential <bug class> in <component> that I believe maps to
your <tier> tier. Affected: <file:function>. Can you confirm whether this
is already known or under active remediation?

I'll send the full report and PoC only if it's not already known.

Best,
<name>
```

This avoids duplicate-work penalty if the bug is already known. Don't skip it even if you already have a working PoC — the check-in costs ~5 minutes and can save 48 hours of waiting on a known issue.

### PoC as a private gist, never inlined in the email

The PoC almost always contains:
- Endpoints / URLs (target-specific)
- Account names or test data (operational)
- Sometimes a captured HTTP body

Put the PoC in a **private (secret) GitHub Gist** and link to it in the email body. Don't attach the PoC file directly — many email gateways flag executables and large files.

When creating the gist, **strip $ amounts and target-specific bounty-table references**. The gist can outlive the submission and end up indexed by search engines.

```bash
# create a private gist via GitHub API
curl -X POST -H "Authorization: token $GITHUB_TOKEN" \
  -d '{"description": "PoC: <bug class>","public": false,"files":{"poc.py":{"content":"<...>"}}}' \
  https://api.github.com/gists
```

Then link `https://gist.github.com/<user>/<id>` in the email.

### Save everything to disk before submitting

Per the PERSISTENCE RULE above: every report, PoC, screenshot, and submission note goes to `findings/<target>-<bug-class>/` on disk. Submissions get lost in email threads; disk files don't.

### Intigriti submit package (disk + Telegram) — when user says submit

User often says **"submit dulu"** / **"Oke submit dulu deh"** mid-hunt. **Stop hunting** and ship a paste-ready package before more probes (T&C reverse, register, XSS, etc.).

```text
findings/<program-or-brand>-<bug-class>/
├── intigriti-report.md      # full body (paste into Description)
├── PASTE_FIELDS.txt         # Title / Severity / Asset / Endpoint / one-liners
├── submission-notes.md      # 7Q, do-not-claim, attach list, after-submit
└── evidence/                # finding-scoped JSON/HTTP only
```

Also ship `findings/<same>.tar.gz` for one-shot Telegram download.

**Chat delivery (this user — Indonesian, concise):**
1. Title + Severity + Asset + Endpoint as copy-paste blocks
2. `MEDIA:` report.md + PASTE_FIELDS.txt + submission-notes.md + tar.gz
3. Min attach list + **Do NOT claim** table
4. Explicit: agent cannot login to Intigriti — user submits from researcher account
5. Program URL + "after submit → resume X"

**Shared-stack de-dupe:** multi-brand Hybris/SAP OCC (e.g. kvn-spa / kvb-spa / kvtp) = **one report**, list all Tier-1 hosts.

**Capability-URL / GUID-only cart BAC packaging:** see `references/capability-url-cart-bac-intigriti.md`.

---

## STEPS TO REPRODUCE FORMAT (triager-optimized)

```markdown
**Setup:**
- Account A (attacker): email=attacker@test.com, ID=111
- Account B (victim): email=victim@test.com, ID=222
- Both created via normal registration — no special access

**Steps:**

1. Log in as Account A
2. Send this request (replace `111` with victim ID `222`):

\```
GET /api/v2/resource/222 HTTP/1.1
Host: target.com
Authorization: Bearer ACCOUNT_A_TOKEN
\```

3. Response contains Account B's private data:

\```json
{"id": 222, "email": "victim@test.com", "name": "Victim User", "address": "..."}
\```

**Expected:** 403 Forbidden
**Actual:** 200 OK with victim's private data
```
