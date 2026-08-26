# P2P / Consensus Ingestion Audit

Use for Rust validators, gossip networks, UDP repair services, signature-verification pipelines, bounded channels, retransmission, and blockstore ingestion.

## Trust-boundary trace

For every remotely influenced message, record:

1. **Source:** socket/listener, peer identity source, spoofability.
2. **Admission:** packet-size cap, signature/authentication, stake/allowlist, shred/network version, time window.
3. **Decode:** format parser, allocation behavior, malformed-input cost.
4. **Validation:** nonce/request correlation, Merkle/proof checks, slot/root bounds, identity-to-key mapping.
5. **Expansion:** messages, requests, allocations, cryptographic work, DB reads generated from one input.
6. **Sink:** consensus pool, blockstore, repair queue, retransmit fanout, metrics/reward channels.
7. **Backpressure:** bounded/unbounded queue, `try_send` behavior, blocking fallback, eviction/drop semantics.

Write the trace as `untrusted source → admission → decode → validation → expansion → sink` with exact file:line evidence.

## High-value checks

- **Amplification:** quantify every attacker-influenced loop/range. Compute worst-case fanout across stages, not only the first expansion. Confirm all upstream bounds and queue caps.
- **Pre-auth work:** identify parsing, signature checks, proof checks, allocations, DB reads performed before stake/rate/identity gates.
- **Batch caps:** distinguish batches from packets. A cap on batch count is not a packet cap. Find maximum batch size before claiming a numeric workload.
- **Backpressure:** inspect bounded-channel `Full` handling. Blocking send may cause liveness loss; dropped send may cause state/cache divergence. Prove downstream can remain full under attacker influence.
- **Correlation:** responses must match an outstanding nonce/request plus expected variant, peer/address where required, and proof contents.
- **Time/root windows:** future-slot bounds, old-message pruning, hard-fork/network-version binding.
- **Dedup:** distinguish probabilistic false positives from attacker-chosen collisions. Do not claim chosen collisions unless the keyed bytes and hash/filter behavior make them controllable.
- **TOCTOU:** repeated blockstore/state reads around cleanup or root advancement must tolerate disappearance.

## Known-issue cross-reference

Issue metadata is a lead, not proof.

1. Extract issue number, title, labels, state, body, proposed fix.
2. Locate the exact vulnerable pattern in the audited commit.
3. Locate the exact replacement/guard plus regression test.
4. Classify:
   - `source-verified fixed`
   - `source-verified still present`
   - `metadata closed; fix not independently verified`
   - `not applicable to audited commit`
5. Never infer “fixed” solely from `state: closed` or `state_reason: completed`.
6. Avoid reporting a rediscovered known issue as fresh.

## Finding gate

A candidate remains a **hypothesis** until all are shown:

- remote reachability;
- attacker capability;
- controlling field/value;
- missing or insufficient upstream bound;
- concrete sink effect;
- reproducible or deterministic impact;
- no existing mitigation invalidates the chain.

Do not promote generic CPU use, queueing, blocking, or probabilistic collision to a vulnerability without attacker-controlled sustained impact. Use calibrated labels: `confirmed`, `strong candidate`, `hypothesis`, `refuted`.

## Reporting card

```markdown
### [Severity or Hypothesis] Title
**Confidence:** High/Medium/Low
**Path:** source → admission → decode → validation → sink
**Evidence:** `file:line` exact code
**Attacker controls:** ...
**Bounds/mitigations:** ...
**Worst case:** derived calculation, with sourced constants
**Impact:** ...
**Validation needed:** smallest deterministic test/PoC
**Known-issue overlap:** issue ID or none
```

## Common false-positive traps

- Treating soft receive caps as absent bounds.
- Multiplying guessed batch sizes.
- Calling a blocking send a deadlock without a circular wait.
- Calling ordinary backpressure a remotely exploitable DoS without proving downstream saturation.
- Calling a probabilistic filter false positive an attacker-crafted collision.
- Claiming packets reach a component without tracing listener/channel wiring.
- Listing guarded `unwrap`/`expect` sites without proving invariant violation.
- Declaring all closed issues fixed without checking source and tests.
