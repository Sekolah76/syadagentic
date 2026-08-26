# Distributed Validators (off-chain middleware)

## Protocol Overview
Distributed Validator (DV) middleware clients that split a single Ethereum validator key into threshold-BLS shares across N independent operator nodes, performing consensus on duties (attestations, block proposals, exits) before aggregating threshold signatures to the beacon chain. Examples: **Obol Charon** (Go), **ssv.network** (Go), **Lido Simple DVT module**. Differs from "Liquid Staking" playbooks in that there is no on-chain custody contract to audit — the entire security boundary is the off-chain Go codebase, the libp2p/p2p transport, the DKG ceremony, and any operator-to-API integrations (e.g. Obol API for exit aggregation).

## Trust Assumptions
- **Operator ENRs / pubkeys are trusted at the cluster-lock level.** A malicious operator ENR is a malicious peer. Don't re-derive "who can we trust" from scratch — start from the lock file and treat every divergence as a finding.
- **Threshold trust.** Loss of `t` shares (where `t` is the threshold, typically 3-of-4 or 5-of-7) loses the ability to sign for the validator. Bribery/coercion of `t` operators is the threat model, not 51%-of-stake like L1.
- **Transport trust root is usually a libp2p connection gater, not application-layer auth.** This is the most important mental model flip from on-chain audits — the **conn gater is the trust root**, the handler is a defense-in-depth layer.

## Critical Invariants
- **No single operator share can sign alone.** Threshold signature aggregation must reject `< t` partials.
- **DKG output (validator key share) is identical across all honest operators.** Byzantine agreement on the resulting pubkey.
- **Private share never leaves its operator node in plaintext.** The single most common Critical-tier finding pattern.
- **Cluster lock is unforgeable.** Lock hash + ENR signatures bind the validator to the operator set.
- **Slashing protection is enforced before any aggregation is broadcast.** A duplicate attestation is fatal to the validator's stake.

## Attack Surface
This is the part that diverges most from on-chain audits.

| Surface | What to look for |
|---|---|
| **p2p/ transport (libp2p)** | Connection gater allowlist (relays vs cluster peers), QUIC vs TCP defaults, NAT hole-punch, peer store TTL |
| **DKG ceremony** | FROST / Pedersen message handlers — do they verify `peerID ∈ PeerMap`? Session ID binding? Signer dedup? |
| **QBFT / consensus instances** | Signer index is part of signed payload; ensure pubkey recovery is bound to expected peer pubkey |
| **BLS partial signature exchange (`parsigex`)** | Threshold gating, share-index validation, per-dedup-key dedup |
| **Obol API / operator-facing services** | Auth bearer scheme (typically k1 signature over `lockHash \|\| valPubkey \|\| shareIdx`); HTTPS enforcement |
| **Validator API (vAPI)** | Localhost binding, TLS cert mode, what subset of beacon-node endpoints are reverse-proxied |
| **Keymanager export (HTTP)** | **Highest-frequency Critical finding class** — see pitfall below |
| **Debug/pprof HTTP** | Default-deny binding; confirm `--debug-address` defaults to empty |
| **Process-level** | Lock file for private key (`*.lock`), file permissions on keystores, `privkeylock` grace period |
| **CLI flag handling** | `--no-verify` bypasses lock verification; `--allow-incomplete-keystores`; `--unsafe-*` flags |

## Audit Workflow
1. **Map the cluster lock format first.** Cluster lock is the source of truth — every other component derives trust from it. Find the verification function and walk backward: who calls it, who can disable it (`--no-verify`).
2. **Identify the trust root per protocol surface.** Conn gater for p2p, lock-file signature for cluster membership, k1 secp256k1 for Obol API bearers. **Each surface should have exactly one trust root; redundant checks are not the goal, but defense-in-depth at the handler layer IS.** (See pitfall #1 below.)
3. **Read the conn gater first.** `p2p/gater.go` (or equivalent). This single file tells you 80% of the trust model: which peer IDs can connect, whether relays are trusted, whether the gater is optional (`open: true` is a red flag).
4. **Walk every registered libp2p protocol handler.** For each, ask: does the handler trust `s.Conn().RemotePeer()` as the auth check, or does it re-verify against the cluster lock / session ID / peer pubkey? Gater-trust-only is fine, but flag missing checks.
5. **For DKG: read the message handlers, not the protocol spec.** Look for: `peerID` membership check, `SessionID` binding, sign-of-message-equal-to-dedup, threshold enforcement. The Kyber / FROST library does the crypto correctly — bugs are at the binding layer.
6. **For Obol API / external HTTP: trace the bearer scheme.** Is it `lockHash || valPubkey || shareIdx` (good) or just `shareIdx` (bad — shareIndex is not a secret)? Is HTTPS enforced or warned?
7. **For keymanager export: find the keystore write path and check scheme enforcement.** Look for `url.Parse(...).Scheme == "http"` handling. If it only logs a warning, that's a finding.
8. **For vAPI: confirm the default bind address is loopback.** `127.0.0.1:3600` is safe; `0.0.0.0:3600` is a finding unless the operator has explicitly chosen it.

## High-Risk Components
- **DKG round 1 (commitment + secret share)**: peerID-vs-PeerMap validation; share-index validation; commitment count check vs threshold.
- **DKG round 2 (signature share)**: same checks; FROST signature share size validation.
- **Parsigex broadcast**: dedup per `(peerID, msgID)`; verifyFunc must actually verify (not no-op in production).
- **QBFT round-change and prepare messages**: signature recovery must bind to a known cluster pubkey.
- **Keymanager import**: scheme must be hard-rejected at https or behind an explicit opt-in.
- **Obol API exit fetch**: aggregation must BLS-verify each returned partial against the local pubshare set — never trust the API's positional ordering.
- **Cluster lock modification (`charon edit ...`)**: re-authorization required; grace period for new lock hash; ensure operators can detect a lock swap.

## BLS Keystore Export over HTTP — the #1 Critical Pattern
This single class of finding recurs across DV middleware (Charon, ssv.network, possibly web3signer) and validator clients (lighthouse VC, teku VC, prysm VC). The pattern:

1. A flag accepts an HTTPS-or-HTTP URL for "remote keystore import" / "remote keymanager" / "remote signer."
2. The code only checks `Scheme == "http"` in a warning log, never hard-fails.
3. The key share is uploaded to that URL using EIP-2335 keystore format.
4. **The decryption password is generated locally and sent in the same POST body** (because the remote endpoint needs it to load the keystore).
5. An attacker who can MITM the path (DNS rebinding, ARP, route hijack) or control the URL (e.g. via a config the user trusts but the attacker tampers) gets both the keystore and the password in one shot.

**Severity rule**: any successful exfil of a BLS private key share on a DV protocol is **Critical** by default on Immunefi/Obol-style bounties. Threshold + the operator's own share often equals the full key once `t` operators' shares are aggregated.

**Detection signature**:
```bash
# Find all URL-accepting flags in DV middleware
grep -rn 'flag.*"http' cmd/ | grep -iE 'keymanager|signer|remote|import|upload|export|webhook'
# Find scheme handling
grep -rn 'Scheme == "http"\|.Scheme != "https"' --include='*.go'
# Find the keystore POST path
grep -rn 'PostPartial\|ImportKeystores\|ImportRemote\|UploadKeystore' --include='*.go'
```

**Suggested fix template**: refuse to start if `Scheme == "http"` unless an explicit `--insecure-keymanager` (or analogous) flag is also set. Confirm the code does this — don't assume it does just because the code path exists.

## Pitfalls
1. **Gater-trust-only is NOT a finding by itself, but missing defense-in-depth IS.** If handlers re-validate `peerID ∈ PeerMap`, that's good. If they don't, that's still probably fine — but flag it as Medium/info. Do NOT flag it as Critical unless you can show a concrete path where the gater fails open.
2. **Don't re-derive trust from scratch.** Off-chain audits of DV middleware are 80% following what's already enforced. Spend the audit time on what's *not* enforced (e.g. keymanager URL scheme, Obol API bearer field, DKG handler peerID check).
3. **Iteration budget is tight — batch tool calls.** The 8-phase bughunter methodology is calibrated for Solidity where one call reads 1000 lines. For Go, the equivalent depth requires more `cat`/`grep`/`read_file` calls. **Plan to load 3-5 files in parallel per round-trip.** Don't sequentially `cat file.go` then `cat other.go` — batch them.
4. **Default-bind-address is the most under-checked class.** A vAPI bound to `0.0.0.0` instead of `127.0.0.1` is unauthenticated remote validator API access. Always grep for the default value of the bind flag.
5. **Don't over-trust signature recovery.** `ecdsa.RecoverCompact` returning a pubkey is not the same as that pubkey being a valid cluster member. The check is `recovered.IsEqual(pubkeys[msg.GetPeerIdx()])` — the indexed lookup is part of the trust model.
6. **`newP2PCallback` and `newBcastCallback` are the highest-leverage files in DV middleware.** They sit at the trust boundary. Read them first, not last.
7. **Recent commits are signal, not noise.** If a commit message says "fix X" and X is a security-flavored class, that X is now a known bug class. The fix is informative; the *original flaw* may have variants in adjacent code.

## Related Pack A Patterns
- `attack-patterns-batch1-common/access_control.md` (peer allowlist logic)
- `attack-patterns-batch1-common/signature_replay.md` (Obol API bearers, QBFT msg signing)
- `attack-patterns-batch1-common/arbitrary_call.md` (DKG message injection if handler lacks peerID check)

## Related Pack B Knowledge
- Liquid Staking exploits (Lido, Rocket Pool) — same threshold-loss threat model.
- Bridge message-replay / message-validation (cross-chain audit patterns apply to DKG message handling).

## Exit Criteria
- Conn gater allowlist is mapped, including the relay-trust decision.
- Every registered libp2p protocol handler is read and its trust model is one of: gater-only (acceptable), gater-plus-handler-check (defense-in-depth), or hard-fail (only if external unauth is impossible).
- DKG message handlers all validate peerID + SessionID + message-level invariants.
- Obol API bearers are mapped to their exact data fields and verified to be unguessable.
- Keymanager URL scheme handling is verified to hard-reject HTTP, not warn.
- vAPI default bind is verified to be loopback.
- Findings include file:line, PoC sketch, severity with $ justification.
