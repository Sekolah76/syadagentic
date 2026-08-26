# Manual Web Form Submission — HackenProof-Style Platforms

When a bug bounty platform uses web forms (not GitHub API), submission requires human interaction. This reference documents the workflow for handling that friction without losing submission quality.

## When to Use

- Platform uses web form for submission (HackenProof, HackerOne, Bugcrowd, Intigriti)
- No public API for submission
- You're an AI agent who can't directly fill the form

## The Friction Problem

You **can't** submit directly because:
- Login requires password + 2FA you don't have
- Form needs paste of markdown + file upload
- Each submission is 5-10 minutes of human work

If you try to work around it with hacks (creating a gist the user can download, etc.), the user gets frustrated. They explicitly said:

> "udah woi ngapain bikin gist, kan udah lu kirim tadi filenya"

The lesson: **deliver the file, don't create extra artifacts.**

## The Correct Workflow

### Step 1: Write findings as `.md` files locally

```python
write_file('/home/ubuntu/<target>_report_1_<severity>_<short-name>.md', body)
write_file('/home/ubuntu/<target>_poc_<short-name>.md', poc_content)
```

Path on the user's machine. The file is **directly accessible** if the user is on the same machine, or downloadable via `MEDIA:/path/to/file.md` for Telegram-style delivery.

### Step 2: Display the full markdown inline in chat

After the file is saved, **also paste the markdown content into the chat** so the user can copy-paste without leaving the conversation. Both:
- Save to file (for download)
- Display in chat (for copy-paste)

### Step 3: When the user is on the form, give the short form

For HackenProof specifically, the form has structured fields:

| Form Field | What to paste |
|---|---|
| Title | `[Severity] Short description` |
| Category | `Server Security Misconfiguration` (search "misc") |
| Vulnerability details | Full markdown body |
| Validation steps | Short numbered reproduction steps |
| Severity | Dropdown |
| Supporting files | The `.md` file you saved |

Give the user **just the fields, in order**, with the actual content to paste. Don't make them scroll through a long report.

### Step 4: When the user reports a blocker, help them through it

If they hit a form field they don't understand (e.g. "what's CVSS score?"), give them the answer directly, don't tell them to look it up.

## Out-of-Scope Submissions — Don't Submit

If you discover a finding that turns out to be out of scope, **DO NOT submit it**.

In the Bitkub case, `*.internal.bbtserv.io` was technically valid security-wise (internal subdomains publicly resolvable) but `bbtserv.io` is the parent company, not in Bitkub's target list. Submitting would:
- Waste the user's review time
- Damage reputation (looks like you didn't read scope)
- Potentially get flagged as a low-quality hunter

**Always check the exact target domains in the program's scope section before submitting.**

## What to Tell the User

When the platform requires web submission, be **direct and brief**:

> "Lo lagi di Step 2 [Category]. Pilih: 'Server Security Misconfiguration' (search 'misc')."

Not:

> "There are several approaches you could take here, including the option of..."

Be a co-pilot, not a lecturer. The user is in flow on the form, give them the field and move on.

## Pitfalls to Avoid

- **Don't create gists, IPFS uploads, or other workarounds** — the user has the file, just deliver it
- **Don't paste 50+ line files inline only** — save to file AND show inline
- **Don't explain how to copy-paste from chat** — they know
- **Don't apologize or moralize about platform limitations** — just adapt
- **Don't submit findings outside the program's stated scope** — even if technically valid

## Verified Pattern

This workflow was used to submit 4 manual findings (2 EVAA + 2 Bitkub equivalent) in one session without friction. The user was able to complete each submission in under 5 minutes after receiving the field-by-field content.

## Quality-Gate the Submission Before You Tell the User to Paste

Before pasting any report into a form, run a final pass against these checks:

- [ ] Title includes severity tag `[Critical|High|Medium|Low/Info]` and the bug class (e.g. `[High] XSS in /api/users`)
- [ ] At least one `file:line` reference in the body (paste-friendly, not deep markdown anchors)
- [ ] Steps to Reproduce are 3-5 numbered lines that a triager can paste into curl/Postman
- [ ] Impact section is 1-3 sentences, not a wall of text
- [ ] Severity in the dropdown matches the title tag
- [ ] If the form has a "category" field, choose the **most general** option that applies (e.g. "Server Security Misconfiguration" not "Server Misconfiguration > Email")
- [ ] If the form has a "bug class" multi-select, tick at most 1-2 boxes — picking everything signals low-quality
- [ ] If PoC is required, attach the `.md` PoC file you wrote in Step 1, not a screenshot

Triagers triage in seconds. Reports that look polished get triaged first.

## Submission-Friction Workarounds the User Rejected

Don't try these. User explicitly said "oke" then "udah woi" (rough: "alright, stop it"):

- Creating a public GitHub Gist for the user to download — user said "ngapain bikin gist, kan udah lu kirim tadi filenya"
- Copy-pasting file content in chat 3+ times after they already saw it — they have it
- Generating IPFS pin / 0x0.st URL for the PoC — they can read local files
- Building a "submission helper" script — over-engineering for a 5-min form

The principle: **the user is at the form, give them fields, not artifacts.**
