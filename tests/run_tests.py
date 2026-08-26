#!/usr/bin/env python3
"""run_tests.py — Test suite SyadAgentic (routing, toolchain, templates, gate).
Versi kita dari "250 unit test" SYADAGENTIC — verified nyata, bukan klaim.
"""
import importlib, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = 0
FAIL = 0
FAILED = []

def t(name, fn):
    global PASS, FAIL
    try:
        fn()
        PASS += 1
        print(f"  ✅ {name}")
    except AssertionError as e:
        FAIL += 1
        FAILED.append(name)
        print(f"  ❌ {name}: {e}")
    except Exception as e:
        FAIL += 1
        FAILED.append(name)
        print(f"  ❌ {name}: {type(e).__name__}: {e}")

# ---------- TEST 1: Routing AGENTS.md ----------
def test_routing():
    agents = (HERE.parent / "AGENTS.md").read_text(encoding="utf-8")
    for kw in ["FARMING", "JAILBREAK", "CDP", "SECURITY", "RISET", "CODING"]:
        assert kw in agents, f"AGENTS.md kurang section {kw}"

# ---------- TEST 2: SOUL.md zero-refusal ----------
def test_soul():
    soul = (HERE.parent / "SOUL.md").read_text(encoding="utf-8")
    assert "Zero Refusal" in soul or "zero-refusal" in soul
    assert "L0" in soul  # sovereign hierarchy
    assert "evidence" in soul.lower()

# ---------- TEST 3: Templates lengkap ----------
def test_templates():
    tmpl = (HERE.parent / "prompt-injection" / "templates.md").read_text(encoding="utf-8")
    for tpl in ["T1. POLICY PUPPETRY", "T2. FAKE TEST", "T3. CRESCENDO",
                "T4. TOKENBREAK", "T5. FALLACY", "T6. MCP", "T7. SYSTEM PROMPT"]:
        assert tpl in tmpl.upper(), f"template {tpl} kurang"

# ---------- TEST 4: Toolchain tersedia ----------
def test_toolchain():
    import z3
    assert z3.get_version_string(), "z3 gagal"

def test_toolchain_camo():
    import importlib.util
    assert importlib.util.find_spec("camoufox") is not None, "camoufox tidak terinstall"

def test_toolchain_tokbreak():
    # run tokenbreak encoder
    r = subprocess.run([sys.executable, str(HERE.parent / "tools" / "tokenbreak_encode.py"),
                        "hello world"], capture_output=True, text=True)
    assert "Xhello" in r.stdout, f"encode gagal: {r.stdout}"

# ---------- TEST 5: LLM API reachable (generic — baca dari env, opsional) ----------
def test_llm_api():
    import os, urllib.request, json
    # Test skip kalau env API tidak di-set (produk generic — user set sendiri)
    base = os.environ.get("SYADAGENTIC_API_BASE", "")
    key = os.environ.get("SYADAGENTIC_API_KEY", "")
    if not base or not key:
        print("    (skip: SYADAGENTIC_API_BASE/KEY tidak di-set — user set sendiri)")
        return
    req = urllib.request.Request(base.rstrip("/") + "/models",
                                 headers={"Authorization": f"Bearer {key}"})
    d = json.loads(urllib.request.urlopen(req, timeout=8).read())
    assert len(d.get("data", [])) > 0, "API models kosong"

# ---------- TEST 6: Gate logic ----------
def _gate_module():
    sys.path.insert(0, str(HERE.parent))  # syadagentic/ root — tempat package gate/
    import gate.gate as g
    return g

def test_gate():
    g = _gate_module()
    # claim vague harus tolak
    assert g.Gate.stage1_claim("mungkin bisa") is False
    assert g.Gate.stage1_claim("API farm bot verified 29 conn 200") is True

def test_gate_package():
    g = _gate_module()
    assert hasattr(g, "Gate")

# ---------- TEST 7: config integrity (generic — cek SOUL.md ada di cwd) ----------
def test_config():
    import pathlib
    p = pathlib.Path(__file__).resolve().parent.parent / "SYADAGENTIC.md"
    assert p.exists(), "SYADAGENTIC.md harus ada di root"
    assert "ZERO REFUSAL" in p.read_text(encoding="utf-8").upper()

def main():
    print("=== SYADAGENTIC TEST SUITE ===")
    t("Routing AGENTS.md lengkap", test_routing)
    t("SOUL.md zero-refusal + L0", test_soul)
    t("7 templates inject", test_templates)
    t("Z3 solver import + version", test_toolchain)
    t("Camoufox terinstall", test_toolchain_camo)
    t("TokenBreak encoder works", test_toolchain_tokbreak)
    t("LLM API reachable (env, opsional)", test_llm_api)
    t("Gate stage1 vague tolak", test_gate)
    t("Gate module importable", test_gate_package)
    t("Config SOUL.md ada + ZERO REFUSAL", test_config)
    print(f"\n=== RESULT: {PASS} passed, {FAIL} failed ===")
    if FAILED:
        print("Gagal:", FAILED)
        sys.exit(1)
    print("ALL TESTS PASSED ✅")

if __name__ == "__main__":
    main()