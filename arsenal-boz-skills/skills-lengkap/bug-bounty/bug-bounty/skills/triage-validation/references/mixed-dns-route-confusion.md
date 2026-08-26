# Mixed-DNS Route-Confusion Validation

Use when one hostname resolves to multiple addresses and a proxy/VPN computes one routing decision for the whole vector.

## Core invariant

Each attempted destination must receive a route appropriate to that destination. A vector-level rule such as `any(excluded) => direct` is unsafe when the unfiltered vector is later attempted in resolver order.

## Minimal proof

1. Trace resolution into `Vec<SocketAddr>`.
2. Identify whether routing is per address or collapsed to one scalar decision.
3. Trace the exact vector passed to the connector.
4. Confirm connector order and fallback behavior.
5. Construct `[attacker_non_excluded, excluded]`.
6. Prove the scalar decision is direct/default-interface.
7. Prove the first non-excluded address remains first and is attempted under that decision.

A route-decision unit test alone proves the policy-collapse defect. It does not by itself prove packet-level clearnet exposure; require connector trace or an end-to-end packet capture for that stronger claim.

## Falsification attempts

Kill or downgrade if any holds:

- addresses are partitioned or filtered before connection;
- the route is recomputed for every attempted address;
- canonicalization removes the mixed answer;
- DNS is resolved elsewhere and the local vector is unreachable in production;
- firewall policy prevents the supposedly direct socket from leaving outside the tunnel;
- only client-side DNS is supported, so attacker-controlled multi-answer DNS never reaches this path;
- the feature explicitly promises whole-domain bypass and the claimed protected-address invariant is absent.

Do not kill merely because bypass is an opt-in feature. Compare the documented boundary: “excluded destinations bypass” differs from “any hostname containing one excluded address bypasses all returned addresses.”

## Test discipline

Rust test filters are substring-based over fully qualified names. `--exact` with only the leaf function name may run zero tests while returning success. Always verify output says `running 1 test` and `1 passed`; then replay at least three times on the release commit and current development head.

## NymVPN case note

Observed on public commits `1f49414c9093b4994c153a4e0936dd38613dbf39` (`nym-vpn-v2026.11.3`) and `8451edf32e23caedc50ee42bc525427913bf43e2` (`develop`, 2026-08-01):

- `decide_route_for_addrs` used `addrs.iter().any(db.is_excluded)` to select one `DefaultInterface` decision;
- `serve_socks5` passed the complete resolver-ordered vector unchanged to `connect_to_target`;
- `connect_to_target` attempted addresses sequentially under that one decision;
- `[93.184.216.34:443, 1.0.1.1:443]` therefore selected direct routing while retaining the non-excluded first destination;
- regression test passed 3/3 on both commits;
- public issue/PR keyword searches found no visible duplicate;
- an isolated Linux network-namespace harness created distinct tunnel/direct listeners, mapped Nym's real fwmark to the direct path, sent a real SOCKS5 domain CONNECT, and observed `control=TUNNEL` versus `poc=DIRECT` for the same non-excluded endpoint;
- the decisive harness was re-run against the untouched official `nym-vpn-v2026.11.3` binary after verifying the release archive's published SHA-256 and byte identity with a fresh extraction.

Intent evidence materially strengthened the verdict: UI wording says “Routes traffic for selected regions outside the VPN tunnel” and “Everything else stays protected,” while public PR #5872 explicitly treats direct routing of non-excluded traffic as a leak. Thus intended bypass for an excluded address does not authorize a non-excluded sibling to inherit direct routing.
