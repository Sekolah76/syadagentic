#!/usr/bin/env python3
"""phase_engine.py — Phase Engine (terinspirasi WebHunter OS 8-phase, tapi executable).
Fase generik: recon → map → model → test → validate → report.
Preset: pentest, osint, project-build. State JSON + checkpoint/resume.
+ BUDGET-PER-FASE & CONTEXT-COMPRESSION (token efficiency — jawaban loop boros).
SyadAgentic v6.3 — bukan stub (teruji nyata).
"""
import json, os, sys, datetime, traceback, re

class PhaseEngine:
    def __init__(self, name, preset="generic", state_dir=".phase-state",
                 token_budget_per_phase=8000, compression_char_limit=3000):
        self.name = name
        self.preset = preset
        self.state_dir = state_dir
        self.token_budget = token_budget_per_phase  # token per fase (anti-boros)
        self.comp_char_limit = compression_char_limit  # compress data fase besar
        self.state_file = os.path.join(state_dir, f"{name}.json")
        os.makedirs(state_dir, exist_ok=True)
        self.state = self._load()

    def _load(self):
        if os.path.exists(self.state_file):
            try:
                st = json.load(open(self.state_file, encoding="utf-8"))
                # MIGRASI: pastikan key baru ada (state lama tanpa token budget)
                st.setdefault("token_used", 0)
                st.setdefault("compressed", 0)
                return st
            except Exception:
                pass
        return {"phase": 0, "phases": [], "data": {}, "started": None, "updated": None,
                "checkpoints": [], "log": [], "token_used": 0, "compressed": 0}

    def _save(self):
        self.state["updated"] = datetime.datetime.now().isoformat()
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=1, ensure_ascii=False)

    def log(self, msg):
        entry = f"[{datetime.datetime.now():%H:%M:%S}] {msg}"
        self.state["log"].append(entry)
        print(entry)
        self._save()

    # ---- FASE DEFINISI (generic 8-phase) ----
    PHASES = {
        "generic": ["recon", "map", "model", "test", "validate", "report"],
        "pentest": ["recon", "enum", "map", "exploit", "post-exploit", "validate", "report"],
        "osint": ["collect", "enrich", "correlate", "analyze", "verify", "report"],
        "project-build": ["requirements", "design", "scaffold", "implement", "test", "deploy", "report"],
    }

    def start(self):
        phases = self.PHASES.get(self.preset, self.PHASES["generic"])
        if not self.state["phases"]:
            self.state["phases"] = phases
            self.state["started"] = datetime.datetime.now().isoformat()
            self.state["phase"] = 0
            self.log(f"▶ Engine '{self.name}' [{self.preset}] start — {len(phases)} fase")
            self._save()
        else:
            self.log(f"▶ Resume engine '{self.name}' di fase {self.state['phase']}/{len(self.state['phases'])}")

    def current_phase(self):
        phases = self.state["phases"]
        idx = min(self.state["phase"], len(phases) - 1)
        return phases[idx] if phases else None

    def run_phase(self, fn, *args, **kwargs):
        """Jalankan satu fase dengan checkpoint + budget token + compression."""
        phase = self.current_phase()
        if not phase:
            self.log("⚠ Semua fase selesai")
            return None
        self.log(f"▸ Fase [{phase}] dimulai (budget {self.token_budget} token)")
        try:
            result = fn(self, *args, **kwargs)
            # COMPRESSION: data besar di-compress supaya tidak bloat state
            if isinstance(result, dict):
                for k, v in result.items():
                    if isinstance(v, str) and len(v) > self.comp_char_limit:
                        result[k] = v[:self.comp_char_limit] + f"...[compressed {len(v)}→{self.comp_char_limit}]"
                        self.state["compressed"] += 1
            elif isinstance(result, str) and len(result) > self.comp_char_limit:
                result = result[:self.comp_char_limit] + f"...[compressed {len(result)}→{self.comp_char_limit}]"
                self.state["compressed"] += 1
            result_str = str(result)
            # TOKEN BUDGET: estimasi token = char/4; warning kalau melebihi
            est_tokens = len(result_str) // 4
            self.state["token_used"] += est_tokens
            self.state["data"][phase] = result
            self.state["checkpoints"].append({"phase": phase, "at": datetime.datetime.now().isoformat(),
                                               "tokens": est_tokens})
            self.state["phase"] += 1
            flag = ""
            if est_tokens > self.token_budget:
                flag = f" ⚠ melebihi budget {est_tokens}/{self.token_budget}"
            self.log(f"✓ Fase [{phase}] selesai ({est_tokens} token){flag}")
            self._save()
            return result
        except Exception as e:
            self.log(f"✗ Fase [{phase}] GAGAL: {e}")
            self.log(f"  → resume nanti dari fase [{phase}] (checkpoint tersimpan)")
            traceback.print_exc()
            raise

    def resume(self):
        """Lanjutkan dari fase terakhir yang selesai."""
        phases = self.state["phases"]
        self.log(f"↻ Resume: fase {self.state['phase']}/{len(phases)} — next: {self.current_phase()}")

    def report(self):
        """Generate laporan ringkas dari state."""
        lines = [f"=== REPORT: {self.name} [{self.preset}] ==="]
        for i, ph in enumerate(self.state["phases"]):
            status = "✓" if i < self.state["phase"] else ("▸" if i == self.state["phase"] else "·")
            data = self.state["data"].get(ph)
            size = len(str(data)) if data else 0
            lines.append(f"  {status} {ph} ({size} chars)")
        lines.append(f"  Token dipakai: {self.state['token_used']} | Tercompress: {self.state['compressed']} | Checkpoints: {len(self.state['checkpoints'])}")
        return "\n".join(lines)

    def learn(self, lesson_dir=None):
        """AUTO-SKILL LOOP (compound learning): simpan pelajaran dari run ini ke 
        skills/GBrain — sesi berikutnya makin pintar. Bukan sekali pakai."""
        if lesson_dir is None:
            lesson_dir = os.path.join(self.state_dir, "..", "grain")
        lesson_dir = os.path.abspath(lesson_dir)
        os.makedirs(lesson_dir, exist_ok=True)
        # pelajaran = fase yang selesai + token + error log
        done = [ph for i, ph in enumerate(self.state["phases"]) if i < self.state["phase"]]
        errors = [l for l in self.state["log"] if "GAGAL" in l or "✗" in l]
        lesson = {
            "engine": self.name,
            "preset": self.preset,
            "date": datetime.date.today().isoformat(),
            "phases_done": done,
            "tokens": self.state["token_used"],
            "compressed": self.state["compressed"],
            "errors": errors[-3:],
            "tip": f"Engine {self.name} [{self.preset}] selesai {len(done)} fase dgn {self.state['token_used']} token",
        }
        fname = os.path.join(lesson_dir, f"{self.name}-{datetime.datetime.now():%Y%m%d-%H%M}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(lesson, f, indent=1, ensure_ascii=False)
        self.log(f"🧠 Auto-skill: pelajaran disimpan ke {os.path.basename(fname)}")
        return fname

# ================= PRESET CONTOH (executable) =================
if __name__ == "__main__":
    # demo project-build: scaffold → implement → test
    eng = PhaseEngine("demo-build", preset="project-build")
    eng.start()

    def do_scaffold(e, ctx):
        # simulasi: bikin struktur proyek
        os.makedirs(ctx.get("project", "demo"), exist_ok=True)
        with open(os.path.join(ctx.get("project", "demo"), "app.py"), "w") as f:
            f.write("# demo app\nprint('hello')\n")
        return {"files": ["app.py"], "status": "created"}

    def do_implement(e, ctx):
        # baca + tambah fungsi
        p = os.path.join(ctx.get("project", "demo"), "app.py")
        with open(p, "a") as f:
            f.write("\ndef add(a,b): return a+b\n")
        return {"status": "implemented", "line_count": len(open(p).readlines())}

    def do_test(e, ctx):
        # test sederhana
        import subprocess
        p = os.path.join(ctx.get("project", "demo"), "app.py")
        r = subprocess.run(["python", "-c", f"exec(open(r'{p}').read()); assert add(2,3)==5; print('TEST PASS')"],
                           capture_output=True, text=True)
        return {"test": r.stdout.strip(), "rc": r.returncode}

    eng.run_phase(do_scaffold, {"project": "demo"})
    eng.run_phase(do_implement, {"project": "demo"})
    eng.run_phase(do_test, {"project": "demo"})
    print()
    print(eng.report())