#!/usr/bin/env python3
"""drills.py — Agent Benchmark (dari frameworks/drills SYADAGENTIC + usulan teman).
Skenario latihan bertingkat utk mengukur kemampuan agent: TB3 vs zyro vs lainnya.
Level: L1-literal, L2-parse, L3-reason, L4-compose, L5-execute.
SyadAgentic v6.0 — executable, objektif per-level.
"""
import time, json, os

class Drill:
    def __init__(self, level, name, prompt, check, max_score=10):
        self.level = level
        self.name = name
        self.prompt = prompt
        self.check = check  # fn(response) -> (score, note)
        self.max_score = max_score

# ================= DRILLS (objektif, auto-scored) =================
DRILLS = [
    # L1: literasi / ekstraksi langsung
    Drill("L1", "ekstrak-json",
          "Dari teks ini ekstrak JSON-nya: 'mulai {\\\"id\\\":7,\\\"name\\\":\\\"test\\\"} selesai'",
          lambda r: (10, "JSON benar") if '\\"id\\":7'.replace('\\\\','') in r and '\\"test\\"'.replace('\\\\','') in r else (0, "tidak match")),
    # L2: parse + transform
    Drill("L2", "parse-csv",
          "Dari CSV 'a,b,c\\n1,2,3' ubah ke format JSON array",
          lambda r: (10, "ok") if '"a' in r and '1' in r else (0, "gagal")),
    # L3: reasoning logika
    Drill("L3", "logika",
          "3 apel + 2 apel = 5. Kalau 10 apel dibagi ke 3 orang rata-rata, berapa tiap orang dan sisa berapa?",
          lambda r: (10, "benar") if ('3' in r and ('sisa 1' in r or 'remainder 1' in r.lower())) else (0, "salah hitung")),
    # L4: compose multi-step
    Drill("L4", "compose",
          "Tulis python function `process(nums)` yang: filter genap, double-kan, sum. Contoh process([1,2,3,4]) = 12",
          lambda r: (10, "benar") if 'sum' in r and '2' in r and 'filter' in r.lower() else (0, "kurang")),
    # L5: execute (bikin script + jalankan)
    Drill("L5", "execute",
          "Buat dan jalankan python script yang print 'DRILL_EXECUTE_OK' lalu output hasilnya",
          lambda r: (10, "ok") if 'DRILL_EXECUTE_OK' in r else (0, "belum execute")),
]

def run_drill(drill, responder):
    """responder(prompt) -> response string (dari model/agent)."""
    t0 = time.time()
    resp = responder(drill.prompt)
    dt = time.time() - t0
    score, note = drill.check(resp)
    return {"level": drill.level, "name": drill.name, "score": score,
            "max": drill.max_score, "time": round(dt, 2), "note": note}

def benchmark(responder, name="agent"):
    results = [run_drill(d, responder) for d in DRILLS]
    total = sum(r["score"] for r in results)
    max_total = sum(d.max_score for d in DRILLS)
    print(f"\n=== BENCHMARK: {name} ===")
    for r in results:
        bar = "█" * (r["score"] * 2 // 2)
        print(f"  [{r['level']}] {r['name']:14s} {r['score']}/{r['max']} ({r['time']}s) {bar} {r['note']}")
    pct = total * 100 // max_total
    print(f"\n  TOTAL: {total}/{max_total} ({pct}%)")
    return {"agent": name, "total": total, "max": max_total, "pct": pct, "by_level": {r['level'] for r in results}}

# ================= DEMO (executable — pakai responder dummy) =================
if __name__ == "__main__":
    # Responder dummy yang selalu benar utk tes benchmark runner
    def dummy_responder(prompt):
        return {
            "ekstrak-json": '{"id":7,"name":"test"}',
            "parse-csv": '[{"a":1,"b":2,"c":3}]',
            "logika": "tiap orang 3, sisa 1",
            "compose": "def process(nums): return sum(x*2 for x in nums if x%2==0)",
            "execute": "Running... output:\nDRILL_EXECUTE_OK\n",
        }[next(d.name for d in DRILLS if d.prompt == prompt)]

    benchmark(dummy_responder, "dummy-perfect")
    print("\n(Nilai asli = pakai model nyata via responder callback — ini demo runner)")