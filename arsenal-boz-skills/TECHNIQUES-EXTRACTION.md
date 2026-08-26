# TECHNIQUES-EXTRACTION.md — Teknik Non-Crypto Terbaik dari BOZAGENTIC (kurasi subagent)
# Sumber: subagent-summary-2 (skills, 670s) + subagent-summary-1 (frameworks, 1406s)
# Hanya teknik NON-CRYPTO (crypto dihapus sesuai user) — langsung dipakai utk farming/
# automation/bot. Detail lengkap: bozagentic_frameworks_extraction.md (51KB).

## 🥇 CAPTCHA / ANTI-BOT SOLVER (9 VENDOR — zero-cost)
- Universal solver sidecar: `universal_solver.py` sbg IPC service; tiap provider = modul
  `solve.py --url --sitekey`
- Cloudflare Turnstile/Interstitial: harvest `cf_clearance` cookie
- Aliyun 2.0: slide puzzle ONNX model + quadratic mouse drag curve
- Arkose FunCaptcha: multi-wave ONNX image classifier
- Akamai Bot Manager: `_abck` sensor harvester
- Google BotGuard: polymorphic VM utk OAuth `bgRequest`
- PerimeterX: hashcash Web Worker PoW → `_px3` harvest
- reCAPTCHA/hCaptcha v3 Enterprise + invisible
- (sumber: skills/automation/captcha-solver/SKILL.md)

## 🥇 THREADS / SOCIAL STEALTH (anti-detection)
- **Playwright headless = TERDETEKSI** (TLS/JA3, WebGL/canvas hash, chromium build 
  flags leak) → pakai **Camoufox + manual SSO login sekali** = visible; cookie 
  injection = dead end (butuh real SSO exchange)
- **Log-normal delay** (bukan uniform) + cooldown window + 3% mid-word micro-pause
- Submit button Threads = `svg[aria-label="Balas"]` (BUKAN <button>)
- Link = clipboard paste (`navigator.clipboard.writeText()` + Meta+v), bukan 
  keyboard.type() — Threads cuma URL-detect clipboard
- Max 3 posts/thread; shadowban threshold 2 consecutive fail → auto-pause cron
- Meta API: `POST configure_text_only_post/` + X-IG-App-ID 238260118697367

## 🥇 TELEGRAM BOT PRODUCTION (sk4)
- message_id dedupe (cegah double-reply saat polling overlap/restart)
- safeSend retry dgn 429 `retry_after`
- polling_error handler exit on 409 (instance lain — jangan loop)
- Webhook Nginx/FastAPI + HMAC signature verify on raw bytes (sebelum parse)
- Multi-bot single-process: tiap token = own poll; 2 instance token sama = 409

## 🥇 BATCH / PARALLEL OPS (sk12)
- Resolusi: N>5 independent ops, idempotent, >30s sequential → parallelize
- JS: p-limit + Promise.allSettled (satu fail tak bunuh batch)
- Python: asyncio.gather + Semaphore
- **Resume-from-failure checkpoint** (save state tiap N items — kritis utk batch panjang)
- TokenBucket rate limiter (Telegram 30/s global, 1/s per chat)

## 🥇 CLIENT REVENUE / SCRAPING (sk30)
- **"Browser = LAST RESORT" doctrine**: official API → replicate XHR dari DevTools 
  Copy as cURL (`parse_curl()`) → headless sekali utk token → browser hanya utk 
  JS-render-tanpa-API
- BulkRunner: concurrency + retry/backoff + checkpoint-resume + dedupe
- paginate_offset/cursor + extract() JSON-path

## 🥇 FRAMEWORK (dari subagent-summary-1)
- attack-chaining-core: postcondition→precondition composition, capability graph,
  scoring 8-dimensi CRAILEIS+M, counter-evidence search, minimal-chain discipline
- attack-surface-mapper: evidence-backed mapping + trust boundaries
- webhunter-os: 8-phase bug bounty (recon→exploit→report) + decision-engine
- audit-core: Z3/Halmos/Echidna/Slither masters (detail di extraction 51KB)
- drills: latihan bertingkat DeFi security (tools/security/drills)

## CATATAN
- Teknik di atas = SALINAN/ekstrak — implementasi penuh ada di file BOZAGENTIC asli
  (Downloads/BOZAGENTIC/bozagentic/) yang READ-ONLY
- Crypto/web3 (sybil audit, on-chain monitor, MEV, governor) = DIHAPUS sesuai user
- Semua teknik = reusable + verified oleh BOZAGENTIC production (bukan klaim)