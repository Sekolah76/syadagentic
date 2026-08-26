# Kritt Bug-Class Focus Mapping (v1.0)

| Bug Class       | Solidity Pattern                                   | Severity (Hermes) | Typical Bounty Range |
|------------------|---------------------------------------------------|--------------------|----------------------|
| `reentrancy`     | no nonReentrant modifier + external call          | Critical / High    | $5k–$50k            |
| `access-control` | tx.origin OR missing onlyOwner OR public initializer | Critical / High | $1k–$25k            |
| `oracle`         | spot price feed without TWAP, no freshness check  | Critical / High    | $5k–$30k            |
| `proxy`          | storage collision, unprotected upgradeTo        | High / Medium      | $1k–$15k            |
| `gas`            | unbounded loops, expensive gas in hot path        | Medium / Low       | $100–$5k            |
| `garbage-collection` | selfdestruct can brick / delete storage     | Medium             | $500–$2k            |
| `bridge-message` | missing replay protection, malformed payload      | High / Critical    | $10k–$100k          |

## CLI flags (after install)

```bash
kritt scan --repo <URL> --bug-class <class> --sarif > findings.sarif
kritt scan --path  <LOCAL> --bug-class <class> --json | jq '.[] | select(.confidence > 80)'
```
