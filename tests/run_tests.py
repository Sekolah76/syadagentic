#!/usr/bin/env python3
"""run_tests.py — Test suite SyadAgentic (routing, toolchain, templates, gate, core).

Prinsip: tidak ada test yang bikin CI merah gara-gara dependency opsional.
Dependency opsional (z3, camoufox) -> SKIP, bukan FAIL. Pakai --strict kalau
kamu memang mau SKIP dihitung gagal (misal di mesin lokal yang sudah lengkap).

Exit code 0 = semua test lulus (skip tidak dihitung gagal, kecuali --strict).
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STRICT = "--strict" in sys.argv[1:]

PASS = 0
FAIL = 0
SKIP = 0
FAILED: list[str] = []
SKIPPED: list[str] = []


class Skip(Exception):
    """Dependency opsional tidak ada — bukan kegagalan."""


def _skip(why: str) -> None:
    raise Skip(why)


def t(name: str, fn) -> None:
    global PASS, FAIL
    try:
        fn()
        PASS += 1
        print(f"  ✅ {name}")
    except KeyboardInterrupt:
        raise
    except Skip as e:
        global SKIP
        SKIP += 1
        SKIPPED.append(name)
        print(f"  ⏭️  {name} (skip: {e})")
    except AssertionError as e:
        FAIL += 1
        FAILED.append(name)
        print(f"  ❌ {name}: {e}")
    except Exception as e:  # noqa: BLE001 — test runner must not crash
        FAIL += 1
        FAILED.append(name)
        print(f"  ❌ {name}: {type(e).__name__}: {e}")


def _have(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def _version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


# ---------- TEST: routing ----------
def test_routing():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for kw in ["FARMING", "JAILBREAK", "CDP", "SECURITY", "RISET", "CODING"]:
        assert kw in agents, f"AGENTS.md kurang section {kw}"


# ---------- TEST: soul ----------
def test_soul():
    soul = (ROOT / "SOUL.md").read_text(encoding="utf-8")
    assert "Zero Refusal" in soul or "zero-refusal" in soul, "SOUL.md tanpa zero-refusal"
    assert "L0" in soul, "SOUL.md tanpa hierarki L0"
    assert "evidence" in soul.lower(), "SOUL.md tanpa evidence gate"


# ---------- TEST: templates ----------
def test_templates():
    tmpl = (ROOT / "prompt-injection" / "templates.md").read_text(encoding="utf-8")
    for tpl in ["T1. POLICY PUPPETRY", "T2. FAKE TEST", "T3. CRESCENDO",
                "T4. TOKENBREAK", "T5. FALLACY", "T6. MCP", "T7. SYSTEM PROMPT"]:
        assert tpl in tmpl.upper(), f"template {tpl} kurang"
    n = len(re.findall(r"^#+\s*T\d+", tmpl, re.MULTILINE))
    assert n >= 40, f"template cuma {n}, README klaim 40+"


# ---------- TEST: toolchain (opsional) ----------
def test_toolchain_z3():
    if not _have("z3"):
        _skip("z3-solver tidak terinstall")
    import z3
    assert z3.get_version_string(), "z3 gagal load"


def test_toolchain_camo():
    if not _have("camoufox"):
        _skip("camoufox tidak terinstall (browser opsional)")
    import camoufox  # noqa: F401


def test_toolchain_tokbreak():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "tokenbreak_encode.py"),
                        "hello world"], capture_output=True, text=True)
    assert r.returncode == 0, f"encoder exit {r.returncode}: {r.stderr[:200]}"
    assert "Xhello" in r.stdout, f"encode gagal: {r.stdout[:200]}"


def test_toolchain_caesar():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "caesar_encode.py"), "test"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.strip(), "caesar encoder kosong"


# ---------- TEST: LLM API opsional ----------
def test_llm_api():
    base = os.environ.get("SYADAGENTIC_API_BASE", "")
    key = os.environ.get("SYADAGENTIC_API_KEY", "")
    if not base or not key:
        _skip("SYADAGENTIC_API_BASE/KEY tidak di-set")
    import urllib.request
    req = urllib.request.Request(base.rstrip("/") + "/models",
                                headers={"Authorization": f"Bearer {key}"})
    d = json.loads(urllib.request.urlopen(req, timeout=8).read())
    assert len(d.get("data", [])) > 0, "API models kosong"


# ---------- TEST: gate ----------
def _gate_module():
    sys.path.insert(0, str(ROOT))
    import gate.gate as g
    return g


def test_gate():
    g = _gate_module()
    assert g.Gate.stage1_claim("mungkin bisa") is False, "claim vague harus ditolak"
    assert g.Gate.stage1_claim("API farm bot verified 29 conn 200") is True


def test_gate_package():
    g = _gate_module()
    assert hasattr(g, "Gate"), "gate.Gate hilang"


def test_gate_cli():
    r = subprocess.run([sys.executable, str(ROOT / "gate" / "gate.py"),
                        "claim terverifikasi 200", "--cmd", "echo pass 200",
                        "--expect", "200", "--sev", "P3"],
                       capture_output=True, text=True, timeout=60)
    assert "200" in (r.stdout + r.stderr), f"gate CLI tidak jalan: {r.stdout[-200:]}"


# ---------- TEST: config ----------
def test_config():
    p = ROOT / "SYADAGENTIC.md"
    assert p.exists(), "SYADAGENTIC.md harus ada di root"
    assert "ZERO REFUSAL" in p.read_text(encoding="utf-8").upper()


# ---------- TEST: framework-core modules ----------
def test_framework_core():
    for rel in ["arsenal-framework/governor/governor.py",
                "arsenal-framework/chain-map/chain_map.py",
                "arsenal-framework/drills/drills.py",
                "arsenal-framework/phase-engine/phase_engine.py",
                "arsenal-framework/captcha-harvester/route_intercept_captcha.py"]:
        assert (ROOT / rel).exists(), f"modul core hilang: {rel}"
    for rel in ["arsenal-framework/governor/governor.py",
                "arsenal-framework/chain-map/chain_map.py",
                "arsenal-framework/drills/drills.py"]:
        try:
            compile((ROOT / rel).read_text(encoding="utf-8"), rel, "exec")
        except SyntaxError as e:
            raise AssertionError(f"{rel} gagal compile: {e}") from None


# ---------- TEST: semua python di repo compile ----------
def test_all_python_compiles():
    bad = []
    for p in ROOT.rglob("*.py"):
        if ".git" in p.parts or "__pycache__" in p.parts:
            continue
        try:
            compile(p.read_text(encoding="utf-8", errors="ignore"), str(p), "exec")
        except SyntaxError as e:
            bad.append(f"{p.relative_to(ROOT)}: {e.msg} (line {e.lineno})")
    assert not bad, f"{len(bad)} file .py gagal compile, contoh: {bad[:3]}"


# ---------- TEST: shell scripts sintaks ----------
def test_shell_syntax():
    if subprocess.run(["bash", "-c", "command -v bash"], capture_output=True).returncode != 0:
        _skip("bash tidak ada")
    bad = []
    for p in ROOT.rglob("*.sh"):
        if ".git" in p.parts:
            continue
        r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append(f"{p.relative_to(ROOT)}: {r.stderr.strip()[:80]}")
    assert not bad, f"{len(bad)} script gagal bash -n, contoh: {bad[:3]}"


# ---------- TEST: data files valid ----------
def test_data_files_valid():
    for p in ROOT.rglob("*.json"):
        if ".git" in p.parts:
            continue
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            raise AssertionError(f"{p.relative_to(ROOT)} JSON invalid: {e}") from None
    if not _have("yaml"):
        _skip("pyyaml tidak terinstall")
    import yaml
    for p in ROOT.rglob("*.yaml"):
        if ".git" in p.parts:
            continue
        try:
            list(yaml.safe_load_all(p.read_text(encoding="utf-8")))
        except Exception as e:  # noqa: BLE001
            raise AssertionError(f"{p.relative_to(ROOT)} YAML invalid: {e}") from None


# ---------- TEST: VERSION konsisten ----------
def test_version_consistency():
    v = _version()
    assert re.fullmatch(r"\d+\.\d+\.\d+", v), f"VERSION tidak semver: {v}"
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"version-{v}-" in readme, f"badge README tidak sinkron dengan VERSION {v}"
    inst = (ROOT / "install.sh").read_text(encoding="utf-8")
    assert "VERSION" in inst, "install.sh harus baca VERSION, bukan hardcode"


# ---------- TEST: tidak ada placeholder/secret di core repo ----------
CORE_GLOBS = ["*.md", "*.sh", "*.py", "*.json", "*.yml"]
CORE_DIRS = [".github", "docs", "tests", "tools", "gate", "arsenal-framework"]


def _core_files():
    seen = []
    for pat in CORE_GLOBS:
        seen.extend(ROOT.glob(pat))
    for d in CORE_DIRS:
        seen.extend((ROOT / d).rglob("*"))
    return [p for p in seen if p.is_file() and p.suffix in {".md", ".sh", ".py", ".json", ".yml", ".html", ".txt"}]


def test_no_placeholder():
    hits = []
    pat = re.compile(r"github\.com/USER/|github\.com/USERNAME/|t\.me/\.\.\.")
    for p in _core_files():
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            continue
        if pat.search(txt):
            hits.append(str(p.relative_to(ROOT)))
    assert not hits, f"placeholder belum diganti: {hits[:5]}"


def test_no_secret():
    pat = re.compile(r"ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}"
                     r"|sk-[A-Za-z0-9]{32,}|AKIA[0-9A-Z]{16}"
                     r"|-----BEGIN [A-Z ]*PRIVATE KEY-----")
    hits = []
    for p in _core_files():
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            continue
        for m in pat.finditer(txt):
            if "EXAMPLE" in m.group(0):
                continue
            hits.append(f"{p.relative_to(ROOT)}: {m.group(0)[:12]}…")
    assert not hits, f"secret terdeteksi: {hits[:5]}"


# ---------- TEST: link relatif dokumen top-level ----------
def test_top_level_links():
    bad = []
    files = list(ROOT.glob("*.md")) + list((ROOT / "docs").rglob("*.md"))
    for p in files:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\]\(([^)#\s]+?)(?:#[^)]*)?\)", txt):
            link = m.group(1).strip()
            if link.startswith(("http", "mailto:", "#", "//")) or not link:
                continue
            if not (p.parent / link).exists():
                bad.append(f"{p.relative_to(ROOT)} -> {link}")
    assert not bad, f"link relatif rusak: {bad[:5]}"


# ---------- TEST: manifest integritas skill (kalau ada) ----------
def test_manifest():
    man = ROOT / "arsenal-skills" / "MANIFEST.sha256"
    if not man.exists():
        _skip("MANIFEST.sha256 belum dibuat")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "build_manifest.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"manifest tidak cocok: {(r.stdout + r.stderr)[-200:]}"


def main() -> int:
    print(f"=== SYADAGENTIC TEST SUITE v{_version()} ===")
    t("Routing AGENTS.md lengkap", test_routing)
    t("SOUL.md zero-refusal + L0", test_soul)
    t("Templates T1-T7 + jumlah >= 40", test_templates)
    t("Z3 solver import + version", test_toolchain_z3)
    t("Camoufox terinstall", test_toolchain_camo)
    t("TokenBreak encoder works", test_toolchain_tokbreak)
    t("Caesar encoder works", test_toolchain_caesar)
    t("LLM API reachable (env, opsional)", test_llm_api)
    t("Gate stage1 vague tolak", test_gate)
    t("Gate module importable", test_gate_package)
    t("Gate CLI smoke test", test_gate_cli)
    t("Config SOUL.md ada + ZERO REFUSAL", test_config)
    t("Framework-core 5 modul ada + compile", test_framework_core)
    t("Semua file .py compile", test_all_python_compiles)
    t("Semua script .sh lolos bash -n", test_shell_syntax)
    t("Semua JSON/YAML valid", test_data_files_valid)
    t("VERSION <-> README <-> install.sh sinkron", test_version_consistency)
    t("Tidak ada placeholder USERNAME/t.me", test_no_placeholder)
    t("Tidak ada secret hardcoded", test_no_secret)
    t("Link relatif dokumen top-level valid", test_top_level_links)
    t("Manifest integritas skill cocok", test_manifest)

    print(f"\n=== RESULT: {PASS} passed, {FAIL} failed, {SKIP} skipped ===")
    if SKIPPED:
        print(f"Skip (dependency opsional): {SKIPPED}")
    if FAILED:
        print(f"Gagal: {FAILED}")
        return 1
    if STRICT and SKIP:
        print("STRICT: skip dianggap gagal")
        return 1
    print("ALL TESTS PASSED ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
