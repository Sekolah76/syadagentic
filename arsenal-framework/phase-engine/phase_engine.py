#!/usr/bin/env python3
"""phase_engine.py — Phase Engine (terinspirasi WebHunter OS 8-phase, tapi executable).
Fase generik: recon → map → model → test → validate → report.
Preset: pentest, osint, project-build. State JSON + checkpoint/resume.
SyadAgentic v6.0 — bukan stub (teruji nyata).
"""
import json, os, sys, datetime, traceback

class PhaseEngine:
    def __init__(self, name, preset="generic", state_dir=".phase-state"):
        self.name = name
        self.preset = preset
        self.state_dir = state_dir
        self.state_file = os.path.join(state_dir, f"{name}.json")
        os.makedirs(state_dir, exist_ok=True)
        self.state = self._load()

    def _load(self):
        if os.path.exists(self.state_file):
            try:
                return json.load(open(self.state_file, encoding="utf-8"))
            except Exception:
                pass
        return {"phase": 0, "phases": [], "data": {}, "started": None, "updated": None,
                "checkpoints": [], "log": []}

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
        """Jalankan satu fase dengan checkpoint. fn = callable(engine, ctx) -> dict hasil."""
        phase = self.current_phase()
        if not phase:
            self.log("⚠ Semua fase selesai")
            return None
        self.log(f"▸ Fase [{phase}] dimulai")
        try:
            result = fn(self, *args, **kwargs)
            self.state["data"][phase] = result
            # checkpoint otomatis
            self.state["checkpoints"].append({"phase": phase, "at": datetime.datetime.now().isoformat()})
            self.state["phase"] += 1
            self.log(f"✓ Fase [{phase}] selesai ({len(str(result))} chars data)")
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
        lines.append(f"  Checkpoints: {len(self.state['checkpoints'])} | Log: {len(self.state['log'])}")
        return "\n".join(lines)

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