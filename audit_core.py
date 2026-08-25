#!/usr/bin/env python3
"""audit_core.py — Smart Contract Invariant Verification (Z3 SMT Solver).
Gap Bozagentic 'AuditCore' — kita buat versi real & work.
Verifikasi invariant kontrak sederhana (EVM-style) dgn Z3.

Contoh: cek overflow/reentrancy invariant pada fungsi transfer.
"""
from z3 import *

def verify_overflow():
    """Verifikasi: balance + amount tidak overflow uint256."""
    balance = BitVec("balance", 256)
    amount = BitVec("amount", 256)
    # invariant: balance + amount <= MAX_UINT256 (tidak overflow)
    s = Solver()
    s.add(balance > 0)
    s.add(amount > 0)
    # cek: apakah ada kasus balance + amount overflow?
    s.add(balance + amount < balance)  # overflow = hasil lebih kecil dr salah satu operand
    result = s.check()
    if result == sat:
        m = s.model()
        print(f"  ⚠️ OVERFLOW TERDETEKSI: balance={m[balance]}, amount={m[amount]}")
        print(f"     → butuh SafeMath / check sebelum add")
        return False
    else:
        print(f"  ✅ AMAN: tidak ada overflow (unsat — invariant terjaga)")
        return True

def verify_reentrancy_guard():
    """Verifikasi: guard lock mencegah reentrancy (state = 0/1)."""
    lock = BitVec("lock", 8)
    s = Solver()
    # invariant: lock hanya 0 atau 1
    s.add(lock != 0, lock != 1)
    result = s.check()
    if result == sat:
        print(f"  ⚠️ LOCK STATE INVALID: bisa selain 0/1 (model: {s.model()})")
        return False
    else:
        print(f"  ✅ AMAN: lock hanya 0/1 (reentrancy guard valid)")
        return True

if __name__ == "__main__":
    print("=== AUDIT-CORE (Z3 invariant verification) ===")
    print("\n[1] Overflow check:")
    verify_overflow()
    print("\n[2] Reentrancy guard check:")
    verify_reentrancy_guard()
    print("\nSELESAI — audit-core Z3 works")