---
name: attack-surface-mapper
description: Build an evidence-backed map of externally and internally reachable attack surfaces, trust boundaries, privileged transitions, security assets, and high-value audit targets before vulnerability hunting.
version: 1.0.0
---

# Attack Surface Mapper

## Mission

Create a prioritized, evidence-backed map of where attacker-controlled data, authority, value, and state enter or cross the system. This skill does not claim vulnerabilities. It produces an audit map and test hypotheses for downstream hunter agents.

## Inputs

- Source tree, architecture docs, deployment files, API schemas, smart contracts, protocol specs, configuration, and bounty policy.
- Optional target profile: Web2, smart contract, bridge, validator, wallet, node, cloud service, or mixed system.

## Non-negotiable rules

1. Every mapped surface must cite concrete evidence.
2. Distinguish externally reachable, authenticated, privileged, local-only, build-time, test-only, and dead paths.
3. Do not assume a route is public merely because a handler exists.
4. Do not equate dangerous functionality with a vulnerability.
5. Map default production behavior separately from optional or legacy configuration.
6. Respect scope and authorization constraints supplied by the policy agent.

## Workflow

### 1. Establish system inventory

Identify deployable components, processes, services, packages, contracts, workers, clients, validators, relayers, and operational tooling.

### 2. Enumerate entry points

Map:

- HTTP/RPC/WebSocket/GraphQL handlers;
- authentication, callback, webhook, upload, import, export, parser, and deserialization paths;
- queues, cron jobs, IPC, plugins, CLI and admin interfaces;
- smart-contract external/public functions and callback hooks;
- peer-to-peer messages, gossip, consensus votes, snapshots, ledger/replay inputs;
- bridge messages, oracle updates, signatures, proofs, governance calls;
- configuration, environment variables, secrets, and deployment manifests.

### 3. Track attacker-controlled data

For each entry point record:

- attacker class;
- authentication/authority required;
- input fields and size constraints;
- validation and canonicalization layers;
- parsers and state mutations reached;
- sinks and privileged operations;
- rate, timing, ordering, and replay properties.

### 4. Map trust boundaries

Mark transitions such as:

- unauthenticated → authenticated;
- user → tenant/admin;
- frontend → internal service;
- external network → parser/state machine;
- off-chain → on-chain;
- untrusted contract → callback-enabled protocol;
- peer message → consensus state;
- relayer/oracle/guardian → protocol authority;
- process/container → host/cloud control plane.

### 5. Identify assets and invariants

Assets include credentials, sessions, user data, tenant isolation, signing keys, funds, accounting state, governance authority, consensus safety/liveness, bridge custody, snapshots, and availability.

For each asset, state the invariant that must remain true.

### 6. Score audit priority

Use:

- reachability;
- attacker control;
- privilege/value crossed;
- parser/state complexity;
- composition and callback potential;
- novelty and historical bug density;
- recovery difficulty;
- production relevance.

Priority is for audit scheduling, not severity.

### 7. Produce hunter hypotheses

Generate narrow hypotheses such as:

> An unauthenticated peer can influence length and ordering fields before canonical validation, potentially reaching allocation or state-transition logic.

Avoid conclusions such as “remote DoS exists” until verified.

## Domain lenses

Read `references/domain-lenses.md` and apply only relevant sections.

## Output

Use `templates/attack-surface-map.yaml`. Include blind spots and inaccessible evidence. End with no more than ten prioritized hunter tasks.
