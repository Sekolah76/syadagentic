# Network-perspective severity (Impact × Likelihood)

Programs that score from a **network** perspective (Gonka 2026, similar L1/validator networks) differ from classic web CVSS.

## Formula

```
Risk = Impact × Likelihood
Impact  = effect on the network / all participants, not "how bad for one host"
Likelihood = Organic | Intentional profitable | Intentional griefing
```

## Impact bars

| Tier | Network bar | Examples that qualify | Examples that do **not** |
|------|-------------|----------------------|---------------------------|
| Critical | Catastrophic whole-network | Full network control hijack | Owning one join node |
| High | Significant at scale | Chain halt; module theft; wrong rewards for **all** | Single-node admin RCE; one validator vote forge |
| Medium | Moderate, bounded blast radius | Integrity of one node's vote; incomplete SSRF on executor URL; unauth admin on one host | — |
| Low | Isolated, no chain impact | Token estimate `len(text)`; cosmetic | — |

**Hard rule:** if blast radius is **one participant / one node**, severity usually **caps at Medium** even when that node is fully compromised.

## Likelihood axes

| Class | When |
|-------|------|
| Organic | Triggers under normal ops without attacker |
| Intentional, profitable | Cheap + money path |
| Intentional, griefing | Cheap + disruption (e.g. unauth POST during PoC phase) |

Stock deploy surface matters for likelihood, not for inventing network-wide impact:
- Compose `9100:9100` public → high likelihood for unauth ML callback
- Compose `127.0.0.1:9200` → remote likelihood low; local unauth still real; **impact still single-node → Medium**

## Worked mapping (Gonka package 2026-07)

| Finding | Impact | Likelihood | Severity |
|---------|--------|------------|----------|
| Unauth ML `:9100` forges **this node's** PoC vote (first-write-wins) | Bounded single-validator integrity | Intentional griefing, public 9100 | **Medium** |
| DNS hostname SSRF (no LookupIP) on InferenceUrl | Bounded node-originated HTTP; needs executor | Intentional participant | **Medium** |
| Admin no auth + WorkerPrivateKey + tx re-sign | One-node operator compromise if reachable | Intentional / misconfig; compose loopback | **Medium** (not High) |
| Token estimate = len(text) | Isolated | Organic | **Low** |

Rejected uplift: admin as High/Critical because secrets leak — fails network-wide bar.

## Report body pattern

```markdown
### Severity (program formula)

| Axis | Assessment |
|------|------------|
| **Impact** | Medium — [bounded network effect in one sentence] |
| **Likelihood** | Intentional griefing — [cost + surface] |
| **Risk** | **Medium** |
```

State explicitly why High/Critical do **not** apply when the program requires network-wide effects.

## Process

- Low/Medium + straightforward fix → PR-track OK
- High/Critical → private trusted contributors
- Package doc + one file per finding + `pocs/`
- Final report: **no** `NEEDS_MORE_EVIDENCE` / verifier confidence % — dig evidence or lower severity

## Related

- `bughunter-os/references/adversarial-review-and-severity-downgrade.md` (monorepo bind vs compose)
- `triage-validation` Q2: map to program impact list, not generic CVSS alone
- `references/h1-single-asset-form-fill.md` — one H1 asset per ticket; form coaching; attach fallbacks
