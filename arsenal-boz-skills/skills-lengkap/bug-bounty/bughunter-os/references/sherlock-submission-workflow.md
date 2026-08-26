# Sherlock Submission — Verified Workflow

Proven workflow for submitting findings to Sherlock audit contests as GitHub Issues. Validated against Metric OMM Pool contest (Jul 2026), 14 findings successfully submitted in a single session.

## When to Use

- You're auditing a Sherlock contest and ready to file a finding
- You have a remote Git URL with a PAT embedded (e.g. `https://ghp_xxxx@github.com/sherlock-audit/<contest>.git`)
- The contest uses GitHub Issues for submission (most Sherlock contests do)

## The Workflow (End-to-End)

### 1. Extract PAT from git remote (if not already known)

```bash
git remote get-url origin  # in contest repo dir
# Returns: https://ghp_XXXXX@github.com/sherlock-audit/2026-07-xxx.git
# PAT is the substring between https:// and @
```

In Python:

```python
import re, subprocess
r = subprocess.run(["git", "remote", "get-url", "origin"],
                   cwd="/path/to/contest", capture_output=True, text=True)
auth = re.search(r'https://([^@]+)@', r.stdout).group(1)
```

### 2. Check the issue template (mirrors accepted format)

```bash
cat .github/ISSUE_TEMPLATE/audit-report.yml
```

Common fields: `summary`, `root`, `internal-pre`, `external-pre`, `attack`, `impact`, `poc`, `mitigation`. **Mirroring accepted issues' format matters for triage speed.**

### 3. Submit via GitHub REST API (no `gh` CLI needed)

```python
import urllib.request, json

repo = "sherlock-audit/<contest-name>"
api_url = f"https://api.github.com/repos/{repo}/issues"

payload = {
    "title": "[Severity] Short title — bug class",
    "body": body_text,
    "labels": ["Medium"]  # or "High" / "Critical" / "Low/Info"
}

req = urllib.request.Request(api_url, data=json.dumps(payload).encode(),
                             method="POST", headers={
    "Authorization": f"token {auth}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "audit-submitter",
    "Content-Type": "application/json",
})
with urllib.request.urlopen(req, timeout=30) as r:
    resp = json.loads(r.read())
print(f"Issue #{resp['number']}: {resp['html_url']}")
```

### 4. Apply label + add LoC refs (PATCH issue)

The first POST may not apply the label correctly; **always PATCH after creation**:

```python
issue_n = resp['number']
api_url = f"https://api.github.com/repos/{repo}/issues/{issue_n}"
req = urllib.request.Request(api_url, data=json.dumps({
    "body": new_body_with_locs,
    "labels": ["Medium"]
}).encode(), method="PATCH", headers={...})
```

## LoC Reference Format (CRITICAL)

**Inline markdown anchor** format that resolves in GitHub blob view:

```markdown
In [`file.sol:L42-L43`](https://github.com/sherlock-audit/2026-07-xxx/blob/main/path/file.sol#L42-L43)
```

- `path/to/file.sol` — relative to repo root
- `#L42-L43` — line range anchor (use `L42` for single line, `L42-L43` for range)
- Wrap the link text in backticks

**Each finding MUST have at least one LoC ref in the body.** Reviewers use this to verify the bug is real. Missing LoC = likely rejected.

## Title Format

```
[Severity] <bug class> — <one-line description>
```

Examples (from the actual 14-issue batch):
- `[Medium] SwapMath bin balance overflow DoS — uint104 cap permanently bricks bins with high TVL`
- `[High] PeripheryPayments permissionless drain — anyone can sweep residual tokens via multicall`

The "—" (em dash) separator is conventional and makes scanning the issue list easier.

## Label Severity

| Severity | Label (case-sensitive) |
|---|---|
| Critical | `Critical` |
| High | `High` |
| Medium | `Medium` |
| Low/Info | `Low/Info` |

**Always PATCH label after creation** — first POST often doesn't propagate.

## Body Structure

1. **Summary** — 1-2 sentences: what + where + why it matters
2. **Affected Component** — file:line LoC refs (markdown anchors)
3. **Steps to Reproduce** — numbered list with code snippets
4. **Impact** — what an attacker can do, including worst-case
5. **Recommended Fix** — concrete code suggestion
6. **References** — CWE, related CVEs, prior art

Target: 3000-6000 chars total. Long enough to be thorough, short enough to be readable.

## Common Pitfalls

- **Don't submit a finding the team already accepted as a different severity** — search existing issues first via `gh issue list --repo <contest>` or the GitHub API
- **Don't use generic titles** like "Reentrancy in foo()" — be specific about WHERE
- **Don't skip LoC refs** — reviewers won't validate without them
- **Don't combine multiple bugs in one issue** — one issue per finding
- **Don't submit Low/Info unless explicitly requested** — wastes reviewer time
- **Don't fabricate line numbers** — the code is the source of truth, your numbers must match

## Worked Example: 14 Issues Filed in One Session

From the Metric OMM Pool contest (Jul 2026):

```python
# 14 issues filed via API in one session
# All with: LoC refs, severity labels, markdown body
# Pattern: write body as .md first, submit via API in a loop
for finding in findings:
    submit_via_api(finding.title, finding.body_md, finding.severity)
    time.sleep(1)  # rate limit
```

**Result**: 100% submission success rate, 0 API errors, all 14 issues accepted with labels and LoC refs in place.

## Related Skills

- `sherlock-submission` — narrower skill in the security category, more focused
- `bozagentic-bounty-hunter` — full bounty methodology
