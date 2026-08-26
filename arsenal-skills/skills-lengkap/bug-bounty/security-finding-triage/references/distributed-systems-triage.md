# Distributed Systems and Consensus Triage Reference

Use this reference when a candidate involves validators, replicas, consensus, snapshots, replay, restart, networking, scheduling, or state-machine divergence.

## Safety Claims

A safety issue requires a legal execution in which honest participants violate a property that must never fail, such as:

- two conflicting values finalized;
- committed state diverges among honest replicas;
- invalid state transition becomes committed;
- authenticated ownership/accounting invariant is broken;
- finalized data is reverted contrary to protocol guarantees.

Prove:

- the message/event sequence is protocol-legal;
- malicious participants stay within the claimed capability;
- honest nodes use supported code/configuration;
- divergence is observable at the protected state level, not merely in caches/logs;
- reconciliation, fork choice, or replay does not eliminate the divergence.

## Liveness Claims

A liveness issue requires more than delay. Establish:

- what progress property is promised;
- synchrony/timing assumptions;
- attacker resources and duration;
- whether progress stops indefinitely or only slows;
- whether timeout, view change, leader rotation, or retry restores progress;
- whether the attacker can sustain the condition economically.

## Scheduler Realism

Classify schedules:

- `ATTACKER_FORCED`: attacker can deterministically create ordering;
- `ATTACKER_BIASED`: attacker can increase likelihood;
- `NETWORK_POSSIBLE`: possible under network timing but not controlled;
- `HARNESS_ONLY`: produced only by arbitrary test scheduler;
- `PROTOCOL_ILLEGAL`: violates protocol assumptions.

Do not report harness-only schedules as practical attacks without a bridge to real execution.

## Restart, Snapshot, and Replay

Validate:

- snapshot authenticity and freshness;
- trusted checkpoints;
- replay ordering;
- persisted versus in-memory fields;
- crash consistency;
- partial writes;
- duplicate application;
- rollback boundaries;
- rejoin reconciliation;
- whether a crafted snapshot/state is attacker-producible.

## Network DoS

Differentiate:

- one connection dropped;
- one worker/task panic;
- one process crash;
- automatic process restart;
- node unavailable;
- many nodes affected;
- quorum loss;
- network halt.

Each escalation needs separate evidence.
