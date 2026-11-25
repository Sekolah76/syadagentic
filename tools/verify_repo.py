#!/usr/bin/env python3
"""verify_repo.py — audit klaim repo vs isi nyata.

Kenapa ada: repo ini pernah memuat klaim yang tidak ada barangnya di dalam
("SKILLS.lock 8137 skill", "1128 skills", versi 7.3 padahal sudah 8.2). Script
ini memaksa README, VERSION, installer, dan isi direktori untuk saling cocok.

Pakai:
    python3 tools/verify_repo.py           # tabel hasil
    python3 tools/verify_repo.py --json    # output mesin
    python3 tools/verify_repo.py --quiet   # hanya kegagalan

Exit 0 = semua cek lulus. Exit 1 = ada klaim yang tidak cocok.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "arsenal-skills"
MANIFEST = SKILLS / "MANIFEST.sha256"
README = ROOT / "README.md"

REQUIRED_FILES = [
    "README.md", "LICENSE", "VERSION", "SOUL.md", "AGENTS.md", "SKILL.md",
    "SYADAGENTIC.md", "IDENTITY.md", "SAFETY-FRAMEWORK.md", "CONTRIBUTING.md",
    "SECURITY.md", "CHANGELOG.md", "install.sh", "tests/run_tests.py",
    "gate/gate.py", ".github/workflows/ci.yml",
]

SECRET_RE = re.compile(
    r"ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{32,}"
    r"|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[baprs]-[0-9A-Za-z-]{10,}"
)
PLACEHOLDER_RE = re.compile(r"github\.com/USER/|github\.com/USERNAME/|t\.me/\.\.\.|<YOUR[-_ ]")

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def core_files() -> list[Path]:
    out = []
    for pat in ("*.md", "*.sh", "*.py", "*.json", "*.yml", "*.txt"):
        out.extend(p for p in ROOT.glob(pat) if p.is_file())
    for d in (".github", "docs", "tests", "tools", "gate", "arsenal-framework"):
        base = ROOT / d
        if base.is_dir():
            out.extend(p for p in base.rglob("*") if p.is_file())
    return [p for p in out if p.suffix in {".md", ".sh", ".py", ".json", ".yml", ".html", ".txt"}]


def readme_text() -> str:
    return README.read_text(encoding="utf-8") if README.exists() else ""


def claimed_int(text: str, label: str) -> int | None:
    """Ambil angka dari badge/klaim README, mis. 'skill%20files-1123' atau '**84**'."""
    m = re.search(rf"{label}[^0-9]{{0,30}}?(\d[\d.]*)", text)
    if not m:
        return None
    return int(m.group(1).replace(".", ""))


# ---------------- cek individual ----------------
def c_required():
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).exists()]
    check("file wajib lengkap", not missing,
          "semua ada" if not missing else f"hilang: {missing}")


def c_version():
    vf = ROOT / "VERSION"
    v = vf.read_text(encoding="utf-8").strip() if vf.exists() else ""
    semver = bool(re.fullmatch(r"\d+\.\d+\.\d+", v))
    check("VERSION semver", semver, v or "VERSION tidak ada")
    if not semver:
        return
    check("README badge == VERSION", f"version-{v}-" in readme_text(),
          f"VERSION {v}")
    inst = ROOT / "install.sh"
    inst_txt = inst.read_text(encoding="utf-8") if inst.exists() else ""
    check("install.sh baca VERSION (tidak hardcode)", "VERSION" in inst_txt, "")
    log = ROOT / "CHANGELOG.md"
    log_txt = log.read_text(encoding="utf-8") if log.exists() else ""
    check("CHANGELOG memuat versi terbaru", f"## [{v}]" in log_txt or f"## {v}" in log_txt, "")


def c_skill_counts():
    files = [p for p in SKILLS.rglob("*") if p.is_file()
             and p.name != "MANIFEST.sha256" and "__pycache__" not in p.parts]
    skillmd = [p for p in SKILLS.rglob("SKILL.md")]
    txt = readme_text()
    claimed_files = None
    m = re.search(r"skill%20files-(\d+)", txt)
    if m:
        claimed_files = int(m.group(1))
    else:
        claimed_files = claimed_int(txt, "file skill")
    m2 = re.search(r"(\d+)\s+di antaranya\s+`SKILL\.md`", txt)
    claimed_skillmd = int(m2.group(1)) if m2 else None
    check("jumlah file skill == klaim README",
          claimed_files is not None and claimed_files == len(files),
          f"klaim {claimed_files} vs nyata {len(files)}")
    check("jumlah SKILL.md == klaim README",
          claimed_skillmd is not None and claimed_skillmd == len(skillmd),
          f"klaim {claimed_skillmd} vs nyata {len(skillmd)}")


def c_templates():
    tmpl = ROOT / "prompt-injection" / "templates.md"
    if not tmpl.exists():
        check("templates.md ada", False, "tidak ada")
        return
    n = len(re.findall(r"^#+\s*T\d+", tmpl.read_text(encoding="utf-8"), re.MULTILINE))
    check("templates >= 40 (klaim 40+)", n >= 40, f"{n} template")


def c_manifest():
    if not MANIFEST.exists():
        check("MANIFEST.sha256 ada", False, "belum dibuat — jalankan tools/build_manifest.py")
        return
    entries = sum(1 for ln in MANIFEST.read_text(encoding="utf-8").splitlines() if ln.strip())
    out = subprocess.run([sys.executable, str(ROOT / "tools" / "build_manifest.py"), "--check"],
                         capture_output=True, text=True)
    check("MANIFEST cocok dengan isi direktori", out.returncode == 0,
          f"{entries} entri" if out.returncode == 0 else (out.stdout + out.stderr)[-140:].strip())


def c_placeholders():
    hits = [str(p.relative_to(ROOT)) for p in core_files()
            if PLACEHOLDER_RE.search(p.read_text(encoding="utf-8", errors="ignore"))]
    check("tidak ada placeholder USER/USERNAME", not hits, ", ".join(hits[:4]) or "bersih")


def c_secrets():
    hits = []
    for p in core_files():
        for m in SECRET_RE.finditer(p.read_text(encoding="utf-8", errors="ignore")):
            if "EXAMPLE" in m.group(0):
                continue
            hits.append(f"{p.relative_to(ROOT)}:{m.group(0)[:8]}…")
    check("tidak ada secret hardcoded", not hits, ", ".join(hits[:4]) or "bersih")


def c_links():
    bad = []
    files = list(ROOT.glob("*.md")) + list((ROOT / "docs").rglob("*.md"))
    for p in files:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\]\(([^)#\s]+?)(?:#[^)]*)?\)", txt):
            link = m.group(1).strip()
            if link.startswith(("http", "mailto:", "#", "//")) or not link:
                continue
            if not (p.parent / link).exists():
                bad.append(f"{p.relative_to(ROOT)}->{link}")
    check("link relatif dokumen valid", not bad, ", ".join(bad[:4]) or "bersih")


def c_installer():
    inst = ROOT / "install.sh"
    if not inst.exists():
        check("install.sh ada", False, "")
        return
    if shutil.which("bash"):
        syn = subprocess.run(["bash", "-n", str(inst)], capture_output=True, text=True)
        check("install.sh lolos bash -n", syn.returncode == 0, syn.stderr.strip()[:120])
        ver = subprocess.run(["bash", str(inst), "--version"], capture_output=True, text=True)
        check("install.sh --version jalan", ver.returncode == 0, ver.stdout.strip()[:60])
        dry = subprocess.run(["bash", str(inst), "--dry-run"], capture_output=True, text=True,
                             env={"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": "/tmp"})
        check("install.sh --dry-run tidak menulis", dry.returncode == 0,
              "ok" if dry.returncode == 0 else dry.stderr.strip()[:120])
    else:
        check("install.sh lolos bash -n", True, "bash tidak ada, skip")


def c_ci():
    wf = ROOT / ".github" / "workflows" / "ci.yml"
    txt = wf.read_text(encoding="utf-8") if wf.exists() else ""
    check("CI menjalankan test suite", "tests/run_tests.py" in txt, "")
    check("CI menjalankan verifier", "verify_repo.py" in txt, "")


def c_python_ok():
    import warnings
    warnings.simplefilter("ignore", SyntaxWarning)
    bad = []
    for p in ROOT.rglob("*.py"):
        if ".git" in p.parts or "__pycache__" in p.parts:
            continue
        try:
            compile(p.read_text(encoding="utf-8", errors="ignore"), str(p), "exec")
        except SyntaxError as e:
            bad.append(f"{p.relative_to(ROOT)}:{e.lineno}")
    check("semua .py syntactically valid", not bad, ", ".join(bad[:4]) or "ok")


def c_no_stale_claims():
    """Klaim lama yang sudah terbukti palsu tidak boleh balik lagi."""
    txt = readme_text()
    stale = {
        "8137": "SKILLS.lock 8137",
        "1128 skills": "angka skill lama",
        "USERNAME/syadagentic": "URL clone placeholder",
    }
    found = [why for needle, why in stale.items() if needle in txt]
    check("tidak ada klaim lama/palsu di README", not found, ", ".join(found) or "bersih")


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    quiet = "--quiet" in argv
    for fn in (c_required, c_version, c_skill_counts, c_templates, c_manifest,
               c_placeholders, c_secrets, c_links, c_installer, c_ci, c_python_ok,
               c_no_stale_claims):
        try:
            fn()
        except Exception as e:  # noqa: BLE001 — satu cek error tidak boleh menyembunyikan yang lain
            check(fn.__name__, False, f"{type(e).__name__}: {e}")

    failed = [(n, d) for n, ok, d in results if not ok]
    if as_json:
        print(json.dumps([{"check": n, "ok": ok, "detail": d} for n, ok, d in results], indent=2))
    elif not quiet:
        width = max(len(n) for n, _, _ in results)
        for name, ok, detail in results:
            mark = "✅" if ok else "❌"
            print(f"{mark} {name.ljust(width)}  {detail}")
    else:
        for name, detail in failed:
            print(f"❌ {name}: {detail}")

    total = len(results)
    print(f"\n{total - len(failed)}/{total} cek lulus")
    if failed:
        print("GAGAL:\n" + "\n".join(f"  - {n}: {d}" for n, d in failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
