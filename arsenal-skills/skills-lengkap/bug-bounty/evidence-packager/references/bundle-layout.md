# Suggested bundle layout

```text
evidence-bundle/
├── manifest.yaml
├── README.md
├── claims/
│   └── claim-evidence-matrix.yaml
├── environment/
│   ├── revision.txt
│   ├── build-config.txt
│   └── deployment-profile.md
├── source-references/
├── reproduction/
│   ├── steps.md
│   ├── inputs/
│   ├── outputs/
│   └── controls/
├── traces/
├── state/
│   ├── before/
│   └── after/
├── poc/
├── screenshots/
└── raw-private-do-not-submit/
```

Keep raw sensitive material outside the submission bundle. The manifest should point to sanitized artifacts only.
