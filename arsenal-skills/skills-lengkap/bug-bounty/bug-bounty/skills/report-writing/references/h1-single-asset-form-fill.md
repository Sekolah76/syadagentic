# H1 single-asset form fill (SourceCode / multi-repo programs)

## When this applies

HackerOne (and similar) **SourceCode** programs that list multiple GitHub trees as separate assets and force **exactly one asset per report**.

Classic trap: two findings share final **Medium** severity → combined internal package looks clean → H1 UI still requires one asset → must **split at submit time**.

## Hard rules

1. **Severity equality ≠ one report.** Same severity band is not the same H1 ticket if assets differ.
2. **Root-cause asset wins.** Select the in-scope tree where the defective code lives.
   - Validation in `inference-chain/x/inference` → that asset (even if dial clients are OOS).
   - Missing auth in `mlnode` → `mlnode`.
   - Never pick Bridge/devshard only because the UI labels them Critical-eligible.
3. **Impact may cite OOS callers** (TA, `decentralized-api`) for chain-of-effect — do **not** select OOS as the asset.
4. **Submit order** for multiple Mediums: cleaner unauth/control story first; DNS/validation second.
5. **Combined markdown on disk is fine** as internal packaging; H1 body must be per-asset.

## Form-fill coaching pattern

User pastes field labels one-by-one (`Description*`, etc.). Answer with ready-to-paste blocks:

| Field | Content |
|-------|---------|
| Title | one line, formula |
| Asset | exact tree URL / name |
| Severity | final non-hedged tier |
| Weakness | primary CWE unless multi-select |
| Description | Vulnerability + Steps + Impact + Fix |
| Impact (if separate) | 3–5 sentences, program bar explicit |
| Attachments | main PoC → output capture → optional alt |

Do not dump multi-finding disposition into a single Description field.

## Attachment delivery (Telegram / chat)

- Prefer `MEDIA:/abs/path` for `.md` and evidence.
- If `.py` fails client download: immediately provide **secret gist** + **tar.gz** (do not only re-MEDIA the same `.py`).
- Never put `$` bounty amounts in gist descriptions or PoC files.
- Keep finding-scoped files only in each ticket.

## Gonka 4-asset map (still useful)

| Asset | Typical classes that belong |
|-------|-----------------------------|
| BridgeContract.sol | On-chain bridge only |
| devshard | Devshard only |
| inference-chain/x/inference | Msg validation, URL SSRF filter, module logic |
| mlnode | FastAPI management, PoW Sender callback |
| OOS (never select) | `decentralized-api` as root cause |

## Severity language

Always non-ambiguous final tier. Pattern: *"langsung aja severity finalnya apa, jangan ambigu"* → write **Medium** / **Informational** / **DO NOT SUBMIT**, never "tempered / maybe".

Under network-perspective programs: single-node unauth control and incomplete SSRF validation both map **Medium**; do not upsell High without network-wide proof.
