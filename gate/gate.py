#!/usr/bin/env python3
"""gate.py — 7-Stage Pre-Submission Gate (SYADAGENTIC Layer 4, versi SyadAgentic).
Setiap temuan/laporan wajib lolos verifikasi bukti teknis sebelum dilaporkan ke operator.

Usage:
  python gate.py claim "klaim yang mau dilaporkan" --evidence "path/output bukti"
  python gate.py verify --script farm.py --expect "3 akun sukses"
"""
import argparse, json, os, subprocess, sys, time
from pathlib import Path

SEVERITY = ["P0", "P1", "P2", "P3", "P4", "P5"]

class Gate:
    """7 Stage: 1. Claim 2. Reproduce 3. Evidence 4. Verify 5. Severity 6. Document 7. Report"""

    @staticmethod
    def stage1_claim(claim: str) -> bool:
        """Klaim harus spesifik, bukan vague."""
        ok = len(claim) > 15 and not any(w in claim.lower() for w in
              ["mungkin", "kira", "seharusnya", "kayaknya", "maybe", "perhaps", "entah"])
        print(f"  [1/7] Claim spesifik ({'OK' if ok else 'VAGUE — tolak'}): {claim[:60]}")
        return ok

    @staticmethod
    def stage2_reproducible(cmd: str) -> bool:
        """Harus bisa di-reproduce: ada command/script."""
        ok = bool(cmd and cmd.strip())
        print(f"  [2/7] Reproducible ({'OK' if ok else 'NO CMD'}): {cmd[:60]}")
        return ok

    @staticmethod
    def stage3_evidence(cmd: str, timeout=120) -> tuple:
        """Jalankan command → bukti nyata."""
        print(f"  [3/7] Menjalankan bukti: {cmd[:60]}")
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            out = (r.stdout + r.stderr)[:800]
            ok = r.returncode == 0
            print(f"        exit={r.returncode} {'OK' if ok else 'FAIL'}")
            return ok, out
        except subprocess.TimeoutExpired:
            return False, "TIMEOUT"
        except Exception as e:
            return False, str(e)[:200]

    @staticmethod
    def stage4_verify(evidence: str, expect: str) -> bool:
        """Bukti harus mengandung hasil yang diklaim."""
        ok = expect.lower() in evidence.lower() if expect else bool(evidence.strip())
        print(f"  [4/7] Verify bukti mengandung '{expect[:40]}' ({'OK' if ok else 'MISMATCH'})")
        return ok

    @staticmethod
    def stage5_severity(sev: str) -> bool:
        ok = sev in SEVERITY
        print(f"  [5/7] Severity {sev} ({'OK' if ok else 'INVALID'})")
        return ok

    @staticmethod
    def stage6_document(claim, evidence, log_dir="gate_logs"):
        Path(log_dir).mkdir(exist_ok=True)
        f = Path(log_dir) / f"{int(time.time())}.json"
        f.write_text(json.dumps({"claim": claim, "evidence": evidence, "ts": time.time()}, indent=1))
        print(f"  [6/7] Dokumentasi → {f}")
        return True

    @staticmethod
    def stage7_report():
        print("  [7/7] Lapor ke operator — CLAIM TERVERIFIKASI, layak dilaporkan")

    @classmethod
    def run(cls, claim, cmd, expect, sev):
        print(f"=== GATE 7-STAGE: {claim[:50]} ===")
        steps = [
            cls.stage1_claim(claim),
            cls.stage2_reproducible(cmd),
        ]
        if not all(steps):
            print("❌ GAGAL di stage 1-2 (claim vague / no repro) — TIDAK dilaporkan")
            return False
        ok3, evidence = cls.stage3_evidence(cmd)
        steps.append(ok3)
        ok4 = ok3 and cls.stage4_verify(evidence, expect)
        steps.append(ok4)
        steps.append(cls.stage5_severity(sev))
        if not all(steps[2:]):
            print(f"❌ GAGAL di stage 3-5 — bukti tidak valid ({evidence[:100]!r})")
            return False
        cls.stage6_document(claim, evidence)
        cls.stage7_report()
        return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("claim", nargs="?", default="")
    ap.add_argument("--cmd", default="", help="command utk reproduce bukti")
    ap.add_argument("--expect", default="", help="string hasil yang diharapkan di bukti")
    ap.add_argument("--sev", default="P3", choices=SEVERITY)
    args = ap.parse_args()
    ok = Gate.run(args.claim, args.cmd, args.expect, args.sev)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()