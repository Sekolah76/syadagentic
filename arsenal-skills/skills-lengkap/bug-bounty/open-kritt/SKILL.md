---
name: open-kritt
category: security
description: >
  Drive a **locally-running open-kritt stack** (github.com/Kritt-ai/open-kritt) from Hermes for bug-bounty code audits. open-kritt is a self-hosted Docker platform that orchestrates AI agents (Codex / Claude Code) to find real vulnerabilities in a target repo, de-duplicates, and severity-ranks the findings.

  Use this skill when the user asks to scan/audit a GitHub repo or a local
  codebase with kritt, wants AI-driven vulnerability discovery on a Solidity/
  Rust/JS/Go project, or references "open-kritt" / "kritt scan". The skill
  talks to the kritt backend REST API at http://127.0.0.1:3002/api (override
  with KRITT_BACKEND_URL), so the Docker stack must be running first
  (`./kritt start` in the cloned repo).

  Capabilities: list workflows / post-scripts / local repos, launch a scan
  against a remote GitHub repo or a registered local folder, poll until
  complete, and pull ranked findings. Findings feed naturally into the
  bug-bounty / web3-audit workflows for PoC + reporting.

integration:
  type: local-http-api
  backend_url: http://127.0.0.1:3002/api
  frontend_ui: http://127.0.0.1:5173
  github_url: https://github.com/Kritt-ai/open-kritt
tags:
  - bug-bounty
  - defi
  - web3
  - code-audit
  - ai-security
  - self-hosted
---

# open-kritt — Local AI Vulnerability Scanner (Hermes integration)

> **What it is:** open-kritt is a *self-hosted Docker stack* (frontend + backend + engine + Postgres), **not** a CLI binary and **not** a public SaaS. There is no API key and no npm/pip package — you run it yourself. This skill drives its local backend REST API so Hermes can launch scans and pull findings the same way it uses `pentest-ai`, but over HTTP to `localhost` instead of MCP.

> **Do NOT waste turns trying to install it as a package.** Confirmed dead ends
> (Aug 2026): no `kritt`/`open-kritt`/`open-kritt-ai` on PyPI, nothing on the
> npm registry, no GitHub release binary (`releases/latest/download/...` → 404),
> and `npx github:Kritt-ai/open-kritt` fails with `ENOENT ... package.json`
> because the repo ROOT has no `package.json` (the JS lives under `backend/`,
> `frontend/`, `engine/`). `pip install git+https://...` also fails — no
> `setup.py`/`pyproject.toml` at root. The ONLY supported install is the Docker
> stack (`git clone` → `./kritt setup` → `./kritt start`). This is the general
> rule for **any tool whose README quick-start is `git clone && ./<tool>
> start`** rather than `pip/npm/brew install`: treat it as a self-hosted
> service, point the skill at its local API, and don't go package-hunting.

> **`pentest-ai` = MCP server, `open-kritt` = local HTTP API.** `pentest-ai`
> (`ptai`) is wired in via `hermes mcp add` (config `mcp_servers.pentest-ai:
> {command: ptai, args: [mcp]}`), which is why Hermes can call its tools every
> turn as first-class tools. open-kritt has **no `mcp` subcommand** — it's a web
> stack — so it can't be an MCP server. The equivalent "callable during bug
> hunting" integration is: a skill whose description triggers on scan/audit
> requests + a `scripts/` REST client that hits the local backend. Don't try to
> `hermes mcp add` a tool that doesn't speak MCP.

---

## 1. One-time install (you do this once, outside Hermes)

Needs Git, Docker + Docker Compose, and Node.js 20+.

```bash
git clone https://github.com/Kritt-ai/open-kritt
cd open-kritt
./kritt setup      # guided: pick model access (Codex login / OpenAI / Anthropic / OpenRouter)
./kritt start      # brings up the Docker stack
```

When it's up:
- **Backend API:** `http://127.0.0.1:3002/api`
- **Web UI:** `http://127.0.0.1:5173`

> ⚠️ The backend has **no application auth** and binds to `127.0.0.1`. Keep it
> private. If you need it on your phone, front it with the existing Tailscale
> Serve setup — don't expose 3002/5173 to the public internet.

---

## 2. How Hermes calls it

All calls go through `scripts/kritt_runner.py`, which hits the local backend.
Override the base URL with `KRITT_BACKEND_URL` if you changed the port.

### Discover what's available first (workflow IDs are required to scan)

```bash
python3 ~/.hermes/skills/open-kritt/scripts/kritt_runner.py --list-workflows
python3 ~/.hermes/skills/open-kritt/scripts/kritt_runner.py --list-post-scripts
python3 ~/.hermes/skills/open-kritt/scripts/kritt_runner.py --list-local-repos
```

### Scan a remote GitHub repo (auto-picks first workflow, waits, returns findings)

```bash
python3 ~/.hermes/skills/open-kritt/scripts/kritt_runner.py \
  --target https://github.com/org/target-contracts
```

### Scan with an explicit workflow + post-script (validate/PoC step)

```bash
python3 ~/.hermes/skills/open-kritt/scripts/kritt_runner.py \
  --target org/target-contracts \
  --workflow-id 1 \
  --post-script-id 2
```

### Launch without blocking (return a scan id + UI link immediately)

```bash
python3 ~/.hermes/skills/open-kritt/scripts/kritt_runner.py \
  --target org/repo --no-wait
```

### Pull findings for a scan that's already finished

```bash
python3 ~/.hermes/skills/open-kritt/scripts/kritt_runner.py --scan-id 42 --results
```

### Scan a local folder (register it in the UI first, then reference by name)

```bash
python3 ~/.hermes/skills/open-kritt/scripts/kritt_runner.py \
  --target my-local-repo-folder --repo-kind local
```

---

## 3. Backend REST API (reference)

Base: `http://127.0.0.1:3002/api`

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | `{status:"ok"}` liveness |
| GET | `/workflows` | list workflows (need an `id` to scan) |
| GET | `/post-scripts` | list post-scripts (validate / PoC / report steps) |
| GET | `/local-repos` | list registered local repos |
| POST | `/scans` | create a scan (body below) |
| GET | `/scans/:id` | scan status |
| GET | `/scans/:id/vulnerabilities` | ranked findings |
| PATCH | `/scans/:id` | pause / stop / resume |
| DELETE | `/scans/:id` | delete a finished scan |

**POST /scans body:**
```json
{
  "workflowId": 1,
  "repo": { "kind": "remote", "repo_full": "org/repo", "commit_sha": "HEAD" },
  "postScriptId": 2,
  "launchPolicy": "immediate"
}
```
`kind` is `remote` (GitHub) or `local` (a folder registered via the UI).
`launchPolicy` `immediate` starts now; `queue` waits behind a running scan
(the API returns 409 `scan_launch_policy_required` if one is active and you
didn't choose).

---

## 4. Bug-hunting workflow

```
1. ./kritt start                      # (once) bring the stack up
2. --list-workflows                   # find the workflow id you want
3. --target <repo>                    # launch + wait + pull findings
4. Feed findings → web3-audit / bug-bounty skill
5. Validate exploitability with Foundry/Echidna PoC
6. Write report → report-writing skill → submit
```

Pair with: `web3-audit`, `smart-contract-audit-toolkit`, `surgical-drain-pattern`,
`report-writing`.

---

## 5. Files in this skill

| File | Purpose |
|---|---|
| `scripts/kritt_runner.py` | Local-backend REST client (list / scan / poll / findings) |
| `references/kritt-bug-class-cheatsheet.md` | Bug-class → severity / bounty map |
| `references/default-workflows.md` | Seeded workflow + post-script ID map (wf 1 = generic external-flow, wf 2 = Cosmos ABCI) |
| `templates/scan-request.json` | POST /scans body schema |

---

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| `_conn_error: Connection refused` | Stack not running → `./kritt start` in the repo |
| `no workflows found` | Open the UI (`:5173`), seed/create a workflow, or check `--list-workflows` |
| 409 `scan_launch_policy_required` | Another scan is active; pass a different launch policy or wait |
| Want phone access | Front `:5173` with Tailscale Serve — don't public-expose |
| Different port | `export KRITT_BACKEND_URL=http://127.0.0.1:<port>/api` |
