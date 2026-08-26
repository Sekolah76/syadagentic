# Proton Bounty Policy Reference

Source pages reviewed: `https://proton.me/security/bug-bounty`, `https://proton.me/security/vulnerability-disclosure`, `https://proton.me/security/safe-harbor`.

## Scope

Explicitly listed services only: `proton.me`, `account.proton.me`, `calendar.proton.me`, `drive.proton.me`, `docs.proton.me`, `mail.proton.me`, `api.protonmail.ch`, `pass.proton.me`, Proton Authenticator, Proton VPN, Proton Wallet, Lumo, SimpleLogin, and Standard Notes. Official apps are covered only where the disclosure policy lists them.

## Test limits

No physical testing, social engineering, phishing/spam, DoS/resource exhaustion, malicious software, third-party service testing, data deletion/alteration/sharing/retention/destruction, exfiltration, shell access, persistence, or pivoting. View/store nonpublic data only as necessary to document a vulnerability; stop and notify Proton immediately on nonpublic-data exposure, then purge stored data.

## Reporting and eligibility

Report to `security@proton.me`; PGP is encouraged. First valid report wins. Intended behavior, theory, and best-practice-only reports are ineligible. Require a reproducible PoC or clear impact path, exact affected resource, expected/observed behavior, and measurable impact.

## Rewards

Critical: USD 25,000–50,000; high: USD 2,500–25,000; medium: USD 1,000–2,500; low: case-by-case with no monetary reward by default; exceptional maximum USD 100,000.

## Two-account access gate

Before prioritizing IDOR, tenant isolation, sharing, or cross-service authorization, verify that signup works. If no test access exists, mark authenticated classes blocked; never force signup, brute-force, reuse real-user credentials, or infer authorization impact from public pages. When signup works, use two researcher-owned accounts and a minimal differential matrix: owner, other account, unauthenticated, stale session, and shared-resource recipient. Use only researcher-controlled resources and stop at the first unauthorized read or metadata disclosure.
