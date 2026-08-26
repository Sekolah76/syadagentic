#!/usr/bin/env python3
"""
farm_pipeline.py — Phase-Engine Farming Pipeline (preset farm) — SYADAGENTIC v6.7
Menggunakan phase_engine (state JSON + checkpoint + budget + learn) utk pipeline
farming end-to-end: recon-provider → probe-endpoint → verify-email → register →
harvest-key → validate-key.

Contoh nyata: mail.tm temp-email → register di provider target (template) →
harvest key → validate via 9router. Terstruktur, resume-able, token-efficient.
"""
import sys, os, json, time, urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase-engine"))
from phase_engine import PhaseEngine

# --- MAIL.TM helper (temp email real) ---
def mailtm_get_domain():
    req = urllib.request.Request("https://api.mail.tm/domains")
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode())
    for d in data.get("hydra:member", []):
        if d.get("isActive"):
            return d["domain"]
    return None

def mailtm_create_account(domain):
    import random, string, hashlib
    user = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    pw = "".join(random.choices(string.ascii_letters + string.digits, k=12))
    addr = f"{user}@{domain}"
    body = json.dumps({"address": addr, "password": pw}).encode()
    req = urllib.request.Request("https://api.mail.tm/accounts", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    return {"address": addr, "password": pw, "status": code}

# --- PHASES (callable utk phase_engine) ---
def p_recon(eng, ctx):
    """Cari domain mail.tm aktif."""
    dom = mailtm_get_domain()
    return {"domain": dom, "provider": ctx.get("provider", "generic")}

def p_probe(eng, ctx):
    """Probe endpoint provider target (URL dari ctx)."""
    url = ctx.get("signup_url")
    if not url:
        return {"status": "skipped", "reason": "no signup_url"}
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as r:
            return {"status": r.status, "reachable": r.status < 500}
    except Exception as e:
        return {"status": "err", "error": str(e)[:100]}

def p_verify_email(eng, ctx):
    """Buat akun mail.tm (verifikasi email dulu)."""
    domain = eng.state["data"].get("recon-provider", {}).get("domain")
    if not domain:
        return {"status": "err", "error": "no domain"}
    acc = mailtm_create_account(domain)
    return {"account": acc["address"], "password": acc["password"], "status": acc["status"]}

def p_register(eng, ctx):
    """Register di provider (stub — ganti dgn endpoint target nyata)."""
    acc = eng.state["data"].get("verify-email", {})
    # TEMPLATE: ganti dgn request register provider target
    payload = {
        "email": acc.get("account"),
        "password": acc.get("password"),
        "plan": "free",
    }
    # contoh: simpan sbg artefak (tanpa request nyata = dry-run aman)
    artifact = {"registered": payload, "note": "template — ganti endpoint provider"}
    return artifact

def p_harvest(eng, ctx):
    """Harvest key dari response register (template)."""
    reg = eng.state["data"].get("register-account", {})
    # contoh key dummy utk struktur; ganti dgn parse key nyata
    key = "sk-" + "x" * 32 if reg.get("registered") else None
    return {"api_key": key, "format": "sk-*"}

def p_validate(eng, ctx):
    """Validasi key (stub — test ke 9router/provider)."""
    key = eng.state["data"].get("harvest-key", {}).get("api_key")
    return {"key_valid": bool(key), "key": key, "note": "stub validate — ganti dgn test nyata"}

PHASES = {
    "recon-provider": p_recon,
    "probe-endpoint": p_probe,
    "verify-email": p_verify_email,
    "register-account": p_register,
    "harvest-key": p_harvest,
    "validate-key": p_validate,
}

def main():
    eng = PhaseEngine("farm-run-1", preset="farm",
                      state_dir=os.path.join(os.path.dirname(__file__), ".farm-state"))
    eng.start()
    ctx = {"provider": "mail.tm-demo", "signup_url": None}
    for phase in eng.state["phases"]:
        fn = PHASES.get(phase)
        if not fn:
            eng.log(f"⚠ fase {phase} tidak ada handler")
            continue
        try:
            eng.run_phase(fn, ctx)
        except Exception as e:
            eng.log(f"✗ fase {phase} gagal: {e}")
            break
    print("\n" + eng.report())
    lesson = eng.learn(lesson_dir=os.path.join(os.path.dirname(__file__), ".farm-grain"))
    print(f"\n🧠 Pelajaran: {lesson}")

if __name__ == "__main__":
    main()