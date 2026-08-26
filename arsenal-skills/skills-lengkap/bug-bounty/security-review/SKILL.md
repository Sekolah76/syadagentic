---
name: security-review
description: 'AI-powered codebase security scanner that reasons about code like a security researcher — tracing data flows, understanding component interactions, and catching vulnerabilities that pattern-matching tools miss. Use this skill when asked to scan code for security vulnerabilities, find bugs, check for SQL injection, XSS, command injection, exposed API keys, hardcoded secrets, insecure dependencies, access control issues, or any request like "is my code secure?", "review for security issues", "audit this codebase", or "check for vulnerabilities". Covers injection flaws, authentication and access control bugs, secrets exposure, weak cryptography, insecure dependencies, and business logic issues across JavaScript, TypeScript, Python, Java, PHP, Go, Ruby, and Rust.'
---

# Security Review

An AI-powered security scanner that reasons about your codebase the way a human security
researcher would — tracing data flows, understanding component interactions, and catching
vulnerabilities that pattern-matching tools miss.

## When to Use This Skill

Use this skill when the request involves:

- Scanning a codebase or file for security vulnerabilities
- Running a security review or vulnerability check
- Checking for SQL injection, XSS, command injection, or other injection flaws
- Finding exposed API keys, hardcoded secrets, or credentials in code
- Auditing dependencies for known CVEs
- Reviewing authentication, authorization, or access control logic
- Detecting insecure cryptography or weak randomness
- Performing a data flow analysis to trace user input to dangerous sinks
- Any request phrasing like "is my code secure?", "scan this file", or "check my repo for vulnerabilities"
- Running `/security-review` or `/security-review <path>`

## How This Skill Works

Unlike traditional static analysis tools that match patterns, this skill:
1. **Reads code like a security researcher** — understanding context, intent, and data flow
2. **Traces across files** — following how user input moves through your application
3. **Self-verifies findings** — re-examines each result to filter false positives
4. **Assigns severity ratings** — CRITICAL / HIGH / MEDIUM / LOW / INFO
5. **Proposes targeted patches** — every finding includes a concrete fix
6. **Requires human approval** — nothing is auto-applied; you always review first

## Execution Workflow

Follow these steps **in order** every time:

### Step 1 — Scope Resolution
Determine what to scan:
- If a path was provided (`/security-review src/auth/`), scan only that scope
- If no path given, scan the **entire project** starting from the root
- Identify the language(s) and framework(s) in use (check package.json, requirements.txt,
  go.mod, Cargo.toml, pom.xml, Gemfile, composer.json, etc.)
- Read `references/language-patterns.md` to load language-specific vulnerability patterns

### Step 2 — Dependency Audit
Before scanning source code, audit dependencies first (fast wins):
- **Node.js**: Check `package.json` + `package-lock.json` for known vulnerable packages
- **Python**: Check `requirements.txt` / `pyproject.toml` / `Pipfile`
- **Java**: Check `pom.xml` / `build.gradle`
- **Ruby**: Check `Gemfile.lock`
- **Rust**: Check `Cargo.toml`
- **Go**: Check `go.sum`
- Flag packages with known CVEs, deprecated crypto libs, or suspiciously old pinned versions
- Read `references/vulnerable-packages.md` for a curated watchlist

### Step 3 — Secrets & Exposure Scan
Scan ALL files (including config, env, CI/CD, Dockerfiles, IaC) for:
- Hardcoded API keys, tokens, passwords, private keys
- `.env` files accidentally committed
- Secrets in comments or debug logs
- Cloud credentials (AWS, GCP, Azure, Stripe, Twilio, etc.)
- Database connection strings with credentials embedded
- Read `references/secret-patterns.md` for regex patterns and entropy heuristics to apply

### Step 4 — Vulnerability Deep Scan
This is the core scan. Reason about the code — don't just pattern-match.
Read `references/vuln-categories.md` for full details on each category.

**Injection Flaws**
- SQL Injection: raw queries with string interpolation, ORM misuse, second-order SQLi
- XSS: unescaped output, dangerouslySetInnerHTML, innerHTML, template injection
- Command Injection: exec/spawn/system with user input
- LDAP, XPath, Header, Log injection

**Authentication & Access Control**
- Missing authentication on sensitive endpoints
- Broken object-level authorization (BOLA/IDOR)
- JWT weaknesses (alg:none, weak secrets, no expiry validation)
- Session fixation, missing CSRF protection
- Privilege escalation paths
- Mass assignment / parameter pollution

**Data Handling**
- Sensitive data in logs, error messages, or API responses
- Missing encryption at rest or in transit
- Insecure deserialization
- Path traversal / directory traversal
- XXE (XML External Entity) processing
- SSRF (Server-Side Request Forgery)

**Cryptography**
- Use of MD5, SHA1, DES for security purposes
- Hardcoded IVs or salts
- Weak random number generation (Math.random() for tokens)
- Missing TLS certificate validation

**Business Logic**
- Race conditions (TOCTOU)
- Integer overflow in financial calculations
- Missing rate limiting on sensitive endpoints
- Predictable resource identifiers

### Step 5 — Cross-File Data Flow Analysis
After the per-file scan, perform a **holistic review**:
- Trace user-controlled input from entry points (HTTP params, headers, body, file uploads)
  all the way to sinks (DB queries, exec calls, HTML output, file writes)
- Identify vulnerabilities that only appear when looking at multiple files together
- Check for insecure trust boundaries between services or modules

### Step 6 — Self-Verification Pass
For EACH finding:
1. Re-read the relevant code with fresh eyes
2. Ask: "Is this actually exploitable, or is there sanitization I missed?"
3. Check if a framework or middleware already handles this upstream
4. Downgrade or discard findings that aren't genuine vulnerabilities
5. Assign final severity: CRITICAL / HIGH / MEDIUM / LOW / INFO

### Step 7 — Generate Security Report
Output the full report in the format defined in `references/report-format.md`.

### Step 8 — Propose Patches
For every CRITICAL and HIGH finding, generate a concrete patch:
- Show the vulnerable code (before)
- Show the fixed code (after)
- Explain what changed and why
- Preserve the original code style, variable names, and structure
- Add a comment explaining the fix inline

Explicitly state: **"Review each patch before applying. Nothing has been changed yet."**

## Severity Guide

| Severity | Meaning | Example |
|----------|---------|---------|
| 🔴 CRITICAL | Immediate exploitation risk, data breach likely | SQLi, RCE, auth bypass |
| 🟠 HIGH | Serious vulnerability, exploit path exists | XSS, IDOR, hardcoded secrets |
| 🟡 MEDIUM | Exploitable with conditions or chaining | CSRF, open redirect, weak crypto |
| 🔵 LOW | Best practice violation, low direct risk | Verbose errors, missing headers |
| ⚪ INFO | Observation worth noting, not a vulnerability | Outdated dependency (no CVE) |

## Output Rules

- **Always** produce a findings summary table first (counts by severity)
- **Never** auto-apply any patch — present patches for human review only
- **Always** include a confidence rating per finding (High / Medium / Low)
- **Group findings** by category, not by file
- **Be specific** — include file path, line number, and the exact vulnerable code snippet
- **Explain the risk** in plain English — what could an attacker do with it?
- If the codebase is clean, say so clearly: "No vulnerabilities found" with what was scanned

## Pitfalls

### Severity-filtered requests ("ONLY CRITICAL", "ONLY HIGH", "report only X")

When the user asks for a severity-filtered report (e.g., "Report ONLY CRITICAL with concrete PoC"), **respect the filter strictly**:
- Do NOT include a findings summary table with all severities — the user wants signal, not noise
- Do NOT include LOW, MEDIUM, or INFO findings in the report body
- Do NOT include "non-findings" or "verified safe" sections — the user already knows the codebase has other things
- DO include a brief "coverage" line at the end so the user knows what was checked
- DO include the requested-severity findings with file:line, vulnerable code snippet, PoC path, and fix
- If a MEDIUM finding is genuinely a CRITICAL after re-examination, re-rate it and explain why

**Bad response to "Report ONLY CRITICAL":**
> "CRITICAL-1: free-rider attack. Also, here are 5 LOW findings, 3 MEDIUM findings, and a section on what I verified as safe..."

**Good response to "Report ONLY CRITICAL":**
> "## CRITICAL-1: Free-rider attack on empty bins in `addLiquidity`
> **File:** `metric-core/contracts/libraries/LiquidityLib.sol:81-131`
> **PoC:** [3-step PoC]
> **Fix:** [one-liner require]
>
> Coverage: swap callback reentrancy, flash loan oracle manipulation, bin price manipulation, extension bypass, race conditions, timing attacks — all defended."

### Don't report "verified safe" items when the user asked for findings only

When a user asks "find vulnerabilities" or "what's wrong with X", they want findings, not a list of things that are correct. A "verified safe" section adds noise. Exception: if the user asks "audit this for X specifically", a one-line "checked X, Y, Z — no issues found" is appropriate as coverage confirmation.

### Python/FastAPI: client-controlled backend routing via composite IDs

For proxy or fan-out routes that accept a composite identifier (for example `port:request_id`), treat the backend selector and the remainder as untrusted independently:

1. `int(port)` validates only format; enforce membership in the server-maintained backend registry before any dial.
2. A FastAPI `{value:path}` parameter permits `/`; do not concatenate its unvalidated remainder into a backend URL. `..` can normalize the path and `?` can inject backend query parameters.
3. If the proxied JSON result is returned to the requester, this is response-disclosing loopback SSRF, not merely an internal routing defect.
4. Validate deterministically by mocking the helper that dials the backend, capturing its `port/path`, then resolving the constructed URL with the real HTTP client parser. This proves the primitive safely without probing real local services.
5. Prefer an opaque server-side request-token mapping; otherwise validate port membership and a strict request-ID grammar, then encode path segments.

See [`references/python-fastapi-composite-backend-routing.md`](references/python-fastapi-composite-backend-routing.md) for a reproduction recipe and reporting boundaries.

## Multi-server HTTP surface audits (public / admin / callback)

When the target is a **node API** or decentralized worker with **multiple Echo/HTTP listeners** (public + admin + ML/callback + optional gRPC), do **not** jump into a single handler. Follow:

1. **Map surfaces first** — route registration, middleware stack, code bind (`:%port` vs `127.0.0.1`), and **deploy publish** (compose `ports:` / nginx). Severity of unauth admin depends on localhost-only publish.
2. **SSRF on chain- or peer-stored URLs** — registration validators that only `net.ParseIP` private ranges **miss DNS hostnames** (resolve/rebind at proxy time). `NoRedirectClient` / `CheckRedirect → ErrUseLastResponse` only stops **redirect** SSRF, not initial resolve-to-private. Trace `baseURL+path` and forwarded auth headers.
3. **Admin without app auth** — logging-only middleware + `GetConfig()` unsanitized (keys) + `tx/send` signed as the node is Critical **if** the port is reachable; still report as defense-in-depth with honest compose mitigations.
4. **Unauthenticated callbacks** — phase-gate-only PoC/webhook ports that submit chain msgs as the node when published world-open.
5. **Document mitigated authz** — epoch-bound participant + grantee sig payload gates, dual-context AuthKey reuse, etc., so you do not re-report them.

Full checklist, greps, and finding-card shape: [`references/multi-server-http-surface-audit.md`](references/multi-server-http-surface-audit.md).

### Tooling pitfall — large handler files

Repeated `read_file` on the same large Go handler ranges may block/dedup. Prefer single-range `sed -n 'A,Bp'` and `rg -n 'func …' -A N`; finish the **route→auth map** before writing findings.

### P2P / consensus ingestion audits

For Rust validators, UDP/gossip repair, blockstore ingestion, signature pipelines, bounded channels, or retransmit logic, use [`references/p2p-consensus-ingestion-audit.md`](references/p2p-consensus-ingestion-audit.md).

Required workflow:
1. Trace each message: source → admission → decode → validation → expansion → sink → backpressure, with exact `file:line` evidence.
2. Quantify attacker-controlled fanout from sourced constants. Check upstream bounds, queue caps, and batch-vs-packet semantics.
3. Inventory expensive work before stake, rate, identity, version, nonce, or time-window gates.
4. Analyze bounded-channel `Full` behavior: blocking can bind liveness; dropping can desynchronize caches/state. Prove attacker-controlled sustained saturation before reporting.
5. Cross-reference known issues by verifying the old pattern, replacement guard, and regression test in the audited commit. Closed metadata alone does not prove a fix.
6. Keep candidates labeled `hypothesis` until remote reachability, attacker control, missing mitigation, sink effect, and deterministic impact are proven.

False-positive guards: no guessed batch sizes; no “deadlock” without circular wait; no attacker-chosen collision claim from probabilistic filter false positives; no panic claim from guarded `unwrap`/`expect` without an invariant-breaking path.

## Reference Files

For detailed detection guidance, load the following reference files as needed:

- `references/vuln-categories.md` — Deep reference for every vulnerability category with detection signals, safe patterns, and escalation checkers
  - Search patterns: `SQL injection`, `XSS`, `command injection`, `SSRF`, `BOLA`, `IDOR`, `JWT`, `CSRF`, `secrets`, `cryptography`, `race condition`, `path traversal`
- `references/secret-patterns.md` — Regex patterns, entropy-based detection, and CI/CD secret risks
  - Search patterns: `API key`, `token`, `private key`, `connection string`, `entropy`, `.env`, `GitHub Actions`, `Docker`, `Terraform`
- `references/language-patterns.md` — Framework-specific vulnerability patterns for JavaScript, Python, Java, PHP, Go, Ruby, and Rust
  - Search patterns: `Express`, `React`, `Next.js`, `Django`, `Flask`, `FastAPI`, `Spring Boot`, `PHP`, `Go`, `Rails`, `Rust`
- `references/vulnerable-packages.md` — Curated CVE watchlist for npm, pip, Maven, Rubygems, Cargo, and Go modules
  - Search patterns: `lodash`, `axios`, `jsonwebtoken`, `Pillow`, `log4j`, `nokogiri`, `CVE`
- `references/report-format.md` — Structured output template for security reports with finding cards, dependency audit, secrets scan, and patch proposal formatting
  - Search patterns: `report`, `format`, `template`, `finding`, `patch`, `summary`, `confidence`
- `references/multi-server-http-surface-audit.md` — Public/admin/callback multi-listener audit (SSRF DNS bypass, unauth admin, compose bind vs code bind, PoC callbacks)
  - Search patterns: `SSRF`, `NoRedirectClient`, `admin`, `callback`, `compose`, `InferenceUrl`, `PoC`
- `references/rust-http-api-service-audit.md` — Rust axum/reqwest/sqlx HTTP service audit notes for route/auth mapping, shared agent tokens, assignment/result integrity, async credential retrieval, and SSRF triage
  - Search patterns: `Rust`, `axum`, `route_layer`, `sqlx`, `agent`, `assignment`, `secret`, `credential_id`
- `references/rust-ecash-credential-issuance-audit.md` — Rust ecash/credential issuance audit notes for cross-user share retrieval, async replay/double issuance, migration-lost uniqueness, signer replay leakage, and secret-bearing logs
  - Search patterns: `ecash`, `credential`, `ticketbook`, `blind-sign`, `device_id`, `credential_id`, `blinded_shares`, `Authorization`
- `references/ts-next-react-frontend-audit.md` — TypeScript/Next/React frontend audit checklist for XSS, markdown/MDX rendering, untrusted URLs/images, wallets/docs data leaks, Tauri links, and API route handlers
  - Search patterns: `dangerouslySetInnerHTML`, `react-markdown`, `href={`, `next/link`, `app/api`, `NextResponse`, `localStorage`, `openUrl`, `invoke(`
- `references/desktop-privileged-daemon-boundary-audit.md` — Desktop GUI/Tauri ↔ root/SYSTEM daemon audits: UDS/named-pipe/XPC authentication versus per-RPC authorization, multi-user secret isolation, arbitrary-PID controls, updater/install ownership, privileged helper execution, symlink/path and deserialization checks, plus disposable tests
  - Search patterns: `Tauri`, `Unix socket`, `named pipe`, `XPC`, `Polkit`, `auth_self`, `peer credentials`, `PID`, `cgroup`, `installer`, `updater`, `root-owned`, `SYSTEM`
- `references/zk-privacy-pool-audit.md` — Rust/Solana ZK privacy-pool audit notes for Groth16 public-input order, Poseidon commitment parity, nullifier canonicality, dummy inputs, value conservation, proof wire conversion, and prover/wallet settlement boundaries
  - Search patterns: `Groth16`, `Poseidon`, `nullifier`, `commitment`, `public_amount`, `ext_data_hash`, `canonical`, `dummy`, `alt_bn128`, `transact`
- `references/p2p-consensus-ingestion-audit.md` — P2P / consensus validator ingestion audit (Rust, UDP, gossip, repair, blockstore, retransmit, bounded channels): trust-boundary trace, amplification quantification, known-issue cross-reference, finding gate, false-positive traps
  - Search patterns: `Rust`, `validator`, `consensus`, `repair`, `gossip`, `UDP`, `blockstore`, `amplification`, `backpressure`, `known-issues`, `blocking-ag`
