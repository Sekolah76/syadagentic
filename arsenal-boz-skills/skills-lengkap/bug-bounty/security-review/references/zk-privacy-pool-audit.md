# ZK Privacy Pool Audit Notes

Use these notes when auditing Rust/Solana privacy-pool code with Groth16, Poseidon, commitments, nullifiers, and wallet/prover settlement flows.

## Map The Surfaces First

- Circuit shape: public input order, private witnesses, amount bit/range constraints, dummy input conditions, Merkle path direction/index derivation.
- Host verifier: how request fields become public inputs; whether caller-supplied values are derived instead of trusted.
- On-chain verifier: public input order, byte endianness, field reductions, proof wire format, verifying-key IC length.
- Settlement path: nullifier uniqueness storage, output commitment append, root history acceptance, external value movement, fees/rewards.
- Prover/wallet boundary: proof encoding conversion, requested recipient/amount, ciphertexts that are not proof-bound, key path consistency.

## High-Signal Bug Classes

- **Public-input mismatch**: host verifies `[root, public_amount, ext_data_hash, asset, nfs, outputs]` but on-chain uses a different order, derives `public_amount` differently, hashes external data differently, or hardcodes a different asset.
- **Non-canonical field bytes**: proofs bind field elements while replay/nullifier PDAs/trees key raw bytes. Check every raw-byte identity value is canonical before proof verify and before storage.
- **Value conservation wrap**: all private input/output amounts and public signed amounts must be range-bounded small enough that field arithmetic cannot wrap into a satisfiable false balance.
- **Dummy input bypass**: if zero-amount dummies skip membership, prove they cannot carry value or make a negative public amount balance; dummy nullifiers should not reset co-sign/replay budgets.
- **Nullifier uniqueness gaps**: check pairwise distinctness inside a tx, cross-tx storage/PDA uniqueness, leaf-index binding, and whether duplicate commitments at different indexes intentionally produce different nullifiers.
- **Commitment mismatch**: deposit/on-chain commitment hash must match circuit/wallet Poseidon width, endianness, amount encoding, asset binding, and pubkey derivation.
- **Root authority mismatch**: settlement must accept only roots the program built or maintains, not operator/client-published roots.
- **Proof encoding split**: validators may verify compressed arkworks proofs while Solana consumes 256-byte alt_bn128 wire proofs; ensure conversion happens before settlement and cosigners sign the converted payload they matched.
- **Fee mismatch**: if external withdrawal pays `gross - fee`, the circuit should burn/prove the gross amount and accounting should later pay the fee from the retained vault balance.

## Reporting Discipline

- For user requests like "Critical/High only" or "reject weak leads," do not report safe checks or Medium/Low noise as findings.
- Use known-issue logs first; reject duplicates even when the current code still contains comments describing the old issue.
- If no separate wallet/prover source exists in the repo, state that scope limit rather than inventing a prover finding.
- A good non-finding is one sentence in coverage, not a finding card.
