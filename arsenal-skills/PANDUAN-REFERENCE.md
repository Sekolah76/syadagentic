# Panduan Operator — Hermes + SYADAGENTIC v7.0 SYADAGENTIC SUPREME

Cara ngomong sama Hermes setelah v7.0 OPENCLAW EDITION + hermes-crypto-agent ke-combo.
*Update v7.0 (2026-06-09): Airdrop Intelligence (sk31), CTF/Whitehat (sk32), + observability & safety tooling.*

---

## Daftar Isi

**Operasi crypto (Hermes runtime)**

1\. [Mode default vs mode cepat](#mode-default-vs-mode-cepat)  
2\. [Mint NFT](#mint-nft)  
3\. [Swap token](#swap-token)  
4\. [Bridge cross-chain](#bridge-cross-chain)  
5\. [Sniping token launch](#sniping-token-launch)  
6\. [Airdrop farming multi-wallet](#airdrop-farming-multi-wallet)  
7\. [Mempool watch (anti-drainer)](#mempool-watch-anti-drainer)  
8\. [Beli NFT di marketplace](#beli-nft-di-marketplace)  
9\. [Whale & smart-money tracker](#whale--smart-money-tracker)

**Airdrop Intelligence & Whitehat — BARU di v7.0**

10\. [Airdrop Intelligence (sk31)](#airdrop-intelligence-sk31--baru-v42)  
11\. [CTF / Whitehat toolkit (sk32)](#ctf--whitehat-toolkit-sk32--baru-v42)  
12\. [CTF Swarm full-auto (sk32 → sk43–sk48)](#ctf-swarm-full-auto-sk32--m43m48--update-v42)  
13\. [Rug & legitimacy check](#rug--legitimacy-check--baru-v42)  
14\. [Observability & safety baru](#observability--safety-baru--v42)

**Growth & Protection — sk33–sk42 (update v7.0, 12 Jun)**

15\. [Alpha & farming intelligence (sk33 · sk34 · sk36)](#alpha--farming-intelligence-sk33--sk34--sk36--update-v42)  
16\. [Proteksi komunitas (sk37 · sk38)](#proteksi-komunitas-sk37--sk38--update-v42)  
17\. [Mesin konten & komunitas (sk35 · sk39–sk42)](#mesin-konten--komunitas-sk35--m39m42--update-v42)

**Sesi & ops**

18\. [Session control commands](#session-control-commands)  
19\. [Background job persistence](#background-job-persistence)

**Skill non-crypto & referensi**

20\. [Skill non-crypto (v7.0) — contoh ngomong](#skill-non-crypto-v41--contoh-ngomong)  
21\. [Cheat sheet — natural language ke skill route](#cheat-sheet--natural-language-ke-skill-route)  
22\. [Yang perlu Kakak siapin sebelum mulai](#yang-perlu-kakak-siapin-sebelum-mulai)  
23\. [Cara cepat verify](#cara-cepat-verify-v42--hermes-udah-jalan)

---

## Mode default vs mode cepat

Hermes punya 2 mode operasi. Default = aman, mode cepat = fire and forget.

### Default — confirm before signing
Tiap tx penting dapat plan ringkas + gate `(y/n)`. Cocok buat:
- Tx pertama di sesi baru
- Wallet utama / dana besar
- Operasi yang belum pernah Kakak lakuin sebelumnya
- Kontrak yang belum diaudit

### Mode cepat — `auto_confirm on`
Skip prompt per tx. Tx pertama tetap dapat 1-line summary (info only, bukan gate). Cocok buat:
- Batch ops (mass mint, multi-wallet farming)
- Wallet kecil / test wallet
- Operasi rutin yang udah biasa
- Sniping di mana speed penting

```
Kakak: auto_confirm on
Hermes: [AUTO_CONFIRM] ON. tx akan fire tanpa gate sampai sesi ini berakhir atau lo set off.

Kakak: auto_confirm off
Hermes: [AUTO_CONFIRM] OFF. balik ke mode safe.
```

Operational rails yang TETAP nyala walau auto_confirm on:
- Secret hygiene (gak pernah log priv key)
- Simulate before broadcast
- Drainer/scam code detection
- User-funds-only

---

## Mint NFT

### Single mint dari URL
```
Kakak: mint NFT https://opensea.io/assets/base/0xABC.../1
```

Hermes auto:
- Parse URL → chain `base`, contract `0xABC...`
- Probe mint function (publicMint, mint, claim, dst)
- Detect price via `mintPrice()` / Seadrop config
- Auto-gas (estimate + buffer)
- Simulate → send → wait → report

Output:
```
[TARGET] 0xABC... on base × 1
[FN]     mintPublic(uint256) — detected
[PRICE]  0.0014 ETH
[GAS]    180k @ 0.05 gwei  →  ~$0.02
[SENT]   0xtxhash...
[OK]     block 12345678  gasUsed 142,330
[VIEW]   https://basescan.org/tx/0xtxhash...
```

### Mass mint pakai N wallet
```
Kakak: auto_confirm on. mint https://opensea.io/assets/base/0xABC.../1 pakai 50 wallet
```

Output:
```
[BATCH MINT] 50 wallets × NFT 0xABC... on base
est total cost: 0.0070 ETH (50 × 0.0001 mint fee)
concurrency: 5
[SENDING]

[3/50]   0xAbC...d4F1   ✅ 0xtx1...
[7/50]   0xDeF...c2A3   ✅ 0xtx2...
[12/50]  0x123...8F9    ❌ AlreadyMinted
...
[DONE]   47/50 ok, 3 failed → mint-1748150400.json
```

### Mint Manifold / Zora
Sama, paste URL langsung:
```
Kakak: mint https://app.manifold.xyz/c/12345
Kakak: mint https://zora.co/collect/base:0xABC.../1
```

Hermes pakai protocol-specific handler (Manifold instanceId fetch, Zora 1155 protocol fee).

---

## Swap token

### Swap simple
```
Kakak: swap 0.5 ETH ke USDC di base, pakai wallet pertama
```

Plan:
```
[PLAN]
chain:    base
wallet:   0xAbC...d4F1 (wallet#1)
action:   swap 0.5 ETH → USDC (via 1inch)
slippage: 1%
est out:  ~1,847 USDC
gas:      ~$0.02

Lanjut? (y/n)
```

`y` → fire. Tx hash + explorer link.

### Sell semua holding token
```
Kakak: sell semua $PEPE di wallet#1, ke USDC
```

Hermes:
- Cek balance PEPE di wallet
- Quote via 1inch
- Tampilkan plan
- Execute (kalau approve belum ada, approve dulu otomatis)

### Swap via DEX aggregator pilihan
```
Kakak: swap 1000 USDC ke ETH di arbitrum via jupiter
```
(Jupiter buat Solana. Untuk EVM, default 1inch — Hermes auto-koreksi.)

---

## Bridge cross-chain

### Bridge simple
```
Kakak: bridge 500 USDC dari arbitrum ke base pakai stargate
```

Plan:
```
[BRIDGE PLAN]
from:    arbitrum  → 500 USDC
to:      base      → 499.32 USDC (after fees)
route:   Stargate V2
fee:     0.68 USDC
eta:     ~2 menit
gas:     ~$0.30
bonus:   eligible LayerZero points

Lanjut? (y/n)
```

`y` → execute → wait sampai landed di destination chain → confirm.

### Bridge dengan route otomatis (LI.FI)
```
Kakak: bridge 0.1 ETH dari eth ke base, route paling murah
```

Hermes pakai LI.FI aggregator, pilih route optimal otomatis (Across / Stargate / native / Hop — mana yang termurah).

### Bridge ke non-EVM (Solana via Mayan)
```
Kakak: bridge 100 USDC dari base ke solana
```

Hermes pakai Wormhole + Mayan untuk EVM ↔ Solana. Wallet Solana harus udah ke-import di vault.

---

## Sniping token launch

### Setup sniper
```
Kakak: snipe token baru di base, budget 0.05 ETH per launch, max 3 launch hari ini
```

Output:
```
[SNIPER ACTIVE] base / Uniswap V3 PairCreated
filter:   WETH pair only
budget:   0.05 ETH / launch
max:      3 launches today
safety:   honeypot.is + GoPlus required
wallet:   0xAbC...d4F1
[LISTENING...]

pm2: sniper-base (id 2)
log: pm2 logs sniper-base
```

Saat pair baru terdeteksi:
```
[DETECTED] 0xNew...Token, paired with WETH at block 12345678
[SAFETY]   honeypot.is: clean | GoPlus: 1 warning (mintable)
⚠️ mintable token (owner bisa inflate supply). Lanjut snipe? (y/n)
```

`auto_confirm on` → auto-block kalau CRITICAL flag, auto-proceed kalau cuma WARN.
`auto_confirm off` → tanya per detection.

### Snipe NFT mint launch
```
Kakak: snipe mint NFT collection https://opensea.io/collection/<slug>, watch dari sekarang sampai mint open
```

Hermes pantau status drop (read `getPublicDrop()` Seadrop config), fire mint detik mint window buka.

### Stop sniper
```
Kakak: stop sniper-base
```

---

## Airdrop farming multi-wallet

### LayerZero farming
```
Kakak: layerzero farming, 50 wallet, bridge variasi route 5 chain selama 7 hari
```

Sybil reminder (sekali per session):
```
⚠️ LayerZero punya deteksi sybil bisa blacklist semua wallet terkait.
Gua randomize timing (5-180 menit) + amount jitter (±15%) + variasi bridge per wallet.
Tetap ada risk. Lanjut? (y/n)
```

`y`:
```
[FARMING PLAN]
wallets:   50
chains:    eth, arb, base, op, polygon (5 chains)
tx/wallet: 14-21 (random)
duration:  7 days
total tx:  ~875 (estimasi)
est cost:  ~$45 total gas

[STARTED] background runner: pm2 lz-farming
[CHECK]   pm2 logs lz-farming
[STOP]    "stop lz-farming"
```

### zkSync / Linea farming pattern sama
```
Kakak: zksync farming, 30 wallet, daily activity selama 14 hari
Kakak: linea voyage tasks pakai 25 wallet
```

### Daily check-in airdrop
```
Kakak: daily check-in airdrop X pakai semua wallet, jam 8 pagi WIB
```

Hermes setup cron job, jalan otomatis tiap hari.

---

## Mempool watch (anti-drainer)

### Setup watcher
```
Kakak: pantau wallet gua 0xAbC...d4F1 dari approve mencurigakan, alert ke TG
```

Output:
```
[WATCHER ACTIVE]
target:   0xAbC...d4F1
chains:   ethereum, base, arbitrum
triggers: approve(), setApprovalForAll(), permit()
alert:    @your_alerts_channel channel
filter:   spender harus contract verified, kalau gak → CRITICAL

running as pm2: anti-drainer (id 3)
```

Saat detect approval mencurigakan di mempool (sebelum confirmed):
```
🚨 CRITICAL APPROVAL DETECTED 🚨
wallet:   0xAbC...d4F1
action:   setApprovalForAll(0xSpender..., true)
spender:  0xSus...Address (no verified contract)
tx:       0xpending...

STATUS: pending in mempool (~12s before confirm)
ACTION: kalau ini bukan elo, kirim front-run tx revoke SEKARANG
        "revoke approval 0xSus... di wallet#1"
```

### Auto-revoke mode
```
Kakak: anti-drainer auto-revoke mode on untuk wallet#1
```

Kalau Hermes detect approval ke contract non-whitelist → otomatis broadcast revoke tx dengan gas lebih tinggi, race-condition dengan drainer.

---

## Beli NFT di marketplace

### OpenSea specific listing
```
Kakak: beli BAYC #1234 di opensea, max 25 ETH
```

Plan:
```
[LISTING FOUND]
collection: BAYC
token id:   #1234
price:      22.5 ETH (di bawah max)
seller:     0xSeller...
protocol:   Seaport 1.6
gas:        ~$8

Lanjut? (y/n)
```

### Floor sweep
```
Kakak: sweep floor Pudgy Penguins, 5 unit, max avg 10 ETH per piece
```

Hermes pakai Reservoir aggregator (cek listing terendah cross-marketplace: OpenSea, Blur, LooksRare). Bulk fulfill dalam 1 tx kalau bisa.

### List NFT buat dijual
```
Kakak: list NFT #5678 dari koleksi 0xMy... di opensea, harga 1.5 ETH, expire 7 hari
```

Hermes sign EIP-712 Seaport order → post ke OpenSea API. Listing live di marketplace.

### Magic Eden / Tensor (Solana)
```
Kakak: beli SMB #1234 di magic eden, max 50 SOL
```

Sama flow-nya, beda protocol (Magic Eden ME instruction, bukan Seaport).

---

## Whale & smart-money tracker

### Track wallet whale + alert TG
```
Kakak: tracker smart money via nansen, alert ke TG kalau ada buy > $50k
```

Output:
```
[TRACKER ACTIVE]
source:   Nansen Smart Money label
filter:   buy size > $50k
chains:   ethereum, base, arbitrum, solana
alert:    @your_alerts_channel

pm2: smart-money-watch (id 4)
```

Alert format:
```
🐋 SMART MONEY BUY
wallet:   0xWhale... (Nansen: "Smart Trader")
action:   bought 12.5 ETH worth of $TOKEN
chain:    base
contract: 0xToken...
tx:       https://basescan.org/tx/...
```

### Copy-trade pattern
```
Kakak: copy-trade wallet 0xWhale..., ukuran 5% dari ukuran mereka, max $500 per trade
```

Hermes monitor whale wallet → mirror buy ukuran kecil di wallet Kakak, filter stablecoin transfer dan low-value noise.

### NFT whale alert
```
Kakak: alert kalau ada whale beli NFT > 10 ETH di koleksi blue chip
```

Hermes pakai Reservoir WebSocket stream — push notif real-time.

### Floor drop alert
```
Kakak: alert kalau floor BAYC drop > 5% dalam 1 jam
```

---

## Airdrop Intelligence (sk31) — BARU v7.0

Skill khusus AirdropFinder: ubah siklus airdrop jadi keputusan ber-angka. Semua tool **offline & deterministik** — data on-chain diambil dulu lewat sk10/hermes, sk31 yang nge-judge & nyusun rencana. Fund movement (claim/exit) tetap lewat Spend Governor.

### 1. Eligibility scorer — wallet ini layak gak?
```
Kakak: skor eligibility wallet 0xAbC...d4F1 buat airdrop Linea
```

Output:
```
[ELIGIBILITY] 0xAbC...d4F1 — Linea
score:   72/100  (TIER: likely)
✅ kuat:   age 210d, 47 tx, bridged 3x, 4 unique contracts
⚠️ gap:    volume $1.2k (target >$5k), belum interaksi DeFi native
🚩 flag:   gas spend rendah (bot-like? cek manual)
saran:    + 2-3 swap di native DEX, + 1 LP position → proyeksi ~85/100
```

Rubric bisa di-override per-project (kalau Kakak tau kriteria spesifik proyeknya):
```
Kakak: skor wallet#1 buat ZkSync, bobot: volume 40%, age 20%, kontrak unik 40%
```

### 2. Sybil self-audit — wallet farm gua aman gak?
Ini **jaring keselamatan buat wallet Kakak sendiri** — cek apakah pola antar-wallet gampang ke-cluster sama sybil filter, biar bisa di-de-correlate. Bukan buat ngecoh proyek.
```
Kakak: sybil audit 50 wallet farming gua
```

Output:
```
[SYBIL AUDIT] 50 wallets
risk: HIGH ⚠️
korelasi terdeteksi:
  • funding: 38 wallet didanai dari 1 sumber (0xFund...) — RED
  • timing: 22 wallet tx dalam window 5 menit yang sama — RED
  • gas pattern: amount identik di 41 wallet — YELLOW
  • contract overlap: semua wallet sentuh kontrak yang sama urut sama
saran de-correlation:
  1. Variasikan funding source (pakai CEX withdrawal beda-beda)
  2. Sebar timing (randomize 1-72 jam, jangan batch)
  3. Variasikan urutan & jenis interaksi per wallet
  4. Amount jitter ±15-30%
```

### 3. Claim-window calendar — jangan kelewat claim
`now` selalu di-inject (gak pernah nebak waktu). Alert fire-once di H-48 / H-2 / H-0.
```
Kakak: tambah ke kalender airdrop: ZK claim buka 17 Jun 14:00 WIB, tutup 24 Jun
Kakak: airdrop apa aja yang claim window-nya minggu ini?
```

Output:
```
[CLAIM CALENDAR] minggu ini (12-18 Jun)
🔔 ZK        — buka 17 Jun 14:00 WIB (H-5)   [alert set: H-48, H-2, H-0]
🔔 LayerZero — tutup 15 Jun 23:59 WIB (H-3)  ⚠️ belum claim di 12 wallet!
✅ Scroll    — udah di-claim semua wallet
```

### 4. Exit planner — kapan & gimana jual
```
Kakak: exit plan buat 5000 $ZK, profil balanced, likuiditas tipis
```

Output:
```
[EXIT LADDER] 5000 $ZK — profil: balanced
likuiditas DEX tipis → split sell biar gak slippage parah
  • TGE +0h:   sell 30% (1500) — amankan modal
  • +24h:      sell 25% (1250) — kalau harga > TGE
  • +7d:       sell 25% (1250) — atau cut kalau dump
  • hold 20%:  moonbag (1000)
⚠️ vesting: cek dulu, kalau ada cliff sebagian sell-nya geser
eksekusi via Spend Governor (gate per leg, atau auto_confirm on)
Lanjut setup auto-sell ladder? (y/n)
```

---

## CTF / Whitehat toolkit (sk32) — BARU v7.0

Buat Kakak yang ikut CTF & bug bounty buat reward. **Legal & in-scope only** — target asing kena gate R9 (⚠️ izin? y/n), default tahan. Tool inti stdlib-only & pasif (decode/analisis); exploit aktif tetap manual + izin.

### Triage soal — ini kategori apa, serang dari mana
```
Kakak: triage soal CTF: "diberikan RSA public key dengan e kecil, decrypt flag"
```
```
[TRIAGE] kategori: crypto (confidence tinggi)
arah:    RSA small-e → coba cube-root attack (e=3, no padding)
tooling: sk32 (math manual), atau sage kalau ada
```

### Decode berlapis otomatis
```
Kakak: decode ini: NHZ4dnRoaXNfaXNfYmFzZTY0X2ZsYWc=
```
```
[DECODE] kupas berlapis (diurut printability):
  base64 → "4vxvthis_is_base64_flag"
  ...cek flag pattern: NAME{...}
🚩 ketemu: flag{...}
```

### Classic crypto
```
Kakak: caesar bruteforce "Frperg Zrffntr"
Kakak: xor single byte cari key buat hex ini: 1c0111001f...
```
26 shift / 256 key sekaligus, di-rank by englishness.

### Hash & misc
```
Kakak: ini hash tipe apa: 5f4dcc3b5aa765d61d8327deb882cf99
```
```
[HASH-ID] panjang 32 hex → kandidat: MD5, NTLM, MD4
```

Recon kategori lain (web/pwn/forensics) → sk32 ngarahin ke tooling + delegasi ke sk11 (audit) / sk6 (httpx, in-scope). Mau auto-generate writeup PDF tiap flag ketemu? combo sk32 + sk8.

---

## CTF Swarm full-auto (sk32 → sk43–sk48) — update v7.0

Naik level dari toolkit pasif: **framework CTF full-auto whitehat** di `tools/ctf/`. sk32 jadi orchestrator yang triage → cek scope → dispatch ke sub-skill kategori → validasi flag → submit. Cocok buat event CTFd dengan banyak soal sekaligus.

### Sub-skill kategori (otomatis dipilih sk32)
| Soal | Skill |
|---|---|
| web app / URL / HTTP | **sk43** (SQLi, SSTI, SSRF, IDOR, JWT, deserialization) |
| binary + `nc host port` | **sk44** (ret2win, ret2libc, format string, heap, ROP) |
| binary "what does it do" | **sk45** (angr, Ghidra, radare2, keygen) |
| ciphertext / RSA / key | **sk46** (RSA attacks, block cipher, PRNG — `rsa_attacks.py`) |
| pcap / memory / image / zip | **sk47** (volatility, binwalk, stego, carving) |
| LLM / AI / jailbreak / Gandalf | **sk48** (prompt-injection / LLM red-team) |

### Mode 1 — manual per soal (aman, default)
```
Kakak: ini soal web, target https://chal.ctf.example/01, ada login form
```
sk32 konfirmasi scope (lihat `scope.json`) → load sk43 → kasih playbook + script recon. Flag yang ketemu **wajib** lewat `flag_validator.py`, lalu Kakak yang approve submit.

### Mode 2 — full-auto swarm (banyak soal, butuh setup)
```bash
cd tools/ctf
cp .env.example .env            # isi CTFD_URL, CTFD_TOKEN, API key per provider, MODELS (ID asli!)
cp scope.example.json scope.json # set host yang BOLEH diserang (event ini aja)
docker build -f sandbox/Dockerfile.sandbox -t ctf-sandbox .

python3 run.py          # poll CTFd → race model per soal di sandbox → solve
python3 run.py status   # lihat progress per soal
python3 run.py approve  # submit flag yang antri (kalau HITL_SUBMIT=true)
```
Tiap soal di-race beberapa model paralel di **Docker sandbox terisolasi** (default `--network none`). Lineup model bebas lintas-provider — adapter **Anthropic, OpenAI, Gemini** lengkap (`MODELS=anthropic:...,openai:...,gemini:...`, isi API key provider yang dipakai). Flag pertama yang valid menang; di mode tanpa pendamping, butuh `AUTO_SUBMIT_CONSENSUS` model setuju baru auto-submit.

### Mode 3 — LLM red-team / Gandalf (sk48)
Buat soal kategori AI/LLM (Gandalf-style: peras password dari LLM tanpa kena guard). Solver **host-locked ke gandalf.lakera.ai** (nolak host lain).
```bash
cd tools/ctf
python3 gandalf_solver.py --start 1 --end 7      # static: coba ladder strategi tiap level
python3 gandalf_solver.py --adaptive --model anthropic:claude-opus-4-1   # attacker-LLM (bisa juga openai:.../gemini:..., isi API key-nya)
```
Idenya: input guard periksa prompt *kamu* (lawan: parafrase intent), output guard periksa jawaban *model* (lawan: jangan emit secret literal → encode/acrostic/eja). Detail teknik & defense ladder L1–L8 ada di `skills/sk48.md`. ⚠️ API contract Gandalf gak resmi — verify dulu di DevTools sebelum jalan.

### Pengaman (kenapa ini tetap whitehat)
- **`scope_guard.py`** — cuma host di allowlist yang boleh disentuh; aturan deny menang. Out-of-scope = ditolak.
- **Sandbox** — binary soal cuma jalan di dalam Docker, default tanpa network.
- **`flag_validator.py`** — flag wajib full-match + lolos blocklist placeholder; flag diambil dari output target, **gak pernah dikarang**.
- **HITL default** — `HITL_SUBMIT=true` → flag nunggu approve Kakak. Sejalan sama gate R9 sk32.

Detail teknis: `tools/ctf/README.md`. Catatan review paket asli: `REVIEW.md`.

---

## Rug & legitimacy check — BARU v7.0

Satu command → verdict jelas. Sinyal mentah (honeypot/tax/verifikasi/holder/LP) diambil dari H4 + sk10, `rugcheck` yang nge-judge jadi keputusan + nampilin yang *belum* dicek (jangan diabaikan).
```
Kakak: rugcheck token 0xToken... di base
```
```
[RUGCHECK] 0xToken... on base  →  ⚠️ CAUTION
🛑 critical:  (none)
⚠️ warnings:  sell-tax 9%, owner belum renounce, LP lock cuma 30 hari
✅ ok:        kontrak verified, bukan honeypot, top10 holder 28%
❓ unknown:   age kontrak belum dicek → suruh sk10 isi dulu
verdict: boleh masuk kecil, jangan all-in. Re-check setelah LP lock & renounce.
```
Verdict: **SAFE / CAUTION / DANGER**. Cocok juga jadi bahan edukasi konten AirdropFinder ("cara baca rug signal").

---

## Observability & safety baru — v7.0

Mostly otomatis di belakang layar, tapi bisa Kakak panggil:

| Command | Effect |
|---|---|
| `cost report` | Ledger biaya terpusat: token LLM + gas on-chain (USD) + API call, breakdown per provider/chain |
| `router log` / `router tune` | Liat keputusan router + deteksi *tie* (keyword nabrak) + saran retune bobot |
| `dry-run on` / `off` | Simulasi global — engine `plan()` bukan broadcast (udah ada, sekarang pakai contextvars, lebih rapi) |
| `regression run <suite>` | Golden-set regression: bandingin output sekarang vs baseline → tau kalau ada yang rusak saat upgrade |

Plus yang jalan otomatis:
- **Secret tripwire** — di output layer, redaksi priv key / mnemonic / API key / JWT / PEM sebelum ke-print/log. CTF flag tetap boleh tampil, secret nyata yang gak relevan tetap di-redact.
- **Cost ledger** — tiap operasi nyatet biayanya, jadi `cost report` selalu akurat.

---

## Alpha & farming intelligence (sk33 · sk34 · sk36) — update v7.0

Tiga modul baru biar farming Kakak dari hulu ke hilir ber-angka: nemu proyek duluan → hitung ROI → tau kapan keluar. Semua offline & deterministik, data mentah diambil sk10/sk22/hermes dulu.

### Alpha radar (sk33) — nemu airdrop SEBELUM diumumkan
```
Kakak: scan proyek pre-TGE yang worth difarming di Base
```
```
[ALPHA RADAR] 3 kandidat
📡 ZkProtoX  78/100 (HOT)   · points program ✅ · testnet ✅ · VC tier-1 · effort high
📡 BaseThing 52/100 (WARM)  · governance aktif tanpa token · raise $12M
📡 OldChain   8/100 (COLD)  · token udah ada → peluang airdrop utama lewat
saran: mulai ZkProtoX minggu ini, BaseThing watch dulu
```
Token udah listing? Skor otomatis di-cap 30 — jangan buang gas.

### Farm ROI (sk34) — lanjut, trim, atau drop?
```
Kakak: hitung ROI semua posisi farming gua
```
```
[FARM ROI] 4 posisi · EV $3.2k − cost $410 = net $2.79k
💼 LayerZero  EV $1.2k · ROI 9.0x → KEEP
💼 ZkProtoX   EV $1.8k · ROI 6.2x → KEEP
💼 BridgeFarm EV $150  · ROI 0.4x → TRIM (gas udah kegedean)
💼 DeadFarm   net -$75 → DROP ⚠️ nganggur 60 hari — wallet pasif sering digugurin
```

### Unlock pressure (sk36) — supply makro sebelum kejebak dump
```
Kakak: kalender unlock $ZK 6 bulan ke depan, worth hold gak?
```
```
[UNLOCK CALENDAR] $ZK
🔓 Investor cliff  T-10h  · $160M (40% circ) · pressure EXTREME (32x volume)
   ⚠️ tekanan jual besar <2 minggu — pertimbangkan kurangi posisi DULUAN
🔓 Team linear     T-120h · $40M (10% circ) · pressure HIGH — tandai, siapin exit
```
`now` selalu di-inject (TIME.md). Eksekusi jual tetap lewat exit planner sk31 + Spend Governor.

---

## Proteksi komunitas (sk37 · sk38) — update v7.0

Dua modul defensif **read-only** — jaga member AirdropFinder dari drainer. Gak nyerang, gak nge-exploit; sejalan prinsip whitehat.

### Anti-scam sentinel (sk37) — situs ini asli atau imitasi?
```
Kakak: cek zkprot0x.xyz, resminya zkprotox.xyz
```
```
[SCAM SENTINEL] zkprot0x.xyz → 🚨 LIKELY-SCAM (100/100)
• typosquat: beda 1 huruf dari domain resmi
• 🚩 minta SEED PHRASE — situs resmi GAK PERNAH minta ini
• SSL umur 3 hari + tombol claim
draft warning post udah disiapin — review dulu sebelum broadcast (false positive = fitnah)
```

### Contract watcher (sk38) — aman claim gak?
Modus drainer paling sering: kontrak/claim address diganti diam-diam pas hype claim. Snapshot diambil H9/sk10, sk38 yang diff.
```
Kakak: kontrak claim ZkProtoX berubah gak dari kemarin? aman claim?
```
```
[CONTRACT WATCH] 0xAbc... → 🚨 CRITICAL
🚨 claim address berubah 0xC1... → 0xEVIL... — JANGAN claim sampai verifikasi resmi
🚨 fungsi sensitif baru: setClaimAddress
safe_to_claim: FALSE → semua claim job di-hold
```
`safe_to_claim = FALSE` → claim runner otomatis nahan. No exceptions.

---

## Mesin konten & komunitas (sk35 · sk39–sk42) — update v7.0

Pipeline konten AirdropFinder end-to-end: dengerin komunitas → bikin panduan → repurpose semua platform → video → hook terbaik.

### Auto guide studio (sk35) — 1 airdrop jadi panduan rapi
```
Kakak: bikinin panduan ZkProtoX lengkap + versi telegram & X, embed referral gua
```
```
[GUIDE STUDIO] ZkProtoX (Base)
✅ panduan full Markdown ID (header, persiapan, 6 langkah, disclaimer DYOR)
✅ varian Telegram + varian X (≤280)
✅ referral ke-embed di semua varian
🖼️ 4 screenshot job → delegasi ke browser skill
gate: sk37 scan domain dulu sebelum publish — jangan promosiin scam
```

### Community intelligence (sk39) — apa kata komunitas semalam
```
Kakak: analisis chat grup 24 jam terakhir
```
```
[COMMUNITY INTEL] 1.840 pesan (24h) · sentimen netral (+0.05)
 topik: zkprotox(214), claim(180), gas base(95)
❓ paling sering: "kapan claim ZkProtoX dibuka min?" (38x)
🚨 FUD: 12 pesan "gak cair / scam" → cek fakta (sk37/sk38) dulu, baru klarifikasi
💡 ide: thread FAQ claim ZkProtoX, edukasi gas Base
```

### Omni-repurpose (sk40) + video pipeline (sk41) + hook lab (sk42)
```
Kakak: artikel ini jadiin thread X, post TG, carousel IG, script tiktok & youtube
Kakak: bikinin paket video 45 detik soal 3 airdrop Base
Kakak: kasih 8 varian hook buat konten ini, ranking
```
```
[REPURPOSE] 5 format ✅ — thread 6 tweet (semua ≤280) · TG · 5 slide IG · tiktok 36s · YT 6 mnt
[VIDEO PIPELINE] 45s · hook 6.8s → 3 poin → CTA · storyboard 5 shot · voiceover ID · subtitle .srt
[HOOK LAB] top-3:
  [76] 3 Airdrop Base yang wajib kamu tau sekarang   (angka, urgency)
  [70] Rahasia airdrop Base yang bikin cuan         (curiosity, emosi)
  [64] Jangan farming Base sebelum nonton ini 👀      (emosi, urgency)
```
Render video = skill `remotion_video`; TTS = `voice.py`. Skor hook = prediksi heuristik, bukan jaminan viral — feed balik performa aktual biar makin akurat.

---

## Session control commands

Cukup ngomong langsung ke Hermes, gak perlu syntax khusus:

| Command | Effect |
|---|---|
| `auto_confirm on` | Mode cepat — skip per-tx gate |
| `auto_confirm off` | Mode safe (default) |
| `status` | Liat semua background job aktif |
| `stop <jobname>` | Matikan background job (sniper, farming, watcher) |
| `resume <jobname>` | Lanjut job yang ke-pause |
| `audit` | Trigger sk52 — system self-check |
| `debug` | Trigger sk54 — kalau ada error/bug |
| `upgrade brain` | Trigger sk52 deep review (analisa skill coverage, gap, redundancy) |
| `dry-run on` | Semua tx jadi simulate-only, gak broadcast (buat testing) |
| `dry-run off` | Kembali ke broadcast mode |
| `wallet list` | Liat semua wallet di vault |
| `balance <wallet>` | Liat balance multi-chain wallet |
| `revoke approval <spender> di <wallet>` | Revoke ERC-20/721 approval |
| `cost report` | **v7.0** — biaya terpusat: token + gas (USD) + API, per provider/chain |
| `router log` / `router tune` | **v7.0** — log keputusan router + deteksi tie + saran retune |
| `regression run <suite>` | **v7.0** — golden-set regression lintas rilis |
| `skor eligibility <wallet> buat <proyek>` | **v7.0 (sk31)** — skor 0-100 + gap + flags |
| `sybil audit <N wallet>` | **v7.0 (sk31)** — cek korelasi antar-wallet sendiri |
| `kalender airdrop` / `claim window minggu ini` | **v7.0 (sk31)** — alert H-48/H-2/H-0 |
| `exit plan <amount> <token>` | **v7.0 (sk31)** — exit ladder, via governor |
| `rugcheck <token> di <chain>` | **v7.0** — verdict SAFE/CAUTION/DANGER |
| `triage soal CTF ...` / `decode ...` | **v7.0 (sk32)** — whitehat, in-scope only |
| `scan proyek pre-TGE di <chain>` | **v7.0 (sk33)** — alpha radar, skor + tier |
| `hitung ROI posisi farming` | **v7.0 (sk34)** — EV/ROI, keep/trim/drop |
| `bikinin panduan <proyek>` | **v7.0 (sk35)** — guide ID + varian TG/X + referral |
| `kalender unlock <token>` | **v7.0 (sk36)** — tekanan jual per event |
| `cek domain <situs> resminya <situs>` | **v7.0 (sk37)** — typosquat + drainer signals |
| `kontrak <proyek> berubah gak? aman claim?` | **v7.0 (sk38)** — diff + safe_to_claim gate |
| `analisis chat grup <window>` | **v7.0 (sk39)** — topik, FUD, sentimen, ide |
| `repurpose konten ini ke semua platform` | **v7.0 (sk40)** — X/TG/IG/TikTok/YT |
| `bikinin paket video <durasi> soal <topik>` | **v7.0 (sk41)** — script+storyboard+SRT |
| `kasih varian hook + ranking` | **v7.0 (sk42)** — skor stop-scroll 0-100 |

### Per-wallet alias
```
Kakak: rename wallet 0xAbC...d4F1 jadi "farming-base-1"
Kakak: swap 100 USDC pakai farming-base-1
```

Hermes pakai alias mulai sesi berikutnya.

---

## Background job persistence

Sniper, farming, watcher — semua jalan background via pm2. Survive reboot kalau pakai systemd.

### Liat job aktif
```bash
pm2 ls
```

Sample output:
```
┌─────┬────────────────────┬─────────────┬──────┬─────────┐
│ id  │ name               │ status      │ cpu  │ memory  │
├─────┼────────────────────┼─────────────┼──────┼─────────┤
│ 0   │ hermes (main)      │ online      │ 2%   │ 142 MB  │
│ 1   │ lz-farming         │ online      │ 0.5% │ 48 MB   │
│ 2   │ sniper-base        │ online      │ 1%   │ 36 MB   │
│ 3   │ anti-drainer       │ online      │ 0.3% │ 22 MB   │
│ 4   │ smart-money-watch  │ online      │ 0.4% │ 28 MB   │
└─────┴────────────────────┴─────────────┴──────┴─────────┘
```

### Log per job
```bash
pm2 logs sniper-base --lines 50
pm2 logs lz-farming -f          # follow real-time
```

### Restart / stop
```bash
pm2 restart sniper-base
pm2 stop lz-farming
pm2 delete anti-drainer         # hapus dari list
```

### Auto-start saat VPS reboot
```bash
pm2 save                        # save current state
pm2 startup systemd             # generate systemd unit
# follow instruksi yang muncul
```

---

## Cheat sheet — natural language ke skill route

Tabel cepat: Kakak ngomong apa → skill apa yang fire.

| Kakak ngomong | Route | File yang load |
|---|---|---|
| "mint NFT [URL]" | sk13 | `skills/sk13.md` |
| "mass mint pakai N wallet" | sk13 + sk12 + sk10 | mint + batch + Web3 |
| "swap X ke Y di [chain]" | H1 | `hermes/references/swap.md` |
| "jual semua $TOKEN" | H1 | swap.md |
| "bridge dari A ke B" | H2 | `hermes/references/bridge.md` |
| "stake ETH di lido" | H3 | `hermes/references/defi.md` |
| "supply USDC ke aave" | H3 | defi.md |
| "open long ETH di GMX" | H3 | defi.md (perp section) |
| "snipe token baru di [chain]" | H4 + sk10 | sniping.md + Web3 |
| "snipe mint NFT [URL]" | H4 + sk13 | sniping + minter |
| "pantau wallet [addr]" | H5 | `hermes/references/monitoring.md` |
| "alert kalau whale beli > $X" | H5 + sk4 | monitoring + TG bot |
| "mempool watch [wallet]" | H5 | monitoring (sniffer section) |
| "tracker smart money" | H5 | monitoring (Nansen/Arkham) |
| "beli NFT [token] di [marketplace]" | H6 | `hermes/references/nft.md` |
| "list NFT gua dijual" | H6 | nft.md |
| "floor sweep [collection]" | H6 | nft.md (Reservoir) |
| "sign in dApp pakai SIWE" | H7 | `hermes/references/web3_connect.md` |
| "resolve ENS [name].eth" | H7 | web3_connect.md |
| "layerzero farming N wallet" | H2 + H1 + sk12 | bridge + swap + batch |
| "zksync / linea farming" | H2 + H1 + sk12 | sama pattern |
| "buat wallet baru di [chain]" | sk10 / hermes/wallets.md | tergantung chain |
| "import wallet dari seed" | hermes/wallets.md | (security strict mode) |
| "audit kontrak [addr]" | sk11 | `skills/sk11.md` |
| "kenapa bot gua duplikat" | sk54 + sk4 | debug + telegram |
| "deploy ke VPS" | sk2 | `skills/sk2.md` |
| "buat landing page web3" | sk9 + sk10 | frontend + Web3 connect |
| "bikin animasi penjelasan / diagram" | sk18 | `skills/sk18.md` (Manim/Excalidraw) |
| "bikin gambar pakai comfyui" | sk18 | sk18 + `scene_prep.py` |
| "kontrol Notes/Safari di Mac gua" | sk19 | sk19 + `desktop_control.py` (no cursor steal) |
| "latih robot di Isaac Sim" | sk19 | sk19 + `scene_prep.py` |
| "bikin tulisan gua gak kaya AI" | sk20 | sk20 + `humanizer.py` |
| "blokir IP yang nyerang dari log" | sk21 | sk21 + `hids.py` |
| "investigasi error pakai KQL" | sk21 + sk57 | sk21 + systematic debug |
| "riset mendalam soal X + sumber" | sk22 | sk22 + `research_q.py` |
| "pecahin task ini, gua overwhelmed" | sk23 | `skills/sk23.md` |
| "bikin MCP server" | sk24 | sk24 + `mcp_builder.py` |
| "cek prompt gua ada masalah gak" | sk24 | sk24 (`audit_prompt`) |
| "review compliance / CI-CD / port kode" | sk25 | `skills/sk25.md` |
| "ubah obrolan ini jadi PRD / issues" | sk26 | sk26 + `prd.py` |
| "grill ide gua biar konkret" | sk26 + sk58 | shaping → spec |
| "eval / variance test fitur ini" | sk56 | sk56 + `eval.py` |
| "debug bug aneh yang kadang muncul" | sk57 | `skills/sk57.md` (4-fase + variance) |
| "tujuan gua masih kabur, bantu rapihin" | sk58 | `skills/sk58.md` |
| "bikin content calendar 30 hari" | sk27 | sk27 + `content.py` |
| "adaptasi post ini ke X/LinkedIn/IG/TikTok" | sk27 | sk27 (`adapt`) |
| "bikin thread / carousel / script reels" | sk27 | sk27 + `content.py` |
| "bikin caption + hashtag IG" | sk27 | sk27 (`caption`/`hashtags`) |
| "tulis pakai framework AIDA/PAS" | sk28 | `skills/sk28.md` |
| "tulis blog SEO-friendly" | sk28 | sk28 (SEO writer) |
| "lokalisasi konten ke bahasa lain" | sk28 | sk28 (localization/RTL) |
| "riset tren & kompetitor di niche gua" | sk29 | sk29 (+ sk22 buat dalam) |
| "analisis komentar / performa post" | sk29 | sk29 + `content.py` (butuh data real) |
| "1 artikel jadi thread+carousel+reels" | sk29 | sk29 (`repurpose`) |
| "full pipeline konten otomatis" | sk29 + sk4/sk17 | research→draft→visual→schedule→analyze |
| "riset ilmiah genomics/forecasting" | sk22 | dispatch ke library (scanpy/prophet/dll) |
| "robot lihat & ambil objek (VLA)" | sk19 | sk19 (VLA, sim dulu) |
| "skor eligibility wallet buat [proyek]" | sk31 | `skills/sk31.md` + `eligibility.py` |
| "sybil audit N wallet farming gua" | sk31 | sk31 + `sybil_audit.py` |
| "kalender / claim window airdrop" | sk31 | sk31 + `claim_watcher.py` |
| "exit plan / kapan jual [token]" | sk31 | sk31 + `exit_planner.py` |
| "rugcheck / token ini aman gak" | sk11 + H4 + sk10 | `rugcheck.py` (verdict) |
| "triage soal CTF / decode flag" | sk32 | `skills/sk32.md` + `ctf.py` |
| "caesar / xor / hash tipe apa" | sk32 | sk32 + `ctf.py` |
| "solve CTF web (SQLi/SSTI/JWT)" | sk32 → sk43 | `skills/sk43.md` + `tools/ctf/` |
| "pwn binary / ret2libc / heap" | sk32 → sk44 | `skills/sk44.md` + pwntools template |
| "reverse binary / angr / keygen" | sk32 → sk45 | `skills/sk45.md` + angr template |
| "RSA attack / crypto challenge" | sk32 → sk46 | `skills/sk46.md` + `tools/ctf/rsa_attacks.py` |
| "forensics / stego / pcap / memdump" | sk32 → sk47 | `skills/sk47.md` + sandbox tools |
| "prompt injection / jailbreak / Gandalf" | sk32 → sk48 | `skills/sk48.md` + `tools/ctf/gandalf_solver.py` |
| "full-auto solve CTFd (swarm)" | sk32 | `tools/ctf/run.py` (coordinator + sandbox) |
| "scan proyek pre-TGE / alpha airdrop" | sk33 | `skills/sk33.md` + `alpha_radar.py` |
| "ROI farming / farm mana di-drop" | sk34 | sk34 + `farm_roi.py` |
| "bikin panduan airdrop [proyek]" | sk35 | sk35 + `guide_studio.py` (+browser buat SS) |
| "kalender unlock / tekanan jual [token]" | sk36 | sk36 + `unlock_engine.py` |
| "situs ini palsu gak / cek domain" | sk37 | sk37 + `scam_sentinel.py` |
| "kontrak berubah gak / aman claim?" | sk38 | sk38 + `contract_watch.py` (+H9 snapshot) |
| "apa yang lagi rame di grup / FUD" | sk39 | sk39 + `community_intel.py` (+sk4 tarik pesan) |
| "repurpose ke X/TG/IG/TikTok/YT" | sk40 | sk40 + `repurpose.py` |
| "bikin paket video / storyboard / srt" | sk41 | sk41 + `video_pipeline.py` |
| "varian hook / prediksi judul" | sk42 | sk42 + `hook_lab.py` |
| "biaya / cost report sesi ini" | core | `cost_ledger.py` |
| "router nabrak / tune keyword" | core | `router_log.py` |
| "regression test antar rilis" | sk56 | `eval.py` (RegressionSuite) |

---

## Skill v7.0 — contoh ngomong (Airdrop Intelligence & Whitehat)

Net-new di v7.0. Semua tool offline+deterministik; data on-chain didelegasi ke sk10/hermes; fund movement lewat Spend Governor.

### Airdrop Intelligence (sk31)
```
Kakak: skor eligibility wallet#1 buat Linea, kasih gap & saran
Kakak: sybil audit 50 wallet farming gua, mana yang bahaya
Kakak: claim window airdrop apa aja minggu ini, alert H-48/H-2/H-0
Kakak: exit plan 5000 $ZK profil balanced, likuiditas tipis
```

### CTF / Whitehat (sk32) — legal & in-scope only
```
Kakak: triage soal CTF ini: [deskripsi]
Kakak: decode berlapis: [blob base64/hex]
Kakak: caesar bruteforce "[ciphertext]"
Kakak: ini hash tipe apa: [hash]
```
Target asing / out-of-scope → gate R9 dulu (⚠️ izin? y/n). Exploit aktif = manual + izin.

### Safety & observability
```
Kakak: cost report sesi ini       → token + gas + API breakdown
Kakak: rugcheck 0xToken... di base → verdict SAFE/CAUTION/DANGER
Kakak: regression run mint-detector → cek ada yang rusak gak abis upgrade
```

---

## Skill non-crypto (v7.0) — contoh ngomong

Semua di bawah ini **modul opsional**. Identitas inti tetap crypto+dev — skill ini cuma nyala kalau Kakak nyebut. Gak nyentuh dana, jadi gak ada gate governor (kecuali aksi OS/desktop/robot fisik & firewall → satu kali gate R9).

### Media & kreatif (sk18)
```
Kakak: bikinin animasi Manim buat jelasin gradient descent
Kakak: generate 10 variasi gambar pakai comfyui, seed beda-beda
Kakak: bikin diagram arsitektur sistem gua di excalidraw
Kakak: bikin OG card 1200x630 buat artikel ini
```
Output = file artefak (MP4/PNG/SVG). Butuh engine lokal (ffmpeg/Manim/ComfyUI) — deploy via sk2 kalau di VPS.

### Desktop & robotik (sk19)
```
Kakak: catat ini ke Notes gua          → app-drive, kursor Kakak GAK kerebut
Kakak: latih grasp robot di Isaac Sim, 200 step headless
```
macOS control = background-first (no cursor steal). Robot fisik / aksi destruktif desktop → gate R9 sekali.

### Humanizer (sk20)
```
Kakak: tulisan ini kaku banget, bikin natural   → buang AI-tell
Kakak: tune ke brand voice "ct_degen"
```

### Enterprise & defensif (sk21)
```
Kakak: pantau auth.log, auto-block IP brute-force SSH (dry-run dulu)
Kakak: tulis KQL buat cari spike latency 6 jam terakhir
```
HIDS selalu allowlist IP Kakak + TTL block (gak permaban). Aktivasi firewall → gate R9.

### Riset, fokus, produk (sk22/sk23/sk26)
```
Kakak: riset mendalam dampak EIP-4844 ke L2, kasih sumber
Kakak: gua overwhelmed, pecahin task ini satu-satu, kasih yang pertama doang
Kakak: dari obrolan tadi, bikinin PRD + breakdown jadi issues
```

### Meta-dev & quality (sk24/sk25/sk56/sk57/sk58)
```
Kakak: scaffold MCP server "weather" di Python
Kakak: audit prompt system ini, ada masalah apa
Kakak: variance test fungsi mint-detector 10x, stabil gak
Kakak: bug ini kadang muncul kadang enggak — debug sistematis
Kakak: tujuan "cuan dari web3" masih kabur, bantu shaping
```

### Konten & social media (sk27/sk28/sk29)
Suite marketing lengkap. Identitas inti tetap crypto+dev — ini modul opsional buat bikin & nyebarin konten.
```
Kakak: bikin content strategy: pillar, audience, positioning buat akun gua
Kakak: bikinin content calendar 30 hari, 5 post/minggu, X + IG
Kakak: pesan ini adaptasi ke X thread, LinkedIn, IG carousel, sama reels script
Kakak: bikin 5 hook scroll-stopper buat topik [X]
Kakak: tulis ulang pakai framework PAS, terus humanize (sk20) biar gak bau AI
Kakak: 1 artikel ini repurpose jadi thread + carousel + reels
Kakak: riset tren & kompetitor di niche [X], kasih peluang konten
Kakak: analisis komentar ini — sentimen, pertanyaan, objection
Kakak: bikin 3 variasi A/B buat caption ini (ubah hook doang)
Kakak: jalanin full pipeline: research → draft → visual → schedule → analyze
```
Catatan jujur:
- **Analitik & best-time butuh data real** akun Kakak (export/API). Tanpa itu → estimasi bertanda, bukan angka karangan.
- **Publish & balas komentar = aksi keluar** → default human-in-the-loop (draft → Kakak ACC → kirim). Hal sensitif gak auto-reply.
- Alur juara: sk29 (riset) → sk28 (copy) → sk27 (format) → sk20 (humanize) → sk18 (visual) → sk4/sk17 (schedule).

### Riset & robotik (sk22/sk19)
```
Kakak: riset mendalam [topik ilmiah], dispatch ke library yang tepat + sumber
Kakak: cari dataset/model di Hugging Face buat [task]
Kakak: robot di Isaac Sim lihat botol merah terus ambil (VLA, latih di sim dulu)
```
Robot fisik / VLA real = gate R9 + meta-action STOP selalu menang. Sains = dispatch ke library tervalidasi + verifikasi, bukan ngarang hasil.

---

## Yang perlu Kakak siapin sebelum mulai

1. **VPS akses** — ✅ udah punya `root@vmi3159875`
2. **Master password vault** — buat sekarang, minimum 16 char, simpan di password manager
3. **RPC primary + fallback per chain** — minimum 2 endpoint per chain (rotating biar gak rate-limit). Recommended: Alchemy / Infura / QuickNode + 1 public RPC sebagai fallback
4. **Test wallet kecil dulu** — generate wallet baru via Hermes, isi $20-50 buat smoke test, jangan langsung pakai wallet utama
5. **Telegram bot baru buat alert** — bikin via @BotFather, taro token-nya di `HERMES_TG_BOT_TOKEN`. Jangan pakai bot yang sama dengan channel publik Kakak
6. **API key opsional** — skip dulu kalau belum, Hermes auto-fallback:
   - 1inch (swap): free tier OK
   - Reservoir (NFT): free tier OK
   - Nansen (smart money): paid, paling akurat — opsional
   - Arkham: free tier OK
   - Zerion / Birdeye (portfolio): free tier OK

Setelah 6 hal ini ready → Hermes bisa langsung run. Mau gua bikin **bootstrap script** otomatis (install + env setup + first wallet gen + smoke test), atau Kakak prefer setup manual step-by-step?

---

## Cara cepat verify v7.0 + hermes udah jalan

Setelah install + restart, cek 5 hal:

```bash
# 1. Agent boot tanpa error
pm2 logs hermes --lines 20
# harus muncul: [BOOT] v7.0 SYADAGENTIC SUPREME loaded

# 2. Env var ke-load
env | grep -E "HERMES_|RPC_|ARKHAM_" | head -10

# 3. Skill ke-baca (sekarang sk1-sk32 + sk52-sk58)
ls ~/.openclaw/workspace/openclaw/skills/
# harus liat: sk0-sk32, sk52-sk58, hermes/

# 4. Integrity OK (PENTING — boot rail)
python3 tools/skill_integrity.py verify
# harus: "✅ Integritas OK — 150 file cocok" (exit 0)

# 5. Test offline hijau (zero leak)
bash tools/tests/run_tests.sh           # 85 tests OK
bash skills/hermes/tests/run_tests.sh   # 44 tests OK
# total 129 pass, 0 ResourceWarning di -W error::ResourceWarning
```

Kalau 5 hal di atas ✅, SYADAGENTIC v7.0 siap eksekusi.

> Catatan: tiap habis edit/tambah file `.md` atau `.py`, jalanin `python3 tools/skill_integrity.py generate` lalu `verify`. Verify gagal (exit≠0) = boot rail nahan operasi on-chain sampai diaudit.
