# SKILLS-INDEX.md — Skill Non-Crypto Di-Merge dari SYADAGENTIC ke SyadAgentic
# Sumber: kurasi subagent (48 canonical skills unik, ~90% file = duplikat)
# Di-salin ke arsenal-skills/ (hanya non-crypto — crypto dihapus sesuai user)

## AUTOMATION (arsenal-skills/automation/)
- sk4.md — Telegram bot produksi: message_id dedupe, 429 retry_after, 
  polling_error exit on 409, webhook Nginx/FastAPI
- sk6.md — paginate+TokenBucket rate limiter, extract() JSON-path
- sk12.md — (auto: scraping/parse lanjutan)
- sk17.md — (auto: batch/parallel)
- captcha-solver/ — solve captcha (reCAPTCHA/slider) utk automation

## CTF / RED-TEAM (arsenal-skills/ctf/)
- sk43.md — CTF web exploitation
- sk44.md — CTF binary pwn
- sk45.md — CTF crypto
- sk46.md — CTF forensics + reverse
- sk47.md — CTF swarm full-auto
- sk48.md — LLM prompt-injection/red-team: DUA guard surface (input guard 
  blocklist/classifier vs output guard literal-match secret/LLM reviewer)

## SECURITY (arsenal-skills/security/)
- sk11.md — bug bounty / security audit
- sk21.md — enterprise & defensif (auth.log, KQL, HIDS auto-firewall)
- sk51.md — offensive security & red-team ops (HARD-RAIL: authorized targets only)
- web-exploit-test/ — web exploit testing toolkit

## STATUS
- Teknik dari skill ini = SUDAH di-merge ke arsenal (bukan dijalankan langsung
  tanpa review)
- Skill crypto/web3/on-chain (swap/NFT/MEV/treasury) = DIHAPUS sesuai perintah user
- Sisanya (audit-core, webhunter-os, attack-chains) = framework terpisah,
  bisa di-merge manual jika diperlukan