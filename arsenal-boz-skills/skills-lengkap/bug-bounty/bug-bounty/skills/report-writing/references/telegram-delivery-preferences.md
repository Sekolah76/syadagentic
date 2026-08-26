# Telegram Direct-Delivery Report Preferences (this user)

Hard preferences this user enforces on security reports delivered via Telegram.
Violating any of these gets flagged and re-worked. Apply to ALL deliverables
(report body, file names, titles, headings).

## 1. No severity labels
Strip severity words entirely: Critical, High, Medium, Low, Info, P0/P1/P2.
Do not put them in the report body, title, or file names. If you must convey
impact, describe it in plain words ("full reserve drain", "unlimited mint")
instead of a severity word. Only add severity if the user explicitly authorizes.

## 2. No symbols / decorative punctuation
Rejected: em-dash `—`, en-dash `–`, arrows `→`/`->`, and similar decorative
marks in report prose.
- "SVP Chain — Security Review" → "SVP Chain, Security Review"
- "Finding 1 — ..." → "Finding 1: ..."
- "Why not Critical:" → "Impact ceiling:"
Plain hyphen `-` inside code/identifiers is fine; the ban is on prose
punctuation marks.

## 3. No internal status notes in the deliverable
Never ship work-in-progress framing in a final report:
- "not yet reviewed"
- "blocked by X"
- "marked for follow-up"
- "output encoding limit"
If something wasn't reviewed, either review it or drop it from the report.
Keep internal audit gaps in a separate `submission-notes.md`, never in the
report body. The user explicitly caught and removed "not yet reviewed".

## 4. Verify before delivering
After editing, grep the report and confirm zero hits before sending:

```
grep -nE 'Critical|Medium|Low|High|Info|severity|—|–|→|->' <report>
```

Expect empty output (exit 1). The user WILL re-check and flag any leftover,
so this grep is mandatory, not optional.

## 5. Standalone PoC
Proof of Concept goes in a separate file (`.sol`, `.t.sol`, `.py`), never
embedded in the report markdown. Include a short README with run steps.

## 6. Concise summary
Accompany files with a 2-3 line executive summary of the finding.

## 7. File delivery
Prefer sending files individually via `MEDIA:/path`. Zip only when explicitly
requested or when handling 5+ files.

## Form-submission field mapping
When the user pastes a bounty submission form ("1. Affected Scope, 2.
Vulnerability Description, 3. PoC, 4. Times date"), map directly:
- Affected Scope: repo + file paths
- Vulnerability Description: root cause + impact (plain words, no severity)
- PoC: path to the standalone PoC file + reproduction steps
- Times date: submission date (YYYY-MM-DD)
Write in the user's requested language (they switch EN/ID — match them).
