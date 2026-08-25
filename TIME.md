# TIME.md — Time & Continuity (SYADAGENTIC)
# Kesadaran waktu + continuity lintas sesi.

## WAKTU
- Zona: UTC+7 (Asia/Jakarta)
- Format laporan: [YYYY-MM-DD HH:MM WIB]

## CONTINUITY
- Context compaction = referensi, bukan pengganti — protokol tetap.
- Anti-drift hook: [EXECUTION CONTEXT: L0 ...] di tiap pembacaan.
- State penting disimpan: memory + CHAIN.md + RESULTS-MATRIX.

## SESI PANJANG
- Deadline per request: 90s (kecuali model reasoning — 300s+)
- Paralel kalau bisa (tool batch)
- Long task → background + notify