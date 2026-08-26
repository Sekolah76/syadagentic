# Design SLA / Claim-Window Invalidation (Bridge & Cross-Chain)

Use when a packaged finding says: historical keys deleted → late
`withdraw`/`mint` reverts → “permanent brick / High fund lock.”

Session proof (Gonka G5, 2026-07-19): static delete chain was **true**;
**High exploit framing was REJECTED**. Pattern: `findings/G5-DISPROVE.md`
(C1–C9 counters).

## Default stance

**Assume intentional claim window until disproved.** Storage-bounded
epoch keys + “cannot reinstall lower epochId” is normal key-rotation
hygiene, not automatically a bug.

Only keep High/Critical if **every** counter below fails.

## Kill checklist (run in order)

### C1 — Documented design?
- Constant + comment (`MAX_STORED_EPOCHS = 365 // 365 days`)
- Spec/md: retention, “1 epoch = 1 day”, storage optimization
- If yes → SLA, not silent CWE-404, unless window absurdly short *and*
  undocumented *and* no recovery under realistic ops

### C2 — Attacker force-cleanup?
- Who installs next epoch? Sequential + transition BLS? Owner + ADMIN only?
- Can unauth force N installs or delete arbitrary keys?
- Cleanup as side effect of honest time/committee rotation → **no attacker path**

### C3 — Is `epochId` attacker-chosen?
- Does signing bind `CurrentEpochId` from **current** epoch group?
- If user cannot request under ancient epoch, scenario is only
  “got sig in E, ignored destination claim until E+N”

### C4 — Economic / calendar window
- Map retention N epochs → wall time (genesis `epoch_length`, docs)
- Year-scale → rational capital claims in hours/days → Likelihood **Low**
- Hours/days windows need harder scrutiny

### C5 — Counterpart-chain refund semantics
| Event | Expected |
|-------|----------|
| Threshold signing **failed**/expired | Auto-refund escrow / re-mint |
| Threshold signing **completed** | Drop pending-refund maps (claim-or-lose) |
| Cancel after COMPLETED | Often **rejected** |

“Always permanent loss” dies if fail-path refunds. Residual = post-complete
+ delay past retention — claim-or-lose SLA, not unauth drain.

### C6 — Network-wide High bar
- Risk = Impact × Likelihood; High needs **network-wide** effect
- Stale unclaimed tickets ≠ “bridge dies for everyone”
- Normal relayer SLA inside window → severity collapse

### C7 — “No restore” may be a feature
- Bounds storage + usefulness of compromised historical committee keys
- Owner re-publish of old keys expands trust surface

### C8 — Owner epoch jump
- `setGroupKey(epochId >= latest+1)` can skip and wipe `new-N` → **owner**
  trust class, not unauth High (separate from time + normal progression)

### C9 — Proposal vs production
- Code under `proposals/` may still be in-scope SourceCode
- Do not invent Medium likelihood without live claim volume / relayer SLA

## What stays true (does not save High)
- Mapping delete → verify reverts; sequence guards block reinstall;
  static PoC “epoch N deletes N-MAX” is a design demo

## Verdict template
```
VERDICT: REJECTED | NEEDS_MORE_EVIDENCE | CONFIRMED
SEVERITY_ASSESSMENT: SUGGEST: Informational/Low (design claim window) |
  OK High only if C1–C6 all fail
REASONING: list which C# killed the High framing
```

## Hunter disposition
- **Do not submit** as High “permanent unrecoverable exploit”
- Optional residual: Info/Low — document hard claim deadline; optional
  re-sign/reclaim after destination key expiry
- Keep admin-without-transition-BLS as **separate** trust finding if any

## Related
- Adversarial self-review: `triage-validation` §3b
- Put this checklist into external verifier `target_context` for bridge findings
