# Combined security submission bundle

Use when the researcher explicitly wants several validated findings delivered as one confidential report plus a ZIP attachment. Default platform behavior may still prefer one ticket per root cause; combine only on explicit request or when the reporting channel accepts package-level reports.

## Bundle shape

```text
<target>_Verified_Findings_Submission/
├── README.txt
├── <target>_Verified_Findings_Report.md
├── poc/
│   ├── <finding-a>-poc.txt
│   └── <finding-b>-poc.txt
├── tests/
│   ├── <stable-regression>.patch
│   └── <develop-regression>.patch
└── evidence/
    ├── verification-output.txt
    └── SHA256SUMS.txt
```

Keep PoCs as non-executable `.txt` when policy requests it. Keep revision-specific patches separate when line context differs. Do not add Foundry boilerplate for Rust/Linux findings; state “not applicable” and include `cargo test` evidence instead.

## Combined report structure

1. Submission overview listing independent root causes.
2. Scope and exact tested revisions/assets.
3. One complete section per finding:
   - summary;
   - intended behavior vs boundary violation;
   - root cause and code path;
   - prerequisites;
   - attack sequence;
   - PoC commands and real output;
   - impact;
   - remediation.
4. Shared verification summary.
5. Attachment manifest.

If requested, omit severity, CVSS, reward, and bounty amounts everywhere: report title/body, README, evidence notes, filenames, and ZIP summary. Search the final archive contents for forbidden terms before delivery.

## Verification before ZIP

- Re-run every PoC from the copied bundle paths, not source paths.
- Re-run applicable regression tests and capture exact pass counts.
- Verify official release archive checksum and byte identity when a release binary matters.
- Run syntax checks without leaving `__pycache__` or `.pyc` files in the archive.
- Secret-scan the staged directory.
- Generate `SHA256SUMS.txt` over every payload except the manifest itself, then verify it.
- Create ZIP; test every member CRC; assert an exact member allowlist.
- Compute and report final ZIP SHA-256.
- Confirm cleanup: no leftover namespaces, routes, temporary hosts entries, or child processes.

If `zip` CLI is unavailable, use Python stdlib `zipfile` with `ZIP_DEFLATED`, `testzip()`, and an explicit expected-member list. Capture the final hash with `hashlib.sha256`.

## Delivery

Send one ZIP via `MEDIA:/absolute/path.zip`, accompanied by a terse contents/verification summary and ZIP SHA-256. Preserve the unpacked directory locally for later edits.