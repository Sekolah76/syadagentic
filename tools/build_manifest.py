#!/usr/bin/env python3
"""build_manifest.py — manifest integritas arsenal-skills (SHA256).

Kenapa ada: README/SOUL dulu klaim "SKILLS.lock 8137 skill" padahal file-nya
tidak pernah ada di repo. Script ini bikin klaim itu jadi benar-benar nyata dan
bisa diverifikasi siapa pun.

Pakai:
    python3 tools/build_manifest.py          # tulis ulang MANIFEST.sha256
    python3 tools/build_manifest.py --check  # verifikasi (exit 1 kalau beda)
    python3 tools/build_manifest.py --quiet  # hanya ringkasan

Format tiap baris: <sha256>  <path relatif dari arsenal-skills/>
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "arsenal-skills"
MANIFEST = TARGET / "MANIFEST.sha256"
SKIP_NAMES = {"MANIFEST.sha256"}
SKIP_DIRS = {"__pycache__", ".git"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def scan() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for p in sorted(TARGET.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name in SKIP_NAMES:
            continue
        rows.append((digest(p), p.relative_to(TARGET).as_posix()))
    return rows


def main(argv: list[str]) -> int:
    check = "--check" in argv
    quiet = "--quiet" in argv
    if not TARGET.is_dir():
        print(f"[x] {TARGET} tidak ada", file=sys.stderr)
        return 2

    rows = scan()
    if check:
        if not MANIFEST.exists():
            print("[x] MANIFEST.sha256 belum ada — jalankan tanpa --check dulu", file=sys.stderr)
            return 1
        expected = {}
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            sha, _, rel = line.partition("  ")
            expected[rel.strip()] = sha.strip()
        actual = {rel: sha for sha, rel in rows}
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        changed = sorted(r for r in set(expected) & set(actual) if expected[r] != actual[r])
        if missing or extra or changed:
            print(f"[x] manifest TIDAK cocok ({len(rows)} file dipindai)")
            for label, items in (("hilang", missing), ("baru", extra), ("berubah", changed)):
                if items:
                    print(f"    {label}: {len(items)} -> {items[:5]}")
            return 1
        print(f"[✓] manifest cocok — {len(rows)} file terverifikasi")
        return 0

    body = "\n".join(f"{sha}  {rel}" for sha, rel in rows) + "\n"
    MANIFEST.write_text(body, encoding="utf-8")
    if not quiet:
        print(f"[✓] ditulis {MANIFEST.relative_to(ROOT)} — {len(rows)} file")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
