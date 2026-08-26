---
name: variant-discovery
description: Systematically search an authorized codebase or protocol for additional manifestations of a confirmed root cause while preventing duplicate inflation and preserving independent verification requirements.
version: 1.0.0
---

# Variant Discovery

## Mission

Given a confirmed or high-confidence root-cause fingerprint, identify semantically related manifestations across the target. Discover breadth without assuming every syntactic match is vulnerable.

## Required inputs

- Root-cause fingerprint.
- Confirmed vulnerable example.
- Relevant architecture and attack-surface map.
- Scope and repository revision.

## Search strategy

### 1. Extract semantic signature

Capture:

- violated invariant;
- missing/incorrect operation;
- attacker-controlled dimension;
- vulnerable data type or state transition;
- source and sink relationship;
- required context/configuration;
- remediation pattern.

### 2. Generate search families

Use multiple families:

- direct symbol/helper usage;
- sibling handlers and implementations;
- duplicated code and generated bindings;
- alternate parsers/serializers;
- inverse operations such as mint/burn, lock/unlock, encode/decode;
- lifecycle variants: create/update/delete, startup/runtime/restart/replay;
- boundary variants: single-tenant/cross-tenant, local/remote, on-chain/off-chain;
- data-shape variants: signed/unsigned, truncation, zero/max, empty/duplicate, canonical/noncanonical;
- protocol phase variants: epoch/round/view, source/destination chain, pre/post finality.

### 3. Screen candidates

For each match verify:

- attacker reachability;
- equivalent missing invariant;
- equivalent attacker control;
- relevant production path;
- absence of compensating guards;
- observable primitive;
- same or different remediation boundary.

### 4. Classify

- `CONFIRMED_VARIANT`: independently reproduced.
- `LIKELY_VARIANT`: equivalent path and invariant, reproduction pending.
- `STRUCTURAL_MATCH_ONLY`: syntax/pattern match without exploitability proof.
- `NOT_A_VARIANT`: different root cause or guard prevents issue.
- `SAME_MANIFESTATION`: duplicate path to the already known instance.

### 5. Avoid report inflation

Multiple variants are not automatically multiple bounty reports. Send them to Root Cause Analyzer for clustering. Prefer one report that demonstrates systemic breadth unless separate security boundaries, patches, or impacts justify separation.

### 6. Stop conditions

Stop expanding when:

- searches saturate with no new semantic matches;
- remaining matches are test/dead/generated code only;
- all uses are guarded;
- scope boundary is reached;
- evidence quality declines into speculation.

## Special domain patterns

Use `references/variant-patterns.md`.

## Output

Use `templates/variant-discovery.yaml`. Every confirmed or likely variant must include a verifier test specification.
