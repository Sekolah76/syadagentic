# Distributed Systems Guardrails

Use these controls for consensus, validators, peer-to-peer protocols, replicated state machines, snapshots, replay, restart, and asynchronous execution.

## Legal Event Sequence Requirement

Every proposed schedule must identify:

- initial reachable state;
- authenticated message/event source;
- protocol-valid event at each step;
- attacker-controlled delay, drop, reorder, replay, or duplication capability;
- honest-node transitions;
- invariant violated at the end.

Artificial scheduler control is not attacker control unless the real network permits the same ordering under the stated threat model.

## Safety Versus Liveness

Never conflate:

- local state mismatch with finalized safety violation;
- slow progress with permanent liveness failure;
- one crashed task with node failure;
- one node failure with quorum loss;
- fork observation with conflicting finalization;
- recovery delay with unrecoverable corruption.

## Fault and Quorum Accounting

Record:

- total validators/nodes;
- faulty, malicious, offline, and partitioned nodes;
- stake or voting weight;
- quorum thresholds;
- whether the scenario already exceeds the protocol fault assumption.

A scenario requiring fault power beyond the published threat model is not proof of a vulnerability under that model.

## Persistence Tests

For divergence or corruption claims, test:

- restart;
- snapshot load;
- replay from canonical history;
- peer reconciliation;
- epoch/view/round transition;
- rollback and garbage collection;
- finality checkpoint.

State that disappears during normal reconciliation is not permanent state divergence.

## Resource and DoS Tests

Do not execute unbounded network-wide load. Prefer analytical bounds, local simulations, controlled node clusters, and low-rate confirmation.

Measure:

- attacker cost per event;
- victim CPU, memory, disk, bandwidth, and queue growth;
- protocol and transport caps;
- backpressure;
- restart/fault isolation;
- recovery time;
- amplification factor;
- sustained versus transient impact.
