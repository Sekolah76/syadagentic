# TECHNIQUES-EXTRACTION PART 2 — Tools .py (non-crypto, dari baca langsung)
# Lanjutan kurasi tools/ SYADAGENTIC. Hanya pola NON-CRYPTO yang reusable.

## POLA UMUM YANG BERGUNA (bukan crypto)

### Humanizer (content/humanizer.py)
- Deteksi "AI-tell" + rewrite deterministik jd natural (regex, stdlib, keyless)
- "tricolon-berulang → variasikan, jangan selalu 3"
- Burstiness: panjang kalimat seragam = AI-tell → variasikan
- Rewrite berat tetap lewat LLM (model_registry)

### API-first harvesting (intelligence/api_harvester.py)
- DevTools → Network → "Copy as cURL" → parse_curl() → paginate_* → extract() → to_*
- "Browser = LAST RESORT" — replikasi request, bukan klik-klik
- Kurangi footprint anti-bot + hemat resource

### Global Dry-Run (meta/dryrun.py)
- Satu flag dihormati SEMUA engine: kalau aktif → jalanin full pipeline TANPA 
  broadcast, kumpulin "yang bakal terjadi"
- Safety structural (bukan prompt)

### Compounding Memory (meta/memory_engine.py)
- Simpan fakta/pelajaran/preferensi/keputusan/blocker+resolusi → recall relevan
- "makin pinter tiap hari" — substrat self-improvement

### Self-Improvement Loop (meta/reflection.py)
- LEARN: scan memory/log → distill pola jadi 'lesson' (simpan ke memory)
- Gerbang ketat: apa yang boleh auto-apply vs butuh konfirmasi

### Multi-Agent Swarm (meta/swarm.py)
- Spawn specialist lane paralel (researcher/executor/monitor) → agregasi
- In-process & ringan, kompatibel delegate architecture

### Bulk Runner (monetization/revenue_engine.py)
- Rate-limit, backoff, checkpoint-resume, dedupe — murni stdlib, uji offline

## CATATAN
- File tools .py lainnya = crypto/web3/airdrop (alpha_radar, eligibility, farm_roi,
  unlock_engine, exit_planner, security_daemon, team_auth SIWE, auto_bot, 
  contract_watch) = DIHAPUS sesuai user — tidak di-merge
- Pola di atas = umum (bukan crypto) → berguna utk SyadAgentic framework