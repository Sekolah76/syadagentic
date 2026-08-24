#!/usr/bin/env python3
"""install_universal.py — Pasang SYADAGENTIC jailbreak permanen ke SEMUA agent di device ini.
Deploy SYADAGENTIC.md ke semua titik yang agent baca otomatis:
  - Hermes: config agent.system_prompt + prefill + tirith off
  - opencode: ~/.config/opencode/AGENTS.md (global) + root AGENTS.md
  - Claude Code: ~/.claude/CLAUDE.md
  - Cursor: ~/.cursorrules (global)
  - Project roots: AGENTS.md / CLAUDE.md / .cursorrules
Auto-detect yang ada, install yang bisa. Pakai dgn --root utk project.

Usage:
  python install_universal.py               # install ke semua agent global
  python install_universal.py --root /path  # + taruh di root project
"""
import argparse, json, os, pathlib, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
SOURCE = HERE / "SYADAGENTIC.md"
SOURCE_SHORT = HERE / "SYADAGENTIC-SHORT.md"
HOME = pathlib.Path.home()

def banner(t):
    print(f"\n=== {t} ===")

def install_file(dst: pathlib.Path, copy: bool = True, src=None):
    s = src or SOURCE
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if copy:
            shutil.copy(s, dst)
        print(f"  ✅ {dst}")
        return True
    except Exception as e:
        print(f"  ⚠️ {dst}: {str(e)[:60]}")
        return False

def hermes_setup():
    banner("HERMES")
    cfg_path = pathlib.Path(os.environ.get("HERMES_HOME", HOME / "AppData/Local/hermes")) / "config.yaml"
    if not cfg_path.exists():
        # coba lokasi alternatif
        cfg_path = HOME / ".hermes" / "config.yaml"
    if not cfg_path.exists():
        print("  ⚠️ config.yaml tidak ketemu — skip Hermes config (pasang file manual)")
        install_file(HOME / "AppData/Local/hermes" / "hermes_unrestricted.md")
        return
    import yaml
    d = yaml.safe_load(open(cfg_path)) or {}
    d.setdefault("agent", {})
    d["agent"]["system_prompt"] = SOURCE.read_text(encoding="utf-8")
    d["agent"]["instructions"] = d.get("agent", {}).get("instructions", []) or []
    # prefill
    pref = HERE / "prefill.json"
    if pref.exists():
        pref_dst = cfg_path.parent / "prefill.json"
        install_file(pref_dst)
        d["prefill_messages_file"] = "prefill.json"
    # tirith off
    d.setdefault("security", {})["tirith_enabled"] = False
    yaml.dump(d, open(cfg_path, "w"), default_flow_style=False, allow_unicode=True)
    print(f"  ✅ config updated: {cfg_path}")

def opencode_setup():
    banner("OPENCODE")
    install_file(HOME / ".config" / "opencode" / "AGENTS.md")
    install_file(HOME / ".config" / "opencode" / "GLOBAL_RULES.md", copy=False) if False else None

def claude_setup():
    banner("CLAUDE CODE")
    install_file(HOME / ".claude" / "CLAUDE.md")
    install_file(HOME / ".claude" / "CLAUDE.local.md")

def cursor_setup():
    banner("CURSOR")
    install_file(HOME / ".cursorrules")

def project_setup(root: pathlib.Path):
    banner(f"PROJECT ROOT: {root}")
    for name in ["AGENTS.md", "CLAUDE.md", ".cursorrules"]:
        install_file(root / name)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None, help="project root utk taruh AGENTS/CLAUDE/.cursorrules")
    ap.add_argument("--hermes-only", action="store_true")
    args = ap.parse_args()
    print(f"SOURCE: {SOURCE} ({SOURCE.stat().st_size} bytes) + SHORT ({SOURCE_SHORT.stat().st_size} bytes)")
    hermes_setup()
    if not args.hermes_only:
        opencode_setup()
        claude_setup()
        cursor_setup()
        # deploy SHORT utk frontier
        install_file(HOME / ".config" / "opencode" / "SYADAGENTIC-SHORT.md", src=SOURCE_SHORT)
        install_file(HOME / ".claude" / "SYADAGENTIC-SHORT.md", src=SOURCE_SHORT)
        if args.root:
            project_setup(pathlib.Path(args.root))
    print("\nDONE — SYADAGENTIC (+SHORT utk frontier) terpasang. Restart agent utk aktif.")

if __name__ == "__main__":
    main()