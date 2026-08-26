# Breaking TEE-Encrypted (ECIES) Perps DEX APIs

Reverse-engineering an API where every state-changing request is ECIES-encrypted to a
Nitro/SGX enclave, with EIP-712 signatures inside the encrypted payload. Validated on
Opal DEX (`api.opaldex.com`, Base chain, Rust Nitro enclave).

## The architecture

```
client ── ECIES(secp256k1→AES-256-GCM) ──> enclave public key
         POST {encrypted_payload, user_id}
enclave decrypts → validates EIP-712 signature → executes → returns
```

Auth is **two-layer**:
1. **Session registration**: user wallet signs `AuthorizeSession` (EIP-712) → `/perps/session/register` → returns session key
2. **Per-request**: session key signs endpoint-specific typed data (BalanceQuery, OrderSubmit...) → ECIES-encrypt → POST

## Step 1 — Find enclave public key

From JS bundles, look for `getPublicKey` / `encrypted_endpoints`:

```bash
grep -oE 'getPublicKey[^)]{0,60}' chunk_*.js
grep -oE 'encrypted_endpoints.{0,300}' chunk_*.js
```

Probe (usually needs a `timestamp` field):

```bash
curl -X POST https://api.target.com/perps/public-key \
  -H "Content-Type: application/json" \
  -d "{\"timestamp\": $(date +%s)}"
```

Returns `{public_key, key_type, key_id, supports_ecies, encrypted_endpoints[]}`.

## Step 2 — Match ECIES config in Python

The JS client uses a specific ECIES config. Extract it:

```bash
grep -oE 'ECIES_CONFIG.{0,300}' chunk_*.js
grep -oE 'isEphemeralKeyCompressed[^,;]{0,60}' chunk_*.js
```

Config fields that matter: `ellipticCurve`, `isEphemeralKeyCompressed`,
`symmetricAlgorithm`, `symmetricNonceLength`, `aeadTagLength`.

Python match with `eciespy`:

```python
from ecies import encrypt
from ecies.config import Config

config = Config(
    is_ephemeral_key_compressed=False,   # match JS: 0x04 prefix (65 bytes)
    is_hkdf_key_compressed=False,
    symmetric_algorithm="aes-256-gcm",
    symmetric_nonce_length=16,
)
enc = "0x" + encrypt(PUBKEY, json.dumps(payload).encode(), config=config).hex()
```

**Verify config match**: POST garbage payload. If error changes from
`Failed to decrypt request with ECIES` → `Failed to parse decrypted JSON payload`,
your ECIES config is correct. The parse error even leaks the Rust struct name
(`opal_nitro_enclave::services::gateway_types::BalanceRequest`) — free architecture intel.

## Step 3 — Crack EIP-712 domain

```bash
grep -oE 'name:"[^"]+",version:"[^"]+".{0,200}' chunk_*.js
grep -oE 'F=\{[^}]{0,600}' chunk_*.js        # chainId → contract map
grep -oE '\.(E|Z)=\(0,f\.x\)\(.{0,300}' chunk_*.js   # chain defs
```

**Pitfall**: `verifyingContract` differs per chain. Opal had
`F[Base]=0xccf733...` but `NEXT_PUBLIC_MARGIN_VAULT_ADDRESS=0x1Ec92c...` was for
Sepolia. Using the wrong contract → "Authorization signature verification failed".
Read the `F[chainId]` mapping, don't trust a single hardcoded address.

## Step 4 — Session registration

`AuthorizeSession` typed data fields (from JS):
`{action, sessionKey, userAddress, expiresAt, nonce}`.

- `action` string is exact — Opal used `"authorize_session"`, not `"session_authorization"`. Get it from JS, don't guess.
- `expiresAt`/`nonce` values in the signed message MUST equal the JSON body fields exactly.
- Addresses: enclave may require **lowercase** only (checksummed → "Address checksum mismatch").
- `expiresAt = now + 604800` (7 days) worked.

Register returns `{success, session_key, expires_at}`.

## Step 5 — Per-request typed data + IDOR test

Each endpoint has its own typed data type (BalanceQuery = `{user_id, nonce}`,
MoveToWithdrawal = `{user_id, amount, nonce}`, etc). Sign with **session key**, ECIES-encrypt, POST.

**IDOR test** (the key security question):
- Sign BalanceQuery for SELF, but set body `user_id` = VICTIM
- If response `data.user_id` == SELF → server uses **signed** user_id from decrypted payload (secure)
- If response `data.user_id` == VICTIM → **IDOR** (server uses body user_id for lookup)

Opal was **secure**: body user_id ignored for lookup, signed user_id used. Don't assume
TEE = broken; verify which user_id source drives the query.

## Step 6 — Write-path / withdrawal

`moveToWithdrawal` is **two-phase**: API returns a *permit signature*
(`{gross_amount, nonce, signature}`), then client submits on-chain
`moveToWithdrawal(user, amount, nonce, sig)` to the vault contract. Check both the
API and the contract for replay/nonce-increment bugs.

## Replay

Read-only queries replay fine (harmless). For write-path, check whether the enclave
tracks nonces to prevent replay of the same signed withdrawal.

## Tooling

- `eciespy` (Python) — ECIES encrypt/decrypt, configurable
- `eth_account` — EIP-712 signing (`encode_typed_data`)
- `coincurve` / `pycryptodome` — manual ECIES if eciespy config insufficient
