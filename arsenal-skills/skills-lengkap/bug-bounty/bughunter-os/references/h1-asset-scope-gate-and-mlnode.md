# H1 asset-list scope gate + MLNode control-plane hunt

Proven on Gonka H1 re-hunt (2026-07-19): user provided **exact 4 SourceCode assets** (Critical · Eligible). Directive: *ini in scope, selain itu out scope, hunting ulang*.

## 1. Strict asset-list scope gate (do this before packaging)

When the program (or user image) lists **specific repo paths**, treat that list as the **only** eligible roots:

1. Copy full URLs/paths from the asset UI/image into the session note.
2. Map each path on disk (watch spelling typos, e.g. `ethereum-bridge-contact` not `contract`).
3. For every candidate finding, answer: **primary vulnerable root ∈ list?**
   - Yes → package under that asset.
   - No (even if secondary call into in-scope code) → **OOS for this H1**; park.
4. Do **not** map findings to the wrong asset to force eligibility.
5. Prior findings whose primary root is OOS stay parked even if impact looks strong (e.g. Gonka G1/G3 → `decentralized-api` OOS; G2 → `inference-chain/x/inference` OK).
6. Re-hunt = deep audit **only** listed roots; exclude known already-filed bugs from “new” (e.g. G2 DNS SSRF).

### Severity still uses program formula

```
Risk = Impact × Likelihood
Impact = network perspective
High/Critical ⇒ network-wide
Single participant/node ⇒ usually Low/Medium
```

Scope eligibility ≠ severity uplift. Single-node unauth on an in-scope asset is still **Medium** under network bar.

### Admin-only / centralization on bridges

Comment/docs claiming “prior-epoch validation signature” while `setGroupKey` is `onlyOwner` + `ADMIN_CONTROL` with **no BLS verify** is a **doc/code gap + admin centralization**, not unauth fund drain. File only if:

- unauth / compromised-non-owner path exists, **or**
- program explicitly rewards admin key centralization as High (rare), **or**
- timeout → ADMIN_CONTROL enables network-critical theft without intended ops.

Otherwise: residual note, do not claim High “missing transition sig” alone.

## 2. MLNode / FastAPI worker control-plane checklist

Target class: GPU/ML worker packages (`mlnode`, similar FastAPI + uvicorn + nginx reverse proxy) published next to join-node compose.

### Hunt order

| Step | What to prove |
|------|----------------|
| A | App wiring: `include_router` + global middleware — any `APIKey` / `HTTPBearer` / `Depends(auth)`? |
| B | Conflict middleware only (`check_service_conflicts`) ≠ auth |
| C | Mutating routes: `/stop`, `/inference/down|up`, `/pow/init*`, `/models/delete|download`, pow_v2 stop/generate |
| D | Client-controlled **callback URL** field (`url: str` on init body) |
| E | Server process dials that URL (`requests.post(f"{self.url}/generated")`) with **no allowlist / SSRF filter** |
| F | Deploy likelihood: `uvicorn --host=0.0.0.0` + compose `ports: "8080:8080"` + nginx `location /` → worker with no auth |

### Impact matrix (network perspective)

| Claim | Cap |
|-------|-----|
| Unauth stop inference/PoW on **one** host | Medium |
| Attacker URL → node-originated SSRF / batch exfil | Medium |
| GPU/model download DoS on one host | Medium (local cost) |
| Forge **on-chain** votes without node key / other assets | usually needs OOS API path — do not claim from mlnode alone |
| Network-wide consensus failure | No → not High |

### Static PoC matrix (no live node / no `go`)

Build a Python scanner over the asset tree that asserts PASS/FAIL for:

1. app.py: no auth dependency symbols on routers
2. service_management: conflict-only
3. `/stop` registered
4. `PowInitRequestUrl.url: str` (or equivalent)
5. Sender posts to `{url}/generated` and `{url}/validated` without allowlist
6. manager wires `init_request.url` into Sender
7. pow init routes exist
8. inference down unauth
9. models delete unauth
10. pow_v2 routes unauth

Ship: `G*-H1.md` + `pocs/g*_static.py` (matrix) + `pocs/g*_control.sh` (live curl).

Gold evidence: unit tests that hit `/api/v1/...` with plain HTTP and no credentials.

### Pitfalls

- Do not attribute decentralized-api `:9100` unauth (different asset) as mlnode finding.
- nginx may also proxy `/v1` inference — still separate management `/api/v1` surface.
- Optional `url` is only SSRF if **server-side** fetch proven (Sender/manager), not mere pass-through JSON.
- Prefer `rg`/`sed` line ranges; full Path dumps often truncate mid-audit.

## 3. Package shape after re-hunt

```
findings/G*-H1.md              # one per verified in-scope finding
findings/*-REHUNT-*.md         # scope gate + residual table + submit map
pocs/g*_static.py              # offline matrix
pocs/g*_control.sh             # live curl
```

Submit map columns: Finding | H1 asset path | Action (ready / OOS park / residual).

Report body: Impact × Likelihood table; **no** verifier hedge / “needs more evidence” language.
