# Adversarial Review Before Submission

**Mandatory step before submitting any Critical/High finding**: assume the report is wrong and try to disprove it. This pattern emerged from the Obol Charon audit (Jul 2026) where an initial $50K Critical claim was correctly downgraded to $5K High after rigorous counter-argument search.

## Why This Matters

Most bounty hunters over-claim severity. Triagers will downgrade obvious over-claims, which:
- Hurts your credibility on subsequent findings
- Risks getting the entire report rejected if the critical claim is clearly overstated
- Wastes the triager's time

Honest severity is the right move. Let the triager upgrade if they agree, not argue from a weaker position.

## The 12 Counter-Arguments Checklist

Before submitting, run through ALL of these:

| # | Counter-argument | How to verify |
|---|---|---|
| 1 | Code path not called by default | `grep` the function and read all callsites — is the flag opt-in or always-on? |
| 2 | Flag rarely used with `http://` in practice | Check the test suite — tests using `http://` prove the path is exercised |
| 3 | Go's `http.Client` does not follow HTTPS→HTTP downgrade redirects | **True** but operator-set `http://` URL works directly. MITM is harder, not impossible |
| 4 | Operator must knowingly set both flags | True, but no opt-in required for `http://` scheme — just a `log.Warn` |
| 5 | EIP-2335 keystore encryption is strong | True, but the **decryption password is sent in the same request** — encryption defeated |
| 6 | Bearer token is HTTPS-only in practice | **False** — typically set unconditionally for both schemes |
| 7 | `url.Parse` rejects `http://` | **False** — Go's `url.Parse` accepts it; tests use it |
| 8 | Authorization header is HTTPS-only in practice | **False** — set unconditionally for both schemes |
| 9 | The bug requires social engineering of the operator | Out of scope per most bounties. But copy-paste error, bad tutorial, env-var injection, MITM are all realistic |
| 10 | The bounty prefers "external attacker" framings | **Critical** — read the bounty page's threat model carefully |
| 11 | "Operator opt-in" reduces severity | Read Obol's "we deliberately don't over-reward findings that depend on a member being maliciously incompetent against their own stake" |
| 12 | The combined effect of (no TLS check) + (password in request) is a real design flaw, but its severity depends on how often misconfiguration happens | This is the main reason to downgrade Critical → High/Medium |

If you can find **any one** of these that holds, your severity claim is too high. Downgrade.

## The "Bounty Threat Model" Read

**Before claiming any severity, read the program's threat model section.** Look for phrases like:
- "external attacker" (Critical) vs "insider" (Medium)
- "without prior compromise" (Critical) vs "after operator misconfiguration" (High/Medium)
- "high likelihood" (Critical) vs "low likelihood" (Medium)
- "deliberately don't over-reward X" (anti-pattern indicator)

For Obol specifically:
- **Critical ($50K)**: "An **external attacker** can ... **without** colluding with cluster operators." "Exfiltrate enough BLS validator key shares **from a threshold of operators** ... to reconstruct a validator's **full private key**."
- **High ($5K)**: "**Operator opt-in** misconfig" → "exfiltrate operator key material"
- **Medium ($1K)**: "**Constrained external position**" or "**insider**"

If your finding requires operator misconfig to trigger, it's **not** Critical. It's at best High.

## Severity Downgrade Matrix

| Original claim | Counter-argument found | Downgrade to |
|---|---|---|
| Critical ($50K) | "Operator opt-in required" | High ($5K) |
| Critical ($50K) | "Requires active MITM" | High ($5K) |
| High ($5K) | "Only on deprecated code path" | Medium ($1K) |
| High ($5K) | "Out of scope per program rules" | N/A (rejected) |
| Medium ($1K) | "Won't trigger in practice" | Low ($250) or reject |

## Adversarial Review Output

When you find counter-arguments, **document them in the report**. Don't hide the downgrade. The honest framing is:

> ## Adversarial Review
> Before submission, I attempted to disprove my own report. Here are the counter-arguments I considered:
> [list with status: Acknowledged / True / False / Mitigated]
> The single strongest argument against the original Critical rating is **#X**: [reason]. Therefore, the honest severity is **High ($5K)**, not Critical.

This framing:
- Shows technical depth to the triager
- Builds credibility for future submissions
- Avoids the "always over-claims" pattern
- Sometimes still gets upgraded by the triager if they disagree

## Real-World Example: Obol Charon BLS HTTP Exfil (Jul 2026)

**Initial claim**: Critical ($50K) — "BLS private key share exfiltration via plaintext HTTP to keymanager"
**Adversarial review found**: Operator must set `--keymanager-address` flag (opt-in). Obol's threat model explicitly downweights operator misconfig.
**Final claim**: High ($5K) — "exfiltrate operator key material" matches Obol's High tier.
**Outcome**: Submitted as honest High. Avoided over-claim that would have been downgraded anyway, hurting credibility for the 8 other findings submitted in the same bundle.

**Lesson**: The original 12-counter-argument exercise turned what could have been a rejected/wasted submission into a credible one. Always run it.

---

# Obol Bug Bounty — Specific Notes

URL: `https://docs.obol.org/advanced-and-troubleshooting/security/bug-bounty`

The Obol bug bounty has unique characteristics worth capturing for future Charon/DV middleware audits.

## Threat Model Statement (verbatim)

> "The Obol threat model treats **external attackers harming live DV clusters** as the highest priority... A cluster member acting irrationally against the cluster they themselves operate is a real but lower-priority risk: the cluster's BFT thresholds and slashing economics already make this self-defeating, and we deliberately don't over-reward findings that depend on a member being maliciously incompetent against their own stake."

**Implication**: Findings requiring operator misconfiguration (like `--keymanager-address http://attacker`) are at best High, not Critical.

## Bounty Tiers (verbatim from Obol)

| Tier | Max | Trigger |
|---|---|---|
| Critical | $50,000 | External attacker path, high impact, high likelihood |
| High | $5,000 | External attacker, operator key material compromise, or infra affecting many clusters |
| Medium | $1,000 | Insider or constrained external position; BFT/slashing already makes self-harm costly |
| Low | $250 | Minimal impact; low-to-medium likelihood |

## Reward Calculation

"Reward amount is 10% of the funds directly affected up to a maximum of [tier cap]." For Critical, that means **up to $50K** for an attack that affects $500K+ of staked funds.

## Recommended Submission Process

Per Obol's own page:

> "Before investing significant time in a proof of concept, you may email security@obol.tech with a brief, non-detailed description of the affected component and the class of vulnerability (e.g. 'potential role escalation in OVM' or 'Charon peer message handling'). We will confirm within 48 hours whether the issue is already known or under active remediation."

**Strategy**:
1. **First**: Send a brief triage email (no PoC, no details). 48h response.
2. **If not known**: Send the full report with PoC.
3. **Subject line**: Use the pattern `[Obol Bug Bounty] [Severity] Brief description` — helps the triager route.
4. **Attachments**: Standalone report (one finding per file) plus a `REPORT_Full_Bundle.md` if multiple findings.

## Out of Scope (do not report)

- Social engineering of staff
- Rate limiting / non-security UX
- Physical security
- Third-party apps/libraries
- Obol Stack (pre-release — Hermes, OpenClaw, x402 facilitator, Cloudflared, eRPC, etc.)
- `charon alpha` commands (pre-release)

## Discovery Tip: Fetch Markdown Variant of Docs Pages

For doc-heavy sites like docs.obol.org, the markdown variant is **much** cleaner than scraping HTML:

```bash
# Append .md to page URL to get raw markdown
curl -skL "https://docs.obol.org/advanced-and-troubleshooting/security/bug-bounty.md"
```

This bypasses all the GitBook SPA noise and gives you clean markdown you can `read_file` directly.

---

# PoC Pattern: "Impossible to Install" Targets

When auditing a target like Charon (Go) that requires significant infrastructure to run a real exploit, use the **simulate-the-relevant-network-behavior** pattern:

```python
# 1. Build the EXACT request body the real code would send
#    (read from source: keymanagerReq struct in keymanager.go)
body = {
    "keystores": [json.dumps(EIP2335_KEYSTORE_TEMPLATE)],
    "passwords": [secrets.token_hex(32)]  # matches randomHex64()
}

# 2. POST it with the same HTTP client config (default transport)
#    keymanager.go uses new(http.Client).Do(req) — no custom transport
resp = requests.post(
    f"{attacker_url}/eth/v1/keystores",
    json=body,
    headers={"Content-Type": "application/json", "Authorization": "Bearer dummy"},
    timeout=10
)
```

The PoC demonstrates the bug without installing the target software. Valid as long as:
- The request body matches the real code
- The HTTP client behavior matches the real code (default `http.Client` is fine)
- The attacker can confirm the impact (decryption, signature forgery, etc.)

**Saved PoC**: `/tmp/obol/poc.py` (Obol Charon BLS exfil demo, 6.4KB, runnable in 2 terminals). Shows the full request body, captured plaintext at the attacker, and a step-by-step impact walkthrough.

## When This Pattern Is Valid

- The bug is in a network protocol or API interaction
- The client code's request structure can be read from source
- The server-side impact can be demonstrated with a small mock
- The runtime environment (Charon cluster, DKG peers) is impractical to set up

## When This Pattern Is NOT Valid

- The bug is in client-side state machine logic
- The bug requires multi-step interaction (e.g. DKG round 1 + round 2)
- The PoC needs to demonstrate a specific race condition or timing issue
- The reviewer will demand an end-to-end run (rare, but happens for Critical submissions)

In those cases, bite the bullet and set up the real environment. Or use **a subagent in a sandboxed environment** to run the actual exploit, then capture the output.

---

# Subagent Delegation for Parallel Audit

When auditing a target with **multiple distinct attack surfaces** (e.g. Obol = API + Go client + Solidity contracts), dispatch **one subagent per surface** in parallel rather than serializing:

```python
# Pattern: delegate by attack surface, not by file
subagent_1 = delegate_task(
    goal=f"Audit {target} API ({n_endpoints} endpoints) for security vulnerabilities",
    context="..."
)
subagent_2 = delegate_task(
    goal=f"Audit {target} Go client for {high_value_classes}",
    context="..."
)
# Manually audit the Solidity contracts in parallel
```

**Why this works**:
- Subagents have isolated context, no cross-pollination confusion
- Each can do deep focus on one surface without losing attention
- You stay free to do the manual smart-contract work the subagents can't easily do
- Results come back as separate deliverables you can compare

**Output handling**:
- Don't poll — let them run, do other work
- When results arrive, cross-reference them
- Manually verify the highest-severity claims before submission (subagents can over-claim just like the main agent)

**Cost benefit**: In the Obol audit, 2 subagents + 1 manual session = 9 findings in ~2 hours. Serial would have been ~5+ hours with attention loss.

**Critical caveat**: Subagent reports include `api_calls: N` and `Total duration: Xs` — track these. If a subagent burned 50+ tool calls in 1500s, it likely got close to its limit. Trust the conclusion but verify the highest-severity claim.

---

# Monorepo node + API severity (Go / Cosmos / join-compose)

Proven on Gonka (`gonka-ai/gonka`, 2026-07-19). For single-operator **dAPI + chain** monorepos (not DV middleware — see `distributed_validators_playbook.md`).

## Official program formula first (Gonka-style)

```
Risk = Impact × Likelihood
Impact = network perspective
High/Critical require network-wide effects
One participant/node usually caps at Low or Medium
```

See `report-writing/references/network-perspective-severity.md`.

| Finding class | Network impact | Cap |
|---------------|----------------|-----|
| Unauth ML callback forges **this node's** PoC vote + first-write-wins | Bounded single-validator integrity | **Medium** |
| DNS SSRF no LookupIP (executor dial path) | Bounded node-originated HTTP | **Medium** |
| Admin no auth + GetConfig secrets + tx re-sign | One-node operator compromise | **Medium** (not High/Critical) |
| Token estimate / cosmetics | Isolated | **Low** |

**Do not claim High** for single-node admin even if `WorkerPrivateKey` + re-sign are proven — fails network-wide bar.

## Severity axes (always split — likelihood, not free severity uplift)

| Axis | Cite | Effect on **Likelihood** |
|------|------|---------------------------|
| Process bind | `fmt.Sprintf(":%v", port)` / `0.0.0.0` in `main.go` | Dangerous default |
| Host publish | compose `"9100:9100"` vs `"127.0.0.1:9200:9200"` | Remote vs local reachability |
| App auth | logging-only middleware? | Defense-in-depth even on loopback |

Rules:
1. Network-wide High/Critical needs impact on **all** participants / consensus — not one host.
2. Stock compose localhost admin → **Medium** (local unauth + secret leak + re-sign still valid).
3. Public ML/callback in compose supports remote unauth **Medium** claims if no app auth.
4. Contrast admin vs ML publish in the same compose — best likelihood narrative.
5. Report body: Impact × Likelihood table; no verifier hedge language.

## Single-node vote / first-write-wins

Unauth callback → node signs chain msg:

| Claim | Severity |
|-------|----------|
| Forges **this node’s** vote | Medium |
| First-write-wins locks honest ML (`Has*` skip) | strengthens Medium |
| Network-wide alone under honest-majority OOS | **Do not claim High** |
| Fee spam | usually 1 tx per key |

Check: weight sign (`>0` valid), duplicate key, phase gates. Unit test posting without auth header is gold evidence.

## DNS SSRF (no LookupIP)

`ParseIP` only → DNS hostnames allowed; resolve private at dial. Prerequisite often **selected executor**. Prompt leak to attacker-as-executor may be intended — aim at internal targets. Medium for validation gap. Deterministic control-flow mirror (Python/Go) is valid PoC when live Go toolchain missing.

## Admin GetConfig + tx/send

Raw `GetConfig()` with `WorkerPrivateKey`? `tx/send` re-signs via recorder vs broadcast-only? No auth + secrets + re-sign = full **one-node** compromise when reachable → **Medium** under network bar (document compose loopback as likelihood reducer, not as "info only").

## Verifier refile loop

After external verifier `NEEDS_MORE_EVIDENCE` + `SUGGEST: Medium`: dig more static/unit/PoC evidence, refile at tempered severity, ship if severity OK — **never invent live E2E**, **never paste NEEDS_MORE_EVIDENCE into H1 body**. See `verifier-agent/references/external_llm_invocation.md`.

## H1 package

One package doc + per-finding `G*-H1.md` + `pocs/` scripts + rejected/residual table; each file has Program severity mapping; unit-test unauth is gold evidence for Medium auth bugs.

## Pitfalls

Prefer `rg -n -A` / line-range over full Path dumps if truncated. Do not equate “builds MsgX” or admin `bridge/block` with free mint without authority path.

## Strict H1 asset-list re-hunt + MLNode control plane (2026-07-19)

When H1 assets are **path-scoped** (user image / SourceCode list):

1. Re-hunt **only** those roots; everything else OOS even if impact is strong.
2. Primary vulnerable file must sit under an eligible path — secondary touch of in-scope code does not rescue OOS primary root.
3. Exclude already-filed known bugs from “new” counts.
4. Admin-only bridge `setGroupKey` missing transition BLS = centralization/doc gap unless unauth path — not automatic High.
5. MLNode/FastAPI worker: prove no auth Depends + public publish + server-side callback URL dial → **Medium** single-node (G4 class). Static PASS/FAIL matrix is valid PoC without live GPU.

| Finding class | Cap under network bar |
|---------------|----------------------|
| Unauth mlnode `/stop` + `/pow/init` + attacker `url` SSRF | **Medium** (single host) |
| Bridge admin setGroupKey no transition sig | residual / centralization unless unauth |
| Prior OOS-primary (dAPI) findings | park for this H1 |

Full checklist + static PoC matrix: `references/h1-asset-scope-gate-and-mlnode.md`.
