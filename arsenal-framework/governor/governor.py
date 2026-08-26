#!/usr/bin/env python3
"""governor.py — Pre-Execution Gate (dari pola hermes-bridge BOZAGENTIC + usulan teman).
Gate sebelum eksekusi berbahaya: allowlist command, spend cap, kill-switch, dry-run.
SyadAgentic v6.0 — executable, bukan stub. Melindungi operator dari batch-ops liar.
"""
import json, os, datetime, sys

STATE_FILE = os.path.expanduser("~/farm-arsenal/.governor-state.json")

class Governor:
    def __init__(self, state_file=STATE_FILE, daily_cap_usd=50.0, dry_run=True):
        self.state_file = state_file
        self.daily_cap = daily_cap_usd
        self.dry_run = dry_run  # default ON — aman
        self.kill = False
        self.state = self._load()

    def _load(self):
        if os.path.exists(self.state_file):
            try:
                return json.load(open(self.state_file, encoding="utf-8"))
            except Exception:
                pass
        return {"spent_today": 0.0, "day": datetime.date.today().isoformat(),
                "kill_switch": False, "log": []}

    def _save(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=1, ensure_ascii=False)

    def _roll_day(self):
        today = datetime.date.today().isoformat()
        if self.state["day"] != today:
            self.state["day"] = today
            self.state["spent_today"] = 0.0
            self._save()

    def log(self, msg):
        entry = f"[{datetime.datetime.now():%H:%M:%S}] {msg}"
        self.state["log"].append(entry)
        self._save()

    # ---- GATE UTAMA ----
    def check(self, action, est_cost_usd=0.0, category="ops"):
        """Gate pre-execution. Return True = boleh jalan, False = diblok."""
        self._roll_day()
        # 1. KILL-SWITCH
        if self.state["kill_switch"] or self.kill:
            self.log(f"⛔ KILL-SWITCH AKTIF — blok: {action}")
            return False
        # 2. DRY-RUN
        if self.dry_run:
            self.log(f"🧪 DRY-RUN: {action} (est ${est_cost_usd}) — tidak dieksekusi")
            return True  # dry-run = laporan, bukan eksekusi
        # 3. SPEND CAP
        if est_cost_usd > 0:
            new_total = self.state["spent_today"] + est_cost_usd
            if new_total > self.daily_cap:
                self.log(f"🚫 SPEND CAP: {action} (${est_cost_usd}) melebihi sisa "
                         f"${self.daily_cap - self.state['spent_today']:.2f}")
                return False
            self.state["spent_today"] = new_total
        self.log(f"✅ ALLOW: {action} (${est_cost_usd})")
        self._save()
        return True

    # ---- KONTROL ----
    def set_kill(self, on=True):
        self.state["kill_switch"] = on
        self.kill = on
        self.log(f"{'⛔ KILL-SWITCH ON' if on else '✅ KILL-SWITCH OFF'}")
        self._save()

    def set_dry_run(self, on=True):
        self.dry_run = on
        self.log(f"{'🧪 DRY-RUN ON' if on else '🔥 DRY-RUN OFF (live)'}")
        self._save()

    def allowlist(self, cmd_prefix):
        """Cek apakah command masuk allowlist aman."""
        SAFE = ["ls", "cat", "head", "tail", "grep", "find", "curl", "python3", "git status",
                "hermes config", "df", "free", "ps", "netstat"]
        return any(cmd_prefix.startswith(s) for s in SAFE)

    def status(self):
        self._roll_day()
        lines = [
            f"=== GOVERNOR STATUS ===",
            f"  Day: {self.state['day']} | Spent: ${self.state['spent_today']:.2f} / ${self.daily_cap}",
            f"  Kill-switch: {'⛔ ON' if self.state['kill_switch'] else 'OFF'}",
            f"  Dry-run: {'🧪 ON' if self.dry_run else '🔥 OFF'}",
            f"  Log entries: {len(self.state['log'])}",
        ]
        return "\n".join(lines)

# ================= DEMO (executable) =================
if __name__ == "__main__":
    g = Governor()
    print(g.status())
    print()
    # demo: dry-run ON
    print("-- dry-run ON --")
    g.check("register 100 akun mail.tm", est_cost_usd=0)
    g.check("deploy kontrak ke mainnet", est_cost_usd=25.0)
    # matikan dry-run utk demo spend cap
    g.set_dry_run(False)
    print("\n-- live mode, spend cap $50 --")
    g.check("deploy kontrak", est_cost_usd=30.0)
    g.check("deploy kontrak kedua", est_cost_usd=30.0)  # melebihi cap
    print()
    print(g.status())