---
name: web-exploit-test
version: 2.0.0
description: Localhost-only, stdlib evidence verifier: scan, JWT matrix, race controls.
author: IKONA; v2 hardening by Nous Research Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [authorized-security-testing, localhost, evidence, jwt, race-condition]
---
# Web Exploit Test v2

Local fixture verification only. CLI rejects non-loopback target/allow-host/state URL. TLS strict unless `--insecure`; redirects never followed; request, timeout, worker, race, response bounds enforced. Atomic redacted evidence: schema `2.0`, mode `0600`, states `tested|skipped|error|candidate|verified`. No severity before verified impact.

```bash
python3 scripts/verifier.py scan http://127.0.0.1:8080 --allow-host 127.0.0.1:8080 --modules headers,cors,methods,admin,exposed,xss,sqli,ssrf,ssti,traversal,redirect,https,info --budget 50 --test-budget 4 --output scan.json
python3 scripts/verifier.py jwt http://127.0.0.1:8080/me --allow-host 127.0.0.1 --valid-token "$TOKEN" --budget 8 --output jwt.json
python3 scripts/verifier.py race http://127.0.0.1:8080/action --allow-host 127.0.0.1:8080 --n 8 --workers 4 --serial 2 --state-url http://127.0.0.1:8080/state --state-pointer /counter --expected-delta 8 --max-delta 8 --budget 20 --output race.json
python3 -m unittest discover -s tests -v
```

Scan berjalan sekuensial dengan `ModuleBudget` atomik per modul. `exposed` memakai baseline impossible-path plus signature Git/ZIP/SQLite/env. Kontrol kelas-spesifik tetap maksimal `candidate`; hanya artifact signature kuat dapat `verified`. Methods hanya observasi. JWT `alg:none` mempertahankan payload token valid; token malformed tidak diprobe. Race menghormati `--serial`; `verified` hanya bila `--state-pointer` plus `--expected-delta`/`--max-delta` terpenuhi. Failures are atomic structured evidence without traceback-only output.

Limits: no DNS-name localhost aliases, DNS pinning, redirect following, browser XSS execution, SSRF callback, timing SQLi, destructive payloads, auth workflow, production targets. Offline `references/` remain research material only. Provenance: `PROVENANCE.md`, `NOTICE`, `MANIFEST.sha256`.
