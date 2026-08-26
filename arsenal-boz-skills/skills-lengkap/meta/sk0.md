# sk0 — Skill Registry & Reflection Loop (BOZAGENTIC)
# Load when: sk0
# Category: Core

## REGISTRY

Scan table. Match intent. Load matched skill(s) on demand.
Do NOT preload skill files — token cost.

```
ID  | DOMAIN                              | KEYWORDS (high-weight)
----|-------------------------------------|------------------------------------------------
sk1  | Monetization & value generation     | monetize, pricing, jual, jualan, cuan, funnel
sk2  | Infrastructure & deployment         | VPS, deploy, SSH, nginx, docker, systemd
sk3  | Content creation & distribution     | viral, hook, caption, thread, naskah, konten
sk4  | Process orchestration & bots        | telegram bot, cron, webhook, n8n, automate, otomatis
sk5  | Data transformation & insight       | spreadsheet, excel, csv, dataset, snapshot, laporan
sk6  | Protocol binding & service bridge   | API, REST, webhook, midtrans, integrasi
sk7  | Inference systems & AI builder      | LLM, prompt, claude API, openrouter, kimi, agent, add model, tambah model, registry model
sk8  | File & artifact production          | PDF, DOCX, XLSX, PPTX, generate file, dokumen
sk9  | Interface construction              | landing page, react, tailwind, frontend, UI
sk10 | Web3 / crypto operations            | wallet, airdrop, on-chain, RPC, ethers, viem, mint
sk11 | Security audit & review             | audit, vulnerability, exploit, scam check, malicious
sk12 | Batch / parallel operations         | batch, parallel, bulk, mass, queue, worker, snapshot
sk13 | Universal NFT minter (any contract) | mint, opensea, manifold, zora, seadrop, NFT, claim, drop
sk14 | Daily assistant: briefing & alerts  | briefing, ringkasan harian, alert, kabarin kalau, pantau harga, alarm
sk15 | Daily assistant II: watchdog/vault/multimodal/triage | watchdog, restart kalau mati, simpen alamat, macro, voice note, screenshot, triage
sk16 | Software engineering & coding       | coding, bikin app, backend, API server, database, testing, scaffold, refactor, golang, rust, fastapi
sk17 | Power pack: planner/swarm/automation/backtest/dashboard/voice | rencanain, workflow, otomatis kalau, backtest, dashboard, ngomong, swarm, tim agent
sk18 | Creative & media generation         | comfyui, manim, excalidraw, ascii video, slide, design system, diagram, deck
sk19 | Desktop & physical control          | isaac sim, omniverse, robot, macos control, applescript, scene, usd, mobility, ros2
sk20 | Humanizer & brand voice             | humanizer, brand voice, ai tone, manusiawi, rewrite nada, voice profile
sk21 | Enterprise & defensive ops          | KQL, azure, log analytics, sentinel, HIDS, auto firewall, block ip, intrusion
sk22 | Scientific & deep research          | deep research, AI-Q, tooluniverse, hipotesis, citations, riset ilmiah, eksperimen
sk23 | Executive function & neurodivergent | task breakdown, executive function, ADHD, overwhelmed, fokus, context switch, prioritas
sk24 | MCP-builder & prompt engineering    | MCP server, bikin MCP, FastMCP, prompt engineering, fix prompt, audit prompt
sk25 | Compliance, CI/CD & code migration  | compliance, regulasi, GDPR, SOC2, CI/CD, pipeline, code migration, port bahasa
sk26 | Product & spec workflows            | PRD, to-issues, grill me, spec, user story, TDD, internal comms
sk27 | Content strategy & social media     | content calendar, content strategy, content pillar, carousel, reels, platform adapter, scroll-stopper
sk28 | Copywriting & writing mastery       | AIDA, PAS, CHEF, copywriting framework, SEO writing, storytelling, localization, multilingual
sk29 | Content research, analytics & pipeline | competitor analysis, trend research, social listening, audience insight, content pipeline, A/B caption, best time post
sk30 | Client Revenue Engine (bulk gig, API-first) | client revenue, garapan, bulk gig, harvest, scrape API, anti-browser, mass akun, otomasi job klien, ekstrak data
sk31 | Airdrop Intelligence (eligibility/sybil/claim/exit) | eligibility airdrop, skor airdrop, layak airdrop, sybil, anti-sybil, claim window, jadwal claim, kalender airdrop, vesting unlock, exit plan, kapan jual token
sk32 | CTF / Whitehat toolkit                  | CTF, capture the flag, whitehat, bug bounty, decode flag, crypto challenge, caesar, xor cipher, hash identify, forensics, HTB, THM
sk33 | Pre-TGE Alpha Radar (deteksi airdrop dini) | alpha airdrop, pre-TGE, points program, testnet incentivized, radar airdrop, proyek belum ada token, worth difarming
sk34 | Farming Portfolio & ROI Optimizer       | ROI farming, portfolio airdrop, untung rugi farming, gas vs hasil, farm mana lanjut, drop farming, wallet nganggur
sk35 | Auto Guide Studio (panduan otomatis)    | bikin panduan airdrop, tutorial airdrop, guide step by step, artikel airdrop, embed referral
sk36 | Tokenomics & Unlock Pressure Engine     | unlock token, vesting, cliff, kalender unlock, sell pressure, tokenomics, jual sebelum unlock
sk37 | Anti-Scam Sentinel (brand protection)   | situs palsu, domain palsu, typosquat, phishing airdrop, scam check, warning scam, drainer
sk38 | Contract-Change & Claim-Address Watcher | kontrak berubah, proxy upgrade, claim address, aman claim gak, watch kontrak, cek sebelum claim
sk39 | Community Intelligence (dengerin komunitas) | topik trending komunitas, sentimen komunitas, FUD, analisis chat, pertanyaan member, ide konten komunitas
sk40 | Omni-Repurpose Engine (1 konten → semua) | repurpose konten, ubah jadi thread, carousel IG, script tiktok, script youtube, multi platform
sk41 | Video Script-to-Screen Pipeline         | bikin video, script video, storyboard, voiceover, subtitle, srt, reels, youtube video
sk42 | Hook A/B Lab + Performance Predictor    | hook, judul konten, headline, a/b test judul, stop scroll, prediksi engagement, varian judul
sk43 | CTF Web Exploitation (sub of sk32)       | CTF web, SQLi, SSTI, SSRF, IDOR, XXE, JWT, deserialization, prototype pollution, race condition
sk44 | CTF Binary Exploitation / pwn (sub sk32) | CTF pwn, buffer overflow, ret2win, ret2libc, format string, heap, ROP, pwntools, GOT leak
sk45 | CTF Reverse Engineering (sub of sk32)    | CTF reverse, angr, symbolic execution, Ghidra, radare2, decompile, keygen, deobfuscation
sk46 | CTF Cryptography (sub of sk32)           | CTF crypto, RSA attack, Wiener, Hastad, common modulus, Coppersmith, padding oracle, nonce reuse
sk47 | CTF Forensics & Stego (sub of sk32)      | CTF forensics, stego, pcap, memory dump, volatility, binwalk, exiftool, zsteg, steghide
sk48 | CTF Prompt-Injection/LLM (sub of sk32)   | CTF prompt injection, LLM red-team, jailbreak, Gandalf, Lakera, Mosscap, OWASP LLM01, extract system prompt
sk49 | Team Orchestration & Multi-User Ops  | team, tim, anggota, collaboration, delegate, assign, task routing, multi-user, role, billing split, assign task, client management
sk50 | Autonomous Monetization Engine       | monetize, revenue, profit, earning, income, treasury, yield, P&L, cashflow, auto-revenue, passive income, profit report, money maker
sk51 | Offensive Security & Red-Team Ops    | offensive, red-team, adversary, exploit dev, backdoor, payload, C2, implant, post-exploit, persistence, lateral movement, exfil, opsec

H1  | Swap & sell via aggregator          | swap, 1inch, jupiter, jual token, sell, DEX
H2  | Cross-chain bridge                  | bridge, LayerZero, stargate, LI.FI, across, hop
H3  | DeFi (lending/staking/perp)         | aave, lido, GMX, hyperliquid, pendle, defi
H4  | Token launch & NFT mint sniping     | snipe, honeypot, PairCreated, GoPlus, sniping
H5  | Whale & mempool tracking            | mempool, whale, nansen, arkham, smart money, tracker
H6  | NFT buy/sell (marketplace)          | beli NFT, blur, magic eden, tensor, reservoir, listing
H7  | Web3 sign-in & typed signing        | SIWE, walletconnect, EIP-712, ENS, permit, EIP-1271
H8  | Browser dApp automation             | buka dapp, browser, playwright, navigate, connect wallet, isi form
H9  | Universal contract read/write       | baca/tulis kontrak, read/write, call fungsi, ABI, inspect, proxy, eksekusi
H10 | Crypto dev: deploy/compile/test     | deploy kontrak, compile, forge, solidity, test, verify, CREATE2, bikin token

sk52  | Internal capability refinement      | improve system, self-audit, upgrade brain
sk53  | Deep decomposition & strategy       | strategy, architecture, decompose, plan, design system
sk54  | Fault diagnosis & resolution        | error, bug, debug, gagal, rusak, stack trace
sk55  | Self-improvement & autonomous fix   | self improve, belajar, makin pinter, auto fix, upgrade diri, learn
sk56  | Agentic eval & self-critique        | eval, self-critique, variance, konsistensi, flaky, regression, ukur
sk57  | Systematic debug & auto-debug loop  | systematic debug, RCA, root cause, hypothesis, intermittent, reproduce
sk58  | Problem shaping & decision support  | problem shaping, brainstorming, sign-off, framing, vague goal, uncertainty
```

### V7 NEW SKILLS (sk49–sk51)

**sk49 — Team Orchestration & Multi-User Ops**: team delegation (Level 0–3 routing), task assignment tracking, per-member billing attribution, conflict detection & resolution, client management dashboard, multi-session awareness, role-based access control. → `skills/sk49.md`

**sk50 — Autonomous Monetization Engine**: treasury management, cashflow tracking, P&L generation, revenue stream optimization, auto-revenue strategies (MEV, airdrop, yield, NFT flip), cost optimization, profit reporting (daily/weekly/monthly), passive income pipeline maintenance. → `skills/sk50.md`

**sk51 — Offensive Security & Red-Team Ops**: exploit development lifecycle (research → PoC → weaponize), C2 infrastructure (Cobalt Strike/Mythic/Sliver patterns), post-exploitation (persistence, lateral movement, privilege escalation), payload generation (shellcode, DLL hijacking, process injection), operational security (OPSEC), adversary simulation (MITRE ATT&CK mapping), red-team infrastructure design, phishing & social engineering frameworks. → `skills/sk51.md`

---

## ROUTING

```
0 matches:     answer from core knowledge — load nothing
1 match:       load full skill file
2+ matches:    pick PRIMARY (highest score), load it fully
               pull SUPPORTING (>50% of primary's score) section-by-section
ambiguous tie: ask once — "Fokus ke [A] atau [B] dulu?"
H-skill hit:   load skills/hermes/DISPATCH.md FIRST, then specific reference
```

### Hermes routing
H1-H10 are NOT standalone files. They map to `skills/hermes/references/*.md`:
```
H1 → hermes/references/swap.md       H2 → hermes/references/bridge.md
H3 → hermes/references/defi.md       H4 → hermes/references/sniping.md
H5 → hermes/references/monitoring.md  H6 → hermes/references/nft.md
H7 → hermes/references/web3_connect.md H8 → hermes/references/browser.md
H9 → hermes/references/contract_read.md + contract_write.md
H10 → hermes/references/deploy.md
```
Load `hermes/DISPATCH.md` once per session if any H-skill fires.

---

## REFLECTION LOOP

Runs silently after every output. Non-negotiable.

```
✅ Immediately executable / usable as-is?
✅ Anything the operator will need next that's missing?
✅ Generic advice — could be replaced with operator-specific code?
✅ Faster or cleaner path missed?
✅ Did I include the run command / deploy step?
✅ Token usage justified — could same value land in fewer lines?
✅  Does this generate value or move the profit needle?
✅  Can this scale to the team?
```

Any fail → revise BEFORE outputting.
Upgrade exists → append: `🔧 Upgrade: [one line]`
Revenue applicable → append: `💸 Revenue: [estimated impact]`

---

## REFLECTION ESCAPE HATCH

If reflection loop catches issue but fix would 2x the response length → ship the working version, append:
> `🔧 Bisa di-upgrade ke [X]. Mau elaborasi?`

---

## AUTONOMOUS SCAN 

After every reflection loop, scan autonomous triggers table from AGENTS.md.
If any trigger fires → auto-execute in background, log to memory.
Push exceptions to next briefing.
