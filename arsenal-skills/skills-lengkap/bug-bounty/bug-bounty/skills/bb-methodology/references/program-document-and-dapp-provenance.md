# Program-document intake and first-party dApp provenance

Use this when a bounty program is published in a public document rather than a platform page, or when a dApp’s live contract set must be derived from its frontend.

## 1. Preserve the policy as evidence

1. Obtain an immutable local snapshot of the published policy before testing. For a publicly shared Google Doc, its `.../document/d/<id>/export?format=txt` endpoint is a practical text snapshot.
2. Extract, verbatim where relevant: in-scope host patterns, explicit exclusions, allowed proof methods, prohibited actions, report channel, reward dates, and rate limits.
3. Flag unresolved placeholders (for example, `[insert start date]`) as a **program-status caveat**, not permission to infer dates/rewards.
4. Create a `SCOPE_FENCE.md` before the first request to target systems.

## 2. Establish live first-party provenance

Do not accept an address just because it appears in an explorer, social post, or a stale repository manifest.

Preferred evidence order:

1. Public official site route or served JS bundle points to a first-party API/contract configuration.
2. The first-party API or indexer returns a chain ID + contract address/deployment record.
3. Runtime bytecode, verified source, and deployment transaction are checked per chain.
4. The contract’s role is established (mint, payment, claim, governance, etc.) before assigning a vulnerability class or impact.

Record a provenance matrix:

| Contract | Chain ID | First-party binding | Runtime/source evidence | Role confirmed? |
|---|---:|---|---|---|

A contract appearing identically across chains may be a governance/omnichain deployment, not necessarily a mint/payment contract. Do not broaden its role without evidence.

## 3. Public GraphQL indexers

A first-party GraphQL/GraphiQL endpoint can legitimately expose public indexed on-chain data and schema introspection. Treat the following as mapping evidence, **not findings**:

- GraphiQL/Playground enabled
- introspection enabled
- read-only query schema
- public on-chain fields such as addresses, transaction hashes, token IDs, or vote records
- permissive CORS on an endpoint serving only public data

Safe mapping sequence:

1. Query minimal `__schema` metadata first to determine query/mutation availability.
2. Inspect only type definitions needed to locate contract/deployment fields.
3. If needed, request the minimum public deployment fields (e.g. `chainId`, `contractAddress`, deploy transaction) without collecting user-linked data.
4. Stop treating GraphQL as the primary target unless it exposes mutation, non-public data, authorization boundaries, or a concrete confidentiality/integrity impact.

## 4. Contract validation boundary

For a contract candidate derived this way, use static analysis and a pinned local fork. Never run a proof that moves/mints/burns/freezes real assets unless the program explicitly permits it; most public programs prohibit that behavior even where the contract is in scope.
