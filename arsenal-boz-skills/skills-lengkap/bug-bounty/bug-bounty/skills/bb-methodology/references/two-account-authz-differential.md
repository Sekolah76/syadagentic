# Two-account authorization differential

Use only researcher-owned accounts. Keep account A and B in isolated browser contexts or cookie jars.

## Preconditions

- Policy allows authenticated testing.
- Both accounts belong to the researcher.
- Test resource is created by the researcher.
- No third-party or real-user data involved.

## Matrix

| Actor | Resource owner | Expected | Observe |
|---|---|---|---|
| A | A | allow | baseline response |
| B | A | deny | status/body/side effect |
| A | B | deny | status/body/side effect |
| logged-out | A/B | deny | auth boundary |

## Evidence

Record redacted method, path, request shape, actor context, owner context, expected denial, observed status/body class, and logout/expiry result. Do not store passwords, cookies, bearer tokens, full IDs, or nonpublic data.

## Stop conditions

Stop immediately on nonpublic-data exposure. Retain only minimum redacted evidence allowed by policy. Do not enumerate, scrape, modify, delete, or escalate.

## Proton priority

For Proton-like multi-service programs: researcher-owned account boundary, Drive/Docs sharing, Pass resource ownership, account/session transitions, and cross-service token separation. Treat public config, headers, versions, and intended sharing behavior as non-findings unless a concrete cross-identity impact is proven.
