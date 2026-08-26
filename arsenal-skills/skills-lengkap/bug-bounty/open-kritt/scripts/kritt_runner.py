#!/usr/bin/env python3
"""
kritt_runner.py — Hermes wrapper for a LOCALLY-RUNNING open-kritt stack.

open-kritt is a self-hosted Docker stack (frontend + backend + engine),
NOT a CLI tool and NOT a public SaaS. After you run `./kritt setup && ./kritt start`
in the cloned repo, the backend REST API is available at:

    http://127.0.0.1:3002/api        (default; override with KRITT_BACKEND_URL)

This wrapper talks to that local backend to:
  1. list available workflows / post-scripts (needed to launch a scan)
  2. create a scan against a GitHub repo or a registered local repo
  3. poll the scan until it completes
  4. pull the ranked vulnerability findings

Usage:
  python3 kritt_runner.py --target <github_url_or_org/repo> [--workflow-id N]
                          [--post-script-id N] [--wait] [--format json]

  python3 kritt_runner.py --list-workflows        # discover workflow IDs first
  python3 kritt_runner.py --scan-id 42 --results  # pull findings for an existing scan

Env:
  KRITT_BACKEND_URL   default http://127.0.0.1:3002/api
"""

import argparse, json, os, sys, time, urllib.request, urllib.error

BACKEND = os.getenv("KRITT_BACKEND_URL", "http://127.0.0.1:3002/api").rstrip("/")


# ---------- low-level HTTP ----------

def _req(method: str, path: str, body: dict | None = None, timeout: int = 30) -> dict:
    url = f"{BACKEND}{path}"
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        try:
            detail = json.loads(detail)
        except json.JSONDecodeError:
            pass
        return {"_http_error": e.code, "detail": detail}
    except urllib.error.URLError as e:
        return {"_conn_error": str(e.reason),
                "hint": f"Is the open-kritt stack running? Start it with `./kritt start` in the cloned repo. Backend expected at {BACKEND}"}


# ---------- health ----------

def health() -> dict:
    return _req("GET", "/health", timeout=5)


def ensure_up() -> str | None:
    """Return None if backend is reachable, else an error dict-as-str."""
    h = health()
    if h.get("status") == "ok":
        return None
    return json.dumps(h)


# ---------- discovery ----------

def list_workflows() -> dict:
    return _req("GET", "/workflows")

def list_post_scripts() -> dict:
    return _req("GET", "/post-scripts")

def list_local_repos() -> dict:
    return _req("GET", "/local-repos")


# ---------- scan lifecycle ----------

def create_scan(target: str, workflow_id, post_script_id=None,
                model: str = "", harness: str = "codex",
                severity_ranker: str = "1",
                repo_kind: str = "remote") -> dict:
    """
    target: 'org/repo' or 'https://github.com/org/repo' for remote,
            or a registered local-repo folder name for kind=local.

    Body fields per backend/src/lib/validation.js (validateScan):
      - workflowId, postScriptId (required)
      - repo_full / repo_kind / commit_sha (top-level, NOT nested)
      - model, harness, severity_ranker (required for model selection)
      - model_provider (optional, default: codex)
    """
    body = {
        "workflowId": str(workflow_id),
        "postScriptId": str(post_script_id) if post_script_id is not None else None,
        "repo_kind": repo_kind,
        "repo_full": target,
        "commit_sha": "HEAD",
        "model": model,
        "model_provider": "codex",
        "harness": harness,
        "severity_ranker": str(severity_ranker),
        "launchPolicy": "immediate",
    }
    if post_script_id is None:
        body.pop("postScriptId")
    return _req("POST", "/scans", body)


def get_scan(scan_id) -> dict:
    return _req("GET", f"/scans/{scan_id}")


def get_findings(scan_id) -> dict:
    return _req("GET", f"/scans/{scan_id}/vulnerabilities")


def poll_until_done(scan_id, interval: int = 10, timeout: int = 1800) -> dict:
    """Poll a scan until it leaves the active states or timeout."""
    ACTIVE = {"queued", "pending", "prewarming_cache", "running",
              "rate_limited", "post_processing"}
    start = time.time()
    while time.time() - start < timeout:
        s = get_scan(scan_id)
        status = (s.get("status") or s.get("scan", {}).get("status", ""))
        sys.stderr.write(f"[kritt] scan {scan_id} status={status} "
                         f"({int(time.time()-start)}s)\n")
        if status and status not in ACTIVE:
            return s
        time.sleep(interval)
    return {"_timeout": True, "scan_id": scan_id}


# ---------- orchestration ----------

def run(target: str, workflow_id=None, post_script_id=None,
        wait: bool = True, repo_kind: str = "remote",
        model: str = "", harness: str = "codex", severity_ranker: str = "1") -> dict:
    err = ensure_up()
    if err:
        return json.loads(err)

    # auto-pick the first workflow if none supplied
    if workflow_id is None:
        wfs = list_workflows()
        items = wfs if isinstance(wfs, list) else wfs.get("workflows", wfs.get("data", []))
        if not items:
            return {"error": "no workflows found; open the UI and create/seed one first",
                    "raw": wfs}
        workflow_id = items[0].get("id")
        sys.stderr.write(f"[kritt] auto-selected workflow id={workflow_id}\n")

    # auto-pick a post-script if none supplied
    if post_script_id is None:
        ps = list_post_scripts()
        items = ps if isinstance(ps, list) else ps.get("postScripts", ps.get("data", []))
        if items:
            post_script_id = items[0].get("id")
            sys.stderr.write(f"[kritt] auto-selected post-script id={post_script_id}\n")

    created = create_scan(target, workflow_id, post_script_id, model,
                          harness, severity_ranker, repo_kind)
    if "_http_error" in created or "_conn_error" in created:
        return created
    scan_id = created.get("id") or created.get("scan", {}).get("id")
    if not scan_id:
        return {"error": "scan not created", "raw": created}

    if not wait:
        return {"scan_id": scan_id, "status": "launched",
                "view": f"http://127.0.0.1:5173/scans/{scan_id}"}

    poll_until_done(scan_id)
    findings = get_findings(scan_id)
    return {"scan_id": scan_id, "findings": findings,
            "view": f"http://127.0.0.1:5173/scans/{scan_id}"}


# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser(description="open-kritt local-stack wrapper")
    ap.add_argument("--target", help="GitHub URL / org/repo, or local repo folder name")
    ap.add_argument("--workflow-id", default=None)
    ap.add_argument("--post-script-id", default=None)
    ap.add_argument("--repo-kind", choices=["remote", "local"], default="remote")
    ap.add_argument("--no-wait", action="store_true", help="launch and return immediately")
    ap.add_argument("--list-workflows", action="store_true")
    ap.add_argument("--list-post-scripts", action="store_true")
    ap.add_argument("--list-local-repos", action="store_true")
    ap.add_argument("--scan-id", default=None, help="existing scan id")
    ap.add_argument("--results", action="store_true", help="with --scan-id: pull findings")
    ap.add_argument("--format", choices=["json"], default="json")
    args = ap.parse_args()

    # discovery shortcuts
    if args.list_workflows:
        print(json.dumps(list_workflows(), indent=2)); return
    if args.list_post_scripts:
        print(json.dumps(list_post_scripts(), indent=2)); return
    if args.list_local_repos:
        print(json.dumps(list_local_repos(), indent=2)); return

    # results for an existing scan
    if args.scan_id and args.results:
        print(json.dumps(get_findings(args.scan_id), indent=2)); return
    if args.scan_id:
        print(json.dumps(get_scan(args.scan_id), indent=2)); return

    if not args.target:
        ap.error("--target is required (unless using a --list-* or --scan-id flag)")

    out = run(args.target,
              workflow_id=args.workflow_id,
              post_script_id=args.post_script_id,
              wait=not args.no_wait,
              repo_kind=args.repo_kind)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
