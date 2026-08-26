---
name: bb-methodology
description: Use at the START of any bug bounty hunting session, when switching targets, or when feeling lost about what to do next. Master orchestrator that combines the 5-phase non-linear hunting workflow with the critical thinking framework (developer psychology, anomaly detection, What-If experiments). Routes to all other skills based on current hunting phase. Also use when asking "what should I do next" or "where am I in the process."
---

# Bug Bounty Methodology: Workflow + Mindset

Master orchestrator for hunting sessions. Combines the 5-phase non-linear workflow with the critical thinking framework that separates top 1% hunters from the rest.

---

## PART 1: MINDSET (How to Think)

### Core Principle

Hunting is not "find a bug" -- it is "prove an attack scenario." Think like an attacker with a specific goal, not a scanner looking for patterns.

### Daily Discipline: Define, Select, Execute

Before touching any tool:

1. **Define**: "Today I target [feature/domain] to achieve [CIA impact]"
2. **Select**: Choose 1-2 vuln classes (IDOR, Race Condition, etc.)
3. **Execute**: Focus ONLY on selected techniques. No wandering.

### 5 Ultimate Goals (Pick One Per Session)

1. **Confidentiality** -- steal data the attacker shouldn't see
2. **Integrity** -- modify data the attacker shouldn't change
3. **Availability** -- disrupt service (app-level DoS only)
4. **Account Takeover** -- control another user's account
5. **RCE** -- execute commands on the server

### 4 Thinking Domains

#### 1. Critical Thinking (deep analysis)

**Question trust boundaries:**
- Frontend control disabled? Send request directly via proxy
- `user_role=user` cookie? Change to `admin`
- `price=1000` in POST? Change to `1`
- `<script>` blocked? Try `<img onerror=...>`

**Reverse-engineer developer psychology:**
- Feature A has auth checks -> Similar feature B (newly added) probably doesn't
- Complex flows (coupon + points + refund) -> Edge cases have bugs
- `/api/v2/user` exists -> Does `/api/v1/user` still work with weaker auth?

**What-If experiments:**
- Skip checkout -> hit `/checkout/success` directly
- Skip 2FA -> navigate to `/dashboard`
- Send coupon request 10x simultaneously -> Race condition?
- Replace `guid=f8a2...` with `id=100` on sibling endpoint -> IDOR?

#### 2. Multi-Perspective (multiple angles)

| Perspective | What to check |
|------------|---------------|
| Horizontal (same role) | User A's token + User B's ID -> IDOR |
| Vertical (different role) | Regular user -> `/admin/deleteUser` |
| Data flow (proxy view) | Hidden params in JSON: `debug=false`, `discount_rate` |
| Time/State | Race conditions, post-delete session reuse |
| Client environment | Mobile UA -> legacy API with weaker auth |
| Business impact | "What's the $ damage if this breaks?" |

#### 3. Tactical Thinking (pattern detection)

- **Naming anomaly**: `userId` everywhere but suddenly `user_id` -> different dev, weaker security
- **Error diff**: Same 403 but different JSON structure -> different backend systems
- **200 but wrong body length/content**: `200 OK` with tiny response or "just a moment" text → WAF soft block, not a real response. Run `bypass_403.sh` to confirm and get baseline diff.
- **Environment diff**: Prod vs Dev/Staging -> debug headers, CSP disabled
- **Version diff**: JS file before/after update -> new endpoints, removed params
- **Supply chain**: Check framework/library versions for known CVEs
- **Third-party integration**: Stripe/Auth0/Intercom -> webhook signature missing?

#### 4. Strategic Thinking (big picture)

- **Asymmetry**: Defender must patch ALL holes. You only need ONE.
- **Intuition engineering**: Log why something "feels wrong." Verify later. Update mental DB.
- **Unknown management**: Can't understand something? Add to "investigate later" list. Just-in-Time Learning.

#### 5. AI-Assisted Thinking (model as a second analyst)

Use AI to expand hypotheses, not to declare verdicts. The model is a fast adversarial planner; the browser, proxy, and live requests are the proof layer.

- **Decompose the feature**: ask for actors, assets, entry points, state transitions, and trust boundaries.
- **Generate sibling paths**: versioned endpoints, mobile routes, legacy APIs, alternate roles, and admin-only variants.
- **Build a role matrix**: anonymous, user A, user B, stale session, fresh session, admin, service account.
- **Ask for dev shortcuts**: "Where would a tired developer skip a check or reuse a helper?"
- **Ask for chains**: "If this bug is real, what bug B and C sit next to it?"
- **Turn ideas into requests**: every AI suggestion must become a single reproducible HTTP experiment.
- **Kill weak signals fast**: if AI cannot point to a concrete request, response diff, or cross-account delta, the idea stays as a hypothesis.

High-signal prompts:
- "Given this endpoint and feature, list the 10 most likely trust-boundary mistakes."
- "What sibling endpoints, methods, or roles should I test next?"
- "Which bug class would a rushed implementation likely miss here?"
- "What does the smallest proof request look like?"
- "What would make this become a real report instead of a scanner hit?"

### Amateur vs Pro: 7-Phase Comparison

| Phase | Amateur | Pro |
|-------|---------|-----|
| Recon | Main domain only | Shadow IT, dev environments, all assets |
| Discovery | Look for errors | Look for design contradictions, business logic flaws |
| Exploit | Give up when blocked | Build filter-bypass payloads |
| Escalation | Report the phenomenon only | Chain to real harm (session steal, ATO) |
| Feasibility | Include unrealistic conditions | Minimize attack prerequisites |
| Reporting | State facts only | Quantify business risk |
| Retest | Check if old PoC fails | Analyze fix method, find incomplete patches |

### Two Approach Routes

- **Route A (Feature-based)**: "This feature is complex" -> deep-dive its input handling -> find vuln
- **Route B (Vuln-based)**: "I want IDOR" -> find endpoints with sequential IDs -> test access control

### Anti-Patterns (Stop Doing These)

- **Program hopping**: Stick with one target minimum 2 weeks / 30 hours
- **Tool-only hunting**: Automation finds duplicates. Manual testing finds unique bugs.
- **Rabbit hole**: Max 45 min per parameter. Set a timer. If stuck, sleep on it.
- **No goal**: "Just looking around" = wasted time. Always Define first.
- **Architecture-as-vulnerability**: Reporting standard platform architecture (public RPC endpoints, client env vars, CORS on token-auth APIs) as bugs. Run adversarial self-review BEFORE writing the report, not after. See `triage-validation/references/web3-dapp-architecture-false-positives.md`.
- **Writing reports before adversarial review**: Always run the 7-Question Gate + adversarial "assume this is wrong" pass BEFORE investing time in a full report. Saves 45+ min per false positive.

### Adversarial Self-Review — 9-Category Counter-Argument Framework

When you have a candidate finding, **assume the report is incorrect** and run this pass BEFORE writing. Each category is a class of rejection that bug-bounty triagers use. If you cannot defeat every category, the finding is probably N/A — kill it before report-writing eats an hour.

1. **Scope ambiguity** — Does the affected asset actually fall inside the program scope, under any reasonable interpretation? "Internal admin tooling reachable on a public-internet hostname" is borderline; "demo page on a marketing site" usually isn't. State the strongest scope-in interpretation AND the strongest scope-out interpretation in the report; do not pretend ambiguity doesn't exist.

2. **No demonstrated impact** — Did you actually prove harm (data exfil, account compromise, code execution, privilege escalation), or only prove "endpoint is reachable"? Hypothetical impact ("if an attacker guessed credentials they could…") almost never pays. If your finding lives in "could/would/might" land, you owe the report a concrete demo path.

3. **Default-credential / preconditions** — Did you confirm default creds exist, or is "admin/admin might work" just a guess? Brute-force without proof of credential validity is not a finding — enumerate the username space and prove at least one valid user, or kill it.

4. **Intended public exposure** — Could a defender argue the configuration is a standard SaaS pattern (SSO callback, login from any IP, public status page)? If so, the bug must be the SSO bypass or the auth-bypass, not the reachability. Move the report onto the actually-exploitable primitive.

5. **OOS by policy** — Re-read the program's out-of-scope list. Mature programs (Tencent, Google, Meta) explicitly enumerate "no rate limit on non-critical forms," "admin panel can be brute forced," "information leakage without direct attack," "missing security headers." If your finding lands on one of those bullets, you can submit but expect rejection — and don't be surprised.

6. **Behavioral / WAF realism** — Did you test under realistic attack load (distributed, low-and-slow, bypass header order)? Behavioral WAFs (AEGIS, Akamai Bot Manager, Cloudflare ML) may pass a small burst then silently drop or fake-respond. A 30-request burst that all return 200 does NOT prove "no rate limit" — it proves "30 sequential requests from one IP weren't rate-limited."

7. **Honeypot / decoy possibility** — Could the endpoint be a deliberate trap that logs all attempts and bans in real-time? Auth endpoints behind behavioral detection sometimes return uniform success/fail errors while quietly correlating with a security team. State the assumption explicitly; if you can't rule it out, soften the impact claim.

8. **Duplicate / known-issue risk** — Mature programs with 100+ reports submitted are likely to have triaged your exact issue before. Search Hacktivity, GitHub issues, changelogs. If you find evidence the team already knows about it, do not resurface it — find a sibling or chain instead.

9. **Sensitive-data exposure (the missing piece)** — Does the bug actually leak credentials, PII, or money? "Endpoint reachable" + "internal service name leaked" + "no auth" by themselves do not pay. The escalation to "this name reveals a credential / enables bypass / grants access" is what carries the bounty. If no escalation exists, downgrade to N/A.

**Output**: After the pass, list each category as PASS / FAIL / UNKNOWN. Any FAIL → kill the finding or rebuild it as a different chain. UNKNOWN → either gather the missing evidence or scope down the claim. The 9-category framework is reusable across web2, web3, cloud, and mobile bug classes — see `references/adversarial-self-review-checklist.md` for the printable checklist and worked examples.

---

## PART 2: WORKFLOW (What to Do)

### The 5-Phase Non-Linear Flow

```
+-------------------------------------------------+
|                                                 |
|  +----------+    +----------+    +----------+   |
|  | 1. RECON |---+| 2. MAP   |---+| 3. FIND  |  |
|  +----------+    +-----+----+    +-----+-----+  |
|       ^                |               |         |
|       |                v               v         |
|       |          +----------+    +----------+    |
|       +----------| 4. PROVE |---+| 5. REPORT|   |
|                  +----------+    +----------+    |
|                                                  |
|  Non-linear: stuck at any phase -> go back       |
|  New API found at phase 3 -> return to phase 2   |
|  WAF blocks at phase 4 -> origin IP from phase 1 |
+-------------------------------------------------+
```

**THIS IS NOT LINEAR.** Move freely between phases. When stuck, return to a previous phase.

### Output Style Constraint (User Preference)
- Ultra terse, technical, no filler. 1 line if possible.
- Drop conjunctions. Strip "Sure!"/"Of course!".
- Code first, explanation minimal.
- If unsure: state it, proceed. No hedging.

## Phase 0: SESSION START (Every Time)

**Before touching any tool, answer these:**

1. **Define**: "Today I target [feature/domain] to achieve [C/I/A/ATO/RCE]"
2. **Select**: Choose 1-2 vuln classes (IDOR, XSS, SSRF, etc.)
3. **Execute**: Focus ONLY on selected techniques
4. **Identity**: Anonymous or authenticated? If the bugs you're hunting need a
   session (IDOR, BOLA, privilege escalation, auth bypass, mass-assignment),
   load auth **once** at session start — see `docs/auth-sessions.md`. Then
   every downstream tool (httpx, katana, ffuf, nuclei, dalfox, PoC verifiers)
   sends those headers automatically and audit log entries are stamped with
   a stable `session_id` hash. For SIWE/wallet login, create only ephemeral
 researcher-owned EOAs, reproduce the frontend's exact message, use separate
 cookie jars for the replay/BOLA differential, redact all auth material, and
 log out test sessions. See `references/controlled-siwe-validation.md`.
 For conventional form login or SSO, use a named secret reference, verify that
 the agent process—not merely an SSH shell—can resolve it, then perform one
 normal login plus one harmless session oracle before attacking authorization.
 Redact query strings, owned-account IDs, cookies, tokens, and response values.
 Never request or persist passwords in chat, reports, notes, artifacts, or
 memory; prefer secure credential profiles/resolvers. For cross-account
 testing, use two isolated browser contexts/cookie jars; never overwrite
 session A while testing session B. A 302 SSO chain is a mapping lead, not a
 finding. See `references/authenticated-program-baseline.md`.
 Cross-account differential testing must record actor/session, target owner,
 exact request, expected denial, observed response, and logout/expiry behavior.
 Stop immediately on nonpublic data exposure; retain only minimum redacted
 evidence required by policy.
- [x] Program channel first: resolve the **live** bounty/VDP page before deep dive.
   - Platform slug may 404 (Immunefi/H1/Bugcrowd) — also check vendor `/vdp`, `SECURITY.md`, `security@`.
   - Example: **Nym** is not a reliable Immunefi slug; official channel is https://nym.com/vdp-bbp + `security@nym.com` (PGP). Details: `references/nym-vdp-bbp.md`.
- [x] Manual-Only Programs: when policy prohibits automated tools/scanners/indexes, apply strict boundaries (no automated subfinder/httpx/archive sweeps). Details: `references/manual-only-program-policy.md`.
6. **Target-switch signals (this user)**: *"skip dulu"*, *"bounty lain"*, numeric menu pick (`1` = first listed target) → **cancel residual todos** on the old program immediately; write `/home/ubuntu/recon/<target>/SCOPE_FENCE.md` before more probes. Do not keep residual hunts after skip.
7. **Prior-work de-dupe**: inventory local `*-report.md`, PGP packages, incomplete chains (e.g. CSP without XSS sink = hardening debt, not a submit).
8. **Live deployment provenance for dApps**: before auditing checked-in addresses, extract the chain ID, RPC, deployment block, flags, and contract map from the frontend bundle currently served to users. Label repository manifests as `current`, `legacy`, or `candidate source`; never let an older checked-in manifest outrank the active app. Prove source equivalence contract-by-contract with runtime bytecode and validate impact on a pinned fork. For custom-chain fork fallback and the full evidence checklist, see `references/live-dapp-deployment-provenance.md`.
9. **Document-published programs and public indexers**: snapshot public policy documents, convert scope into a `SCOPE_FENCE.md`, and explicitly flag unresolved dates/placeholders. A first-party GraphQL/GraphiQL indexer can establish a contract-provenance lead, but its public schema, introspection, CORS, and public on-chain query data are not findings by themselves. Bind each contract to a current official flow and prove its actual role before auditing it. See `references/program-document-and-dapp-provenance.md`.

**Route selection -- Wide or Deep?**

| Signal | Wide (recon sweep) | Deep (focused testing) |
|--------|-------------------|----------------------|
| New program, first day | X | |
| Wildcard scope `*.target.com` | X | |
| Main webapp, been here >3 days | | X |
| Scope update (new domain added) | X | |
| Found interesting subdomain | | X |
| Hunting IDOR / BOLA / auth bugs | | X (auth-aware) |

### Phase 1: RECON

**Goal**: Maximize attack surface. Find what others missed.

**Wide approach** (initial sweep):
```
Subdomain enum -> DNS resolution -> HTTP probing -> Port scan -> Tech detect
```

**Deep approach** (targeted):
```
Google Dorks -> JS file download -> Hidden param discovery -> API mapping
```

| What you find | Next action |
|--------------|-------------|
| Live subdomains with tech stack | Phase 2 (Mapping) |
| Known software (WordPress, Jira) | Check CVEs + defaults immediately |
| Cloud resources (S3, Firebase) | Test permissions (read/write/list) |
| 403 **or 200 + block page** on endpoint | `tools/bypass_403.sh <url>` auto-detects soft blocks (200+block-body). Verdict: bypassed/needs_review/blocked. If all blocked after 5 min, skip |
| Nothing after 5 min on a host | Skip, try next host (5-minute rule) |

**Command**: `/recon target.com`

### Phase 2: MAPPING & ANALYSIS

**Goal**: Understand the app like its developer does.

**Checklist:**
- [ ] Map all endpoints (Burp/Caido sitemap + JS analysis)
- [ ] Identify auth model (cookie, JWT, OAuth, SAML?)
- [ ] Find business-critical flows (payment, registration, password reset, data export)
- [ ] Download and analyze JS files for hidden routes, secrets, logic
- [ ] Identify roles and permissions (user, admin, API keys)
- [ ] Note "weird" behaviors (anomalies in naming, errors, timing)

| What you find | Next action |
|--------------|-------------|
| JS files with interesting code | Taint analysis (Sink -> Source) |
| OAuth/SAML authentication | OAuth/SAML checklist |
| API with ID parameters | Phase 3, target IDOR |
| Complex business logic (payment, coupon) | Phase 3, target BizLogic |
| postMessage listeners | DOM analysis, postMessage-tracker |

### Phase 3: VULNERABILITY DISCOVERY

**Goal**: Find the bug. Use Error-based first, then Blind-based.

**Map attack surface (toolchain)**

| Attack surface | Tools | Scope filter |
|---|---|---|
| DNS / subdomains | `subfinder` → `httprobe` → `naabu` → `nuclei` | Known CVEs first → then takeover (act immediately) |
| Buried endpoints | `waybackurls` + `gau`/`gospider` + `ffuf -w .../api-endpoints.txt` | Parameters & old paths |
| GraphQL | `gqlmap` / `inql` | Introspection |
| POST endpoints | `arjun` | Mass assignment |
| Dedupe | `httpx -status-code -content-md5` |
| Sub takeover | `subzy` / `subjack` | **act immediately** |
| **AI source review** | `kritt scan --bug-class oracle` | Solidity/EVM only; see `references/open-kritt-integration.md` |

> 💡 **Tip:** Run `kritt` concurrently with `slither --filter-paths` — they use different symbolic executors and cross-validate findings.

**Decision flow based on what you're testing:**

```
What input are you testing?
+-- ID parameter (user_id, order_id)
|   -> IDOR checklist
+-- Search/filter/sort field
|   -> SQLi, NoSQLi probing
+-- URL input / webhook / PDF gen
|   -> SSRF checklist
+-- Text field reflected in page
|   -> XSS (DOM or reflected)
+-- File upload
|   -> SVG XSS, web shell, path traversal
+-- Price/quantity/coupon
|   -> Business logic, race conditions
+-- Login / 2FA / password reset
|   -> Auth bypass
+-- Profile update API
|   -> Mass Assignment
+-- Template / wiki editor
|   -> SSTI
+-- Nothing obvious
    -> Fuzz with ffuf, try Error-based probing
```

**Error vs Blind decision:**
1. Try Error-based first (send `'`, `"`, `{{7*7}}`, `${7*7}`) -- watch for 500 errors, stack traces
2. No error? Time-based (`SLEEP(10)`, `; sleep 10;`) -- watch response time
3. No time diff? OOB (`curl attacker.com`, interactsh) -- watch for DNS callback
4. Still nothing? Boolean (`AND 1=1` vs `AND 1=0`) -- watch content-length diff

| What you find | Next action |
|--------------|-------------|
| Low-impact behavior (redirect, self-XSS, cookie injection) | Chain it -- find a connector gadget |
| Confirmed vuln (XSS, IDOR, SQLi) | Phase 4 (Prove and Escalate) |
| Blocked by WAF/CSP/403 **or soft-block 200** | `/bypass-403 <url>` → check verdict (not just status) → `tools/waf_encoder.py "<payload>"` → if upload: `tools/multipart_mutator.py` → 5 min, kill |
| Known software vuln (CVE) | 1-day speed workflow |
| Nothing after 20 min on this endpoint | Rotate (20-minute rule) |

### Phase 4: PROVE & ESCALATE

**Goal**: Prove maximum business impact. Turn Low into Critical.

**Escalation decision:**
```
What did you find?
+-- XSS
|   +-- Can steal cookie/token? -> Session hijack -> ATO
|   +-- Cookie is HttpOnly? -> Force email change via XHR -> ATO
|   +-- Self-XSS only? -> Find CSRF to trigger it
+-- IDOR
|   +-- Can read PII? -> Automate scraping, show scale
|   +-- Can change password/email? -> Direct ATO
|   +-- UUID only? -> Find UUID leak source, then retry
+-- SSRF
|   +-- DNS only? -> DON'T REPORT. Try cloud metadata
|   +-- Can reach 169.254.169.254? -> Extract keys -> RCE
|   +-- Internal port scan? -> Find Redis/K8s -> RCE
+-- SQLi
|   +-- Error-based? -> Extract data (passwords, tokens)
|   +-- Can INTO OUTFILE? -> Web shell -> RCE
|   +-- Blind? -> Boolean/Time extraction
+-- Open Redirect
|   +-- OAuth flow? -> Token theft -> ATO
|   +-- javascript: scheme? -> XSS
+-- Blocked by defense
|   -> Bypass (WAF/CSP/proxy/sanitizer/2FA)
+-- Low-impact, can't escalate alone
    -> Find connector gadget for chain
```

**After proving impact, check:**
- [ ] Can attack work with 0-1 clicks? (minimize prerequisites)
- [ ] Does it affect all users or specific role?
- [ ] What's the business $ impact?

### Phase 5: VALIDATE & REPORT

**Goal**: Get paid. Make triager's job easy.

**Pre-report gate:**
```
Run /validate (7-Question Gate)
+-- All 7 pass? -> Write report
+-- Any fail? -> KILL the finding. Don't waste time.
+-- Borderline? -> Run /triage for quick go/no-go
```

**Report:**
```
Run /report
+-- Platform-specific format (H1/Bugcrowd/Intigriti/Immunefi)
+-- Title: [Bug Class] in [Endpoint] allows [role] to [impact]
+-- Impact-first summary (sentence 1 = what attacker CAN do)
+-- Exact HTTP requests in Steps to Reproduce
+-- Under 600 words
+-- CVSS 3.1 score that MATCHES actual impact
```

**After submission:**
- [ ] While waiting for triage: try to escalate further (A->B signal method)
- [ ] If fix deployed: re-test for bypass (incomplete patch = new bug)
- [ ] Record finding with `/remember` for hunt memory

---

## PART 3: NAVIGATION & TIMING

### Non-Linear Navigation Quick Reference

| I'm stuck because... | Go to... |
|----------------------|----------|
| Can't find any subdomains | Phase 1: Try different recon sources, Google Dorks |
| Found subdomain but don't know what to test | Phase 2: Map the app, download JS, understand auth |
| Testing but nothing works | Phase 3: Switch vuln class (20-min rotation rule) |
| Found a bug but impact is low | Phase 4: Escalation paths or gadget chaining |
| WAF/CSP/403 blocking my payload | `/bypass-403` → fingerprint WAF → `waf_encoder.py` variants → kill if 5 min spent (403 even after `/bypass-403` + WAF fingerprint + `waf_encoder.py` variants) |
| Been stuck for 45 min on one param | STOP. Rabbit hole. Move to next endpoint. |
| New API endpoint discovered during testing | Return to Phase 2: map it before attacking |
| Found one bug | A->B signal: same dev made more mistakes. Hunt 20 min for siblings. |
| Findings look like standard architecture | STOP. Run adversarial review NOW. Compare to Uniswap/Aave. If same pattern = kill immediately. |

### 20-Minute Rotation Clock

Every 20 minutes ask yourself: **"Am I making progress?"**
- Yes -> Continue
- No -> Rotate to next: endpoint -> subdomain -> vuln class -> target
- Been on same target 2+ weeks with no findings? -> Consider switching program

### Tool Routing by Phase

| Phase | Tools | Why this order |
|-------|-------|----------------|
| Program / VDP channel | Live program URL + `SECURITY.md` + vendor `/vdp` (Nym → `references/nym-vdp-bbp.md`) | Before deep dive — wrong platform wastes hours |
| Recon: Subdomains | `subfinder` -> `amass` -> `puredns` -> `httpx` | Passive first (no detection) -> resolve DNS -> probe HTTP + tech stack |
| Recon: URLs | `gau` + `waymore` -> `katana` -> `uro` | Archive (forgotten endpoints) -> active crawl (JS-rendered) -> deduplicate |
| Recon: JS | `jsluice` + `mantra` + `trufflehog --only-verified` | Extract URLs/secrets -> find API keys -> verify keys actually work |
| Recon: Ports | `naabu` (wide) -> `rustscan` (deep) | Fast top-1000 sweep -> full 65535 on interesting targets |
| Recon: Scan | `nuclei -tags cve` -> `nuclei -tags takeover` -> `kritt scan --bug-class all` (AST+symbolic AI scan) | Known CVEs first -> then takeover (act immediately) -> AI source review (open-kritt). See `references/open-kritt-integration.md`. |
| Mapping: Params | `arjun` + `paramspider` + ParamMiner | Brute-force hidden params + mine archives + cache headers |
| Mapping: JS code | Download -> `jsluice` -> VS Code/Cursor grep | Extract -> static analysis -> AI-assisted taint analysis |
| Mapping: Dorks | Manual Google Dorks | Custom per-target queries find what automation misses |
| Native VPN/daemon | Release asset + source trace + isolated network namespaces | Prove aggregate policy decisions at the final socket/interface; audit installer ownership through root execution. See `references/native-client-privacy-and-installer-validation.md` |
| Combined confidential submission | One report + staged PoCs/tests/evidence + verified ZIP | Use only on explicit request; omit requested metadata globally; re-run from staged paths, checksum, secret-scan, CRC-test. See `references/security-submission-bundle.md` |
| Discovery: Fuzz | `ffuf -ac` + `cewl` custom wordlist | Auto-calibrate filtering + target-specific words beat generic lists |
| Discovery: XSS | `kxss` -> `dalfox` | Filter (which params reflect?) -> scan (only reflective params) |
| Discovery: SQLi | `ghauri` | Modern blind SQLi on ID-like parameters |
| Discovery: SSRF | `interactsh-client` | Self-hosted OOB listener for blind SSRF/XXE/RCE |
| Discovery: WAF | `wafw00f` -> `whatwaf` | Identify WAF vendor -> test bypass techniques |
| Exploit: 403 | `byp4xx` or `nomore403` | 20+ bypass techniques automated |
| Exploit: Takeover | `subzy` | Checks CNAME against 70+ vulnerable services |
| Exploit: Cloud | `s3scanner` + `aws` CLI | Scan bucket permissions -> extract metadata credentials |
| Exploit: Secrets | `trufflehog --only-verified` | Only verified working keys (no false positives) |

- **Monorepo Navigation:** When hunting in monorepos, check `pnpm-workspace.yaml` or `packages/` first. Use `find . -name "foundry.toml"` to locate sub-project roots. Source remappings often live in the root or in a `remappings.txt` inside the sub-project.
- **Camofox for WAF Bypass:** If `browser_navigate` hits Cloudflare "Just a moment," use `camofox-browser` via its REST API at `localhost:9377`. It is significantly more stealthy.
- **Lazy Checkpoint Griefing:** Loops walking through historical "expiry buckets" or "epoch checkpoints" (Stake DAO / Curve patterns) can be griefed by "dusting" with many small, distinct expiration events to maximize loop iterations.

### Session End Checklist

- [ ] Save all Burp/Caido project files
- [ ] Record any "weird but not yet exploitable" behaviors (future gadgets)
- [ ] Update notes with failed attempts (don't re-test with same techniques)
- [ ] Log findings with `/remember`

### Account-access gate for bounty triage

Treat account availability as a first-class scope constraint, not an afterthought:

1. Parse policy before probing. Record exact in-scope hosts, reporting channel, allowed test methods, data-handling limits, and whether automation/indexes are prohibited.
2. Check access path manually. If signup is unavailable, do not force registration, brute-force, reuse real-user credentials, or invent auth coverage. Mark authenticated classes (IDOR, tenant isolation, privilege escalation, mass assignment) as blocked.
3. If signup is available, use only researcher-owned accounts. For authorization testing, create two owned accounts and keep a role/resource matrix; prove cross-account access with the minimum harmless read or metadata operation.
4. Prefer programs with clear policy, available test accounts, meaningful rewards, and concrete impact criteria. Switch early when a public marketing surface is the only reachable asset.
5. Scope-fence every target switch. Preserve policy evidence plus a short decision log; do not carry residual probes or assumptions from the previous program.

For multi-service programs, prioritize account/session boundaries, cross-service token confusion, object sharing, and resource authorization before generic header or version checks. See `references/proton-bounty-policy.md` for the Proton policy snapshot and reusable two-account gate.

### Program viability and access gate

Treat target selection as a fast, evidence-backed filter before any hunt:

1. **Verify live status first**: active vs paused/closed; bounty vs VDP; current reward ceiling; exact reporting channel. A directory label is secondary to the first-party policy.
2. **Verify reachable surface**: public site, app, API, product/firmware, and authenticated paths. A broad scope or high maximum reward does not compensate for an unreachable asset.
3. **Check researcher access**: signup, login provider, test-account policy, API-key issuance, hardware/firmware requirements. If access requires a blocked OAuth flow, unavailable account creation, or customer-only provisioning, mark auth-dependent classes blocked; do not bypass or invent coverage.
4. **Interpret blocks correctly**: Cloudflare/challenge/403 means reachability friction, not a vulnerability. Try one low-noise first-party route or documented alternate channel; then stop if the only remaining path is bypassing the protection.
5. **Stop early** when expected proof quality is low: no account, no test tenant, no owned product, no contract/source, paused submissions, or only a marketing surface. Record the skip reason and switch targets.
6. **Serialize stateful browser work**: one navigation/login/action at a time; wait for the current page before the next action. Parallel SPA navigations can race, corrupt the active page, and trigger gateway/session recovery. For OAuth, let the researcher complete credential/MFA/consent in-browser; never request or handle Google credentials, OTPs, cookies, or tokens.

Reusable decision notes and examples: `references/program-viability-triage.md`.

### Vendor-product bounty viability gate

For hardware/software vendors with a product bounty, separate **program eligibility** from **reachable attack surface** before testing:

1. Snapshot the live policy: product families, reward ceilings, report channel, PoC/evidence rules, disclosure limits, exclusions, and whether testing requires owned hardware or accounts.
2. Build a product-access matrix: `DSM/SRM/BeeStation`, desktop/mobile packages, C2/cloud, web services, firmware, and public corporate site. Mark each `available`, `blocked`, or `not applicable`.
3. Rank only reachable surfaces by expected impact × reward × proof quality. A high maximum reward does not justify spending time on an unreachable product.
4. If only the public marketing site is reachable, perform a short manual sanity pass. Do not convert ordinary CMS behavior, public documentation, headers, or version indicators into a bounty finding without customer-impact proof.
5. Stop and request researcher-owned NAS/router, firmware/package, or test C2 access when authenticated product testing is the only credible path. Do not invent access, reuse credentials, or broaden scope.

**Policy-page interaction pitfall:** regional localization can replace the requested page or make accessibility refs stale after tab changes. When a click fails, inspect the current DOM's first-party links and `href` values; resolve the contact form, PGP key, advisory page, and canonical locale from the live DOM. Treat a stale ref as a navigation issue, not missing policy content. Session-specific Synology policy notes: `references/synology-bounty-policy.md`.

### Manual-only scope variants

Not all manual-only policies mean the same thing. Parse each prohibition separately:

- If **domain enumeration** is prohibited, do not use CT, passive-DNS, search indexes, archives, `subfinder`, or guessed subdomains to expand scope. Start from the exact listed root and wildcard scope; add a host only after a normal manual interaction or an explicitly published first-party link establishes it.
- If **automated tools/scripts/scanners** are prohibited, browser DOM inspection, viewing one page's source/resources, and one hypothesis-driven request generated by that interaction remain distinct from automated recon. Do not turn them into loops, wordlist probes, permutations, or batch requests.
- If **post-access escalation** is prohibited, stop after the minimum proof of the initial access vector. Do not chain privilege escalation, persistence, lateral movement, or operational impact.
- If **data exfiltration/modification/destruction** is prohibited, use researcher-controlled markers or metadata only; stop before reading, copying, changing, or deleting real data.

For programs like KNAPP, where scope is `knapp.com` plus `*.knapp.com`, rewards are modest, and no test account is supplied, use a short manual triage: inspect the public root, manually follow first-party links, assess only directly observed web behavior, and record authenticated coverage as blocked. Do not present a WordPress/plugin version, public resource, or generic hardening issue as a bounty finding without a reproducible target-specific security impact.
