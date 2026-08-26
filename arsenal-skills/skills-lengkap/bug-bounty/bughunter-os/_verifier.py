"""
Verifier Subagent — External Model Verification Layer

Calls an external LLM (OpenAI-compatible API) to verify findings before submission.

Usage:
    verify_finding(
        finding_summary="...",
        code_reference="...",
        claimed_severity="High",
        target_context="Obol Charon"
    )
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path

# Config loaded from file (no API key here for security)
CONFIG_PATH = os.path.expanduser("~/.hermes/skills/bughunter-os/_verifier_config.json")

# In-memory API key (provided at runtime, NOT persisted)
_API_KEY = None


def set_api_key(key: str):
    """Set the API key in memory. Not persisted to disk."""
    global _API_KEY
    _API_KEY = key


def _load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)["verifier"]


def _build_prompt(finding_summary: str, code_reference: str = "",
                  claimed_severity: str = "", target_context: str = "",
                  code_excerpt: str = "") -> str:
    """Build the verifier prompt."""
    parts = [
        "You are an expert security bug bounty verifier.",
        "",
        "Your task: review a vulnerability claim and provide an independent verdict.",
        "",
        "STRICT RULES:",
        "1. Do NOT search for new bugs. Only verify the claim.",
        "2. Do NOT propose alternative attack vectors. Only assess feasibility.",
        "3. You MAY suggest PoC improvements (cleaner test, better repro).",
        "4. You MAY suggest severity adjustments WITH strong reasoning.",
        "5. Be rigorous. If the claim is wrong, REJECT it.",
        "",
    ]

    if target_context:
        parts.append(f"=== CONTEXT ===\n{target_context}\n")
    if finding_summary:
        parts.append(f"=== FINDING CLAIM ===\n{finding_summary}\n")
    if code_reference:
        parts.append(f"=== CODE REFERENCE ===\n{code_reference}\n")
    if code_excerpt:
        parts.append(f"=== CODE EXCERPT ===\n```\n{code_excerpt}\n```\n")
    if claimed_severity:
        parts.append(f"=== CLAIMED SEVERITY ===\n{claimed_severity}\n")

    parts.append("""=== REQUIRED OUTPUT FORMAT ===
VERDICT: [CONFIRMED | NEEDS_MORE_EVIDENCE | REJECTED]
SEVERITY_ASSESSMENT: [OK | SUGGEST: <new severity> because <reasoning>]
POC_ASSESSMENT: [OK | IMPROVEMENTS: <list>]
ISSUES: [any issues found, or "none"]
REASONING: [brief explanation of your verdict]
CONFIDENCE: [0-100%]
""")
    return "\n".join(parts)


def verify_finding(finding_summary: str, code_reference: str = "",
                   claimed_severity: str = "", target_context: str = "",
                   code_excerpt: str = "") -> dict:
    """Call external LLM to verify a finding. Returns parsed verdict dict."""
    if not _API_KEY:
        return {
            "success": False,
            "error": "API key not set. Call set_api_key() first."
        }

    try:
        config = _load_config()
    except Exception as e:
        return {"success": False, "error": f"Config load failed: {e}"}

    prompt = _build_prompt(
        finding_summary=finding_summary,
        code_reference=code_reference,
        claimed_severity=claimed_severity,
        target_context=target_context,
        code_excerpt=code_excerpt
    )

    models = [config["model"]]
    fb = config.get("fallback_model") or config.get("fallback_models")
    if isinstance(fb, str) and fb and fb not in models:
        models.append(fb)
    elif isinstance(fb, list):
        for m in fb:
            if m and m not in models:
                models.append(m)

    last_err = None
    for model_name in models:
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get("max_tokens", 500),
            "temperature": config.get("temperature", 0.1)
        }
        try:
            req = urllib.request.Request(
                f"{config['baseurl']}/chat/completions",
                data=json.dumps(payload).encode(),
                headers={
                    "Authorization": f"Bearer {_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                resp = json.loads(r.read())

            content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Parse verdict
            verdict = {
                "success": True,
                "raw_response": content,
                "model": model_name,
                "tokens": resp.get("usage", {})
            }

            # Extract structured fields
            for line in content.split("\n"):
                line = line.strip()
                for field in ("VERDICT", "SEVERITY_ASSESSMENT", "POC_ASSESSMENT",
                              "ISSUES", "REASONING", "CONFIDENCE"):
                    if line.startswith(field + ":"):
                        verdict[field.lower()] = line[len(field) + 1:].strip()

            return verdict
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:500]
            last_err = f"HTTP {e.code} model={model_name}: {body}"
            # try next model on permission/rate/unavailable
            if e.code in (403, 404, 429, 500, 502, 503):
                continue
            return {"success": False, "error": last_err}
        except Exception as e:
            last_err = f"Error model={model_name}: {e}"
            continue

    return {"success": False, "error": last_err or "All verifier models failed"}


def should_verify(severity: str) -> bool:
    """Decide whether to invoke external verifier based on severity."""
    return severity.lower() in ("critical", "high")


# CLI for testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 _verifier.py <api_key>")
        sys.exit(0)
    set_api_key(sys.argv[1])

    # Test
    result = verify_finding(
        finding_summary="Bug in Obol Charon: validateKeymanagerFlags only logs warning for http:// URLs, allowing BLS key exfil.",
        code_reference="dkg/dkg.go:1201-1225",
        claimed_severity="High",
        target_context="Obol Bug Bounty Program"
    )
    print(json.dumps(result, indent=2))
