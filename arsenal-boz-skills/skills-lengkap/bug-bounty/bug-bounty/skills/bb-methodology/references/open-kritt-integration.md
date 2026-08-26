# open-kritt Integration (AI-Powered Source Scanner)

> **open-kritt**: AI agents that find real vulns via path-sensitive symbolic execution + AST + LLM taint.  
> GitHub: `Kritt-ai/open-kritt` (JavaScript / Node.js). Not always installable in restricted sandboxes.

This reference is the **session-specific integration recipe** — how to wire open-kritt into the Phase 3 DISCOVERY toolchain of this methodology.

---

## Quick Start (3 install paths)

### Path A — Local CLI binary (full offline, recommended)

```bash
# 1. Node.js 22+
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs

# 2. Clone + install
git clone https://github.com/Kritt-ai/open-kritt.git /opt/kritt
cd /opt/kritt && npm ci
npm link   # installs `kritt` to PATH

# 3. Verify
kritt scan --repo https://github.com/org/contract --bug-class oracle --json
```

If npm GitHub fetch is blocked (sandboxed envs):
```bash
# Manual: from a machine *with* GitHub access
npm pack github:Kritt-ai/open-kritt  # produces open-kritt-x.y.z.tgz
# upload .tgz to target, then:
npm install -g open-kritt-x.y.z.tgz
```

### Path B — SaaS API (set env & go)

```bash
export KRITT_API_KEY=<your-key-from-kritt-ai/settings>
export KRITT_ENDPOINT=https://api.kritt.ai/v1
# kritt_runner.py detects this and calls API
```

### Path C — Browser automation fallback

If **no binary, no API key, no network** — kritt playground can be driven via headless Chrome:
```bash
python3 ~/.hermes/skills/open-kritt/scripts/kritt_browser_driver.py --target <repo_url>
```
Needs browser automation tool (e.g. Camofox on `localhost:9377`, or Playwright).

---

## CLI Flags & Output Formats

| Flag | Description |
|---|---|
| `--repo <url>` | GitHub repo to scan |
| `--path <dir>` | Local directory to scan |
| `--bug-class <type>` | Filter: `reentrancy`, `access-control`, `oracle`, `proxy`, `gas`, `garbage-collection`, `bridge-message`, `all` |
| `--format json/sarif/raw` | Output format |
| `--depth quick/full` | Scan depth |
| `--sarif > findings.sarif` | Direct SARIF output → GitHub Code Scanning / VS Code |

---

## Bug-Class → Severity Mapping (for bounty prioritization)

| Bug Class | Solidity Pattern | Severity | Typical Bounty |
|---|---|---|---|
| `reentrancy` | no nonReentrant + external call | Critical/High | $5k–$50k |
| `access-control` | tx.origin / missing onlyOwner | Critical/High | $1k–$25k |
| `oracle` | spot price + no TWAP / stale check | Critical/High | $5k–$30k |
| `proxy` | storage collision / upgradeTo | High/Medium | $1k–$15k |
| `gas` | unbounded loops in hot path | Medium/Low | $100–$5k |
| `garbage-collection` | selfdestruct breaks state | Medium | $500–$2k |
| `bridge-message` | no replay protection | High/Critical | $10k–$100k |

---

## Known Installation Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `npm install github:Kritt-ai/open-kritt` hangs / 254 | GitHub API blocked in sandbox | Use `npm pack` on a machine with access, upload .tgz |
| `kritt: command not found` after install | `npm link` failed silently | Manually symlink: `ln -s $(npm bin -g)/kritt /usr/local/bin/kritt` |
| API mode: 401 Unauthorized | No `KRITT_API_KEY` or wrong endpoint | Set `KRITT_API_KEY` + `KRITT_ENDPOINT=https://api.kritt.ai/v1` |
| Browser driver: blank page / JS error | Camofox headless context needs CSP disabled | Ensure `--disable-web-security --disable-gpu` flags set |
| kritt flags Solidity as JS | Wrong repo language detected | Explicitly pass `--path <contracts_dir>/contracts` not repo root |

---

## Workflow Integration

1. **Phase 1 RECON**: Run `nuclei -tags cve` + `subfinder` first.
2. **Phase 1 RECON**: If GitHub repo found → fire `kritt scan --bug-class all --format sarif &` in **background** (scans take 5–90 min).
3. **Phase 2 TRIAGE**: While kritt runs, do manual review on highest-signal contracts.
4. **Phase 3 DISCOVERY**: Cross-validate: if `kritt` flags `reentrancy` on Line X, run `slither --detect reentrancy --filter-paths` to confirm/deny.
5. **Phase 4 PROVE**: Pipe SARIF into `reports/` — kritt output maps to findings DB.

---

## Example: Concurrent Validation with slither

```bash
REPO="https://github.com/owner/project"
kritt scan --repo $REPO --bug-class all --format sarif > kritt.sarif &
SLITHER_PID=$!
slither $REPO --filter-paths --triage-mode 2>&1 | tee slither.log &
SLITHER_PID2=$!
wait $SLITHER_PID $SLITHER_PID2
```

Compare `kritt.sarif` (AST + symbolic) against `slither.log` (static taint) — **cross-validated findings get +1 severity confidence**.
