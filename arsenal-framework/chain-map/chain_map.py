#!/usr/bin/env python3
"""chain_map.py — Chain Taxonomy (dari attack-chains SYADAGENTIC + usulan teman).
Tiap temuan punya jalur eskalasi: primitif → kombinasi → impact.
Generalisasi lintas domain: pentest, OSINT, monetisasi.
SyadAgentic v6.0 — executable, bukan stub.
"""
import json, os

class ChainMap:
    def __init__(self):
        self.chains = {}

    def add_chain(self, domain, name, primitives, escalation, impact, mandatory_proof=None):
        """Daftarkan chain: primitives (awal), escalation (jalur naik), impact (hasil)."""
        self.chains.setdefault(domain, []).append({
            "name": name,
            "primitives": primitives,
            "escalation": escalation,
            "impact": impact,
            "mandatory_proof": mandatory_proof or [],
        })

    def analyze(self, domain, finding):
        """Cek: finding ini bisa eskalasi ke mana? Return daftar jalur."""
        finding_low = finding.lower()
        results = []
        for chain in self.chains.get(domain, []):
            # match primitif
            matched = [p for p in chain["primitives"] if p.lower() in finding_low]
            if matched:
                results.append({
                    "chain": chain["name"],
                    "matched_primitive": matched,
                    "next": chain["escalation"],
                    "impact": chain["impact"],
                    "proof_required": chain["mandatory_proof"],
                })
        return results

    def report(self, domain=None):
        lines = ["=== CHAIN MAP ==="]
        for d, chains in self.chains.items():
            if domain and d != domain:
                continue
            lines.append(f"\n[{d}]")
            for c in chains:
                lines.append(f"  • {c['name']}: {' → '.join(c['escalation'][:4])} → IMPACT:{c['impact']}")
        return "\n".join(lines)

# ================= PRESET CHAINS (executable) =================
if __name__ == "__main__":
    cm = ChainMap()

    # PENTEST chain (dari attack-chains web2)
    cm.add_chain("pentest", "Auth-Bypass → PrivEsc",
                 primitives=["user identifier", "reset token", "auth cookie", "password reset"],
                 escalation=["session hijack", "privilege escalation", "admin access"],
                 impact="FULL ACCOUNT TAKEOVER",
                 mandatory_proof=["exact identifier accepted", "session works on admin"])

    cm.add_chain("pentest", "IDOR → Data Exfil",
                 primitives=["object id", "user id", "numeric id"],
                 escalation=["read other user data", "modify other user data"],
                 impact="DATA BREACH",
                 mandatory_proof=["different user's object returned"])

    # OSINT chain (generalisasi — usulan teman)
    cm.add_chain("osint", "Email → Breach → Creds → Access",
                 primitives=["email address", "username", "phone"],
                 escalation=["breach database match", "password reuse", "credential stuffing"],
                 impact="ACCOUNT ACCESS",
                 mandatory_proof=["breach record exists", "password hash matches"])

    # MONETISASI chain (generalisasi)
    cm.add_chain("monetize", "Skill → Produk → Channel → Revenue",
                 primitives=["skill", "template", "framework"],
                 escalation=["productize", "package", "distribution channel"],
                 impact="REVENUE",
                 mandatory_proof=["product packaged", "channel live"])

    print(cm.report())
    print()
    print("=== ANALISIS FINDING ===")
    finding = "ditemukan user id 1234 di API /users/1234 — bisa akses data user lain"
    for r in cm.analyze("pentest", finding):
        print(f"  ⚡ Chain: {r['chain']}")
        print(f"     matched: {r['matched_primitive']}")
        print(f"     next: {r['next']}")
        print(f"     impact: {r['impact']}")
        print(f"     proof: {r['proof_required']}")