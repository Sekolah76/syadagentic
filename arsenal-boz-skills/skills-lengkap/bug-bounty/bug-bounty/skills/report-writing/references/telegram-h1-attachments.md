# Telegram → H1 attachment delivery

## Trigger phrases

- `kirim attachment untuk G2/G4`
- `kirim juga yang ini <file.py>`
- `ngga bisa di download`

## Per-ticket priority

| # | Artifact | Required? |
|---|----------|-----------|
| 1 | Main static PoC (`.py`) | **Yes** |
| 2 | Fresh PoC stdout (`*_poc_output.txt`) | **Yes** |
| 3 | Optional live script (`.sh` / `.go`) | Optional |
| 4 | Packaged report (`G*-H1.md`) | Optional if Description already pasted |
| 5 | Bundle (`*.tar.gz`) | When Telegram blocks individual files |

**Finding-scoped only.** G2 ticket never gets `g4_*` or `g2_g4_combined_*` (and vice versa).
H1 single-asset programs: one asset tree per report — see `h1-single-asset-form-fill.md`.

## Delivery sequence

1. Stage short-path copies under `/home/ubuntu/` + keep originals under `findings/` / `pocs/`.
2. First attempt: `MEDIA:/abs/path` for each required file.
3. If user reports download failure (especially **`.py`**):
   - Immediately create a **secret** GitHub gist (`public: false`) with py + output (+ optional alt).
   - Also `MEDIA:` a **`tar.gz`** of the same set.
   - **Do not** only re-MEDIA the same `.py` and stop.
4. Paste gist URL + raw link in chat; H1 Supporting material may use the gist URL.

## Gist hygiene

- No `$` bounty amounts or payout tables in gist description/content.
- Never print GH tokens; use existing token patterns without logging them.
- Prefer secret gists over public.

## Form-fill coaching (companion)

User pastes H1 field labels one-by-one or mid-stream corrects
(`eh salah maksud aku G2`): re-anchor immediately; answer with
**copy-paste field blocks only**. Details: `h1-single-asset-form-fill.md`.

## Intigriti (non-H1) submit package via Telegram

When user says **submit dulu** on an Intigriti program:

1. Build `findings/<brand>-<bug-class>/` with `intigriti-report.md`, `PASTE_FIELDS.txt`, `submission-notes.md`, `evidence/`.
2. `tar -czf findings/<brand>-<bug-class>.tar.gz` that folder.
3. Deliver: `MEDIA:` report + PASTE_FIELDS + notes + tar.gz (prefer tar if many JSON PoCs).
4. Do **not** claim agent can submit on Intigriti web — paste package only.
5. Capability-URL cart BAC specifics: `capability-url-cart-bac-intigriti.md`.
