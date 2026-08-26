# SYADAGENTIC frameworks/ — Teknik & Metodologi Reusable (Ekstraksi)

Sumber: `~/Downloads/SYADAGENTIC/frameworks/` (214 file .md)
Fokus: metodologi yang bisa dipakai ulang (bukan laporan audit spesifik perusahaan).
Dibaca: 2026-08-26 oleh subagent Hermes.

---

## 1. attack-chains/ (11 file — SEMUA dibaca penuh)

### README.md
- Konsep inti: chained attack methodology untuk web2 + web3 bug bounty.
- Komponen: Web2 chains, Web3 chains, attack-chaining-core (capability taxonomy, chain checklist, output templates), attack-surface-mapper (domain lenses, map templates).
- Contoh chain: Auth bypass → priv-esc; flash loan → price manipulation → liquidation; oracle manipulation → sandwich.

### attack-surface-mapper/SKILL.md (teknik inti)
- **Attack Surface Mapper = audit map, bukan claim vuln.** Semua permukaan harus punya bukti (evidence-backed).
- 7 langkah: (1) system inventory, (2) enumerate entry points (HTTP/RPC/WS/GraphQL, callbacks, webhooks, parser/deserialization paths, queues, cron, IPC, admin/CLI, contract external functions, p2p/gossip/consensus, bridge messages, oracle updates, env/secrets/deploy manifests), (3) track attacker-controlled data per entry point (attacker class, auth required, input fields, canonicalization layers, parsers, sinks, rate/timing/replay properties), (4) map trust boundaries (unauth→auth, user→admin, frontend→internal, off-chain→on-chain, untrusted contract→callback protocol, relayer/oracle→authority), (5) identify assets + invariants (state the invariant that MUST hold), (6) score audit priority (reachability, attacker control, privilege crossed, parser complexity, callback potential, novelty, recovery difficulty), (7) produce narrow hunter hypotheses — bukan kesimpulan "remote DoS exists".
- Aturan: jangan asumsikan route publik hanya karena handler ada; bedakan default vs legacy config; dangerous ≠ vulnerability.

### attack-chaining-core/SKILL.md (teknik inti — paling reusable)
- **Core rule: chain valid HANYA jika postcondition step N memenuhi documented precondition step N+1.** Jangan infer kompatibilitas hanya karena same product.
- Normalisasi primitive: `starting capability + preconditions -> trigger -> primitive -> postcondition/capability gained`; pisahkan observed fact vs inferred consequence.
- **Capability graph**: node = attacker capabilities + protected assets; edge = verified/plausible primitive (dengan preconditions, evidence, cost, reliability, duration, scope status).
- 8 dimensi scoring 0-5: C(compatibility), R(reachability), A(attacker control), L(reliability), E(evidence), I(impact), S(scope fit), M(mitigation resistance). Confidence = round(100*(C+R+A+L+E+I+S+M)/40) dengan mandatory caps: unverified critical transition ≤69, production relevance unproven ≤64, impact inferred ≤74, scope unknown ≤59, out-of-scope step = reject, attacker starts with equivalent capability = no escalation.
- **Counter-evidence search (5)**: token audience mismatch, session rotation, tenant isolation, canonicalization, atomicity, rollback, rate limits, privilege boundaries, oracle freshness, quorum/finality, attacker already has capability.
- **Prune weak chains (6)**: speculative→speculative, incompatible states, out-of-scope, secrets equivalent to final impact, unrealistic victim behavior, impractical timing, no capability gain, longer than minimal chain.
- Verdict: NO_VALID_CHAIN / CHAIN_CANDIDATE / RETURN_TO_VERIFIER / CHAIN_VALID_IMPACT_UNPROVEN / REPORT_READY_CHAIN / REJECT_OUT_OF_SCOPE.
- Severity = demonstrated final impact, bukan jumlah severity individu.

### attack-chain-web2/SKILL.md (plugin domain)
- Web2 chain surfaces: auth/registration/recovery/MFA/SSO/OAuth/session, object+function authz, multi-tenant, file upload/parse/delivery, SSRF, cloud metadata/IAM/secrets/queues/storage, cache/proxy/request interpretation, injection, client-side + account impact, business-logic state machines + race.
- **Identity ladder — jangan samakan tanpa proof**: email ≠ user ID ≠ reset token ≠ session cookie ≠ auth session ≠ MFA bypass ≠ admin impersonation.
- **SSRF pivot ladder**: outbound request → internal host reachable → response readable → headers/method controllable → metadata bypass → credentials → valid for principal → IAM action. Blind SSRF ≠ cloud compromise.
- **File chains**: track bytes → content-type → extension → storage key → transformation → execution context → delivery origin. Upload ≠ execution.
- **Client-to-server**: XSS/open redirect ≠ ATO otomatis — buktikan victim requirements, cookie accessibility, CSRF, token exposure.
- Web2 chain matrix: primitive output → next precondition → mandatory proof (mis. reset token → password reset endpoint → purpose/audience/expiry/single-use).

### attack-chain-web3/SKILL.md (plugin domain)
- **Web3 chain families (11)**: temp liquidity→price influence→extraction; oracle control→mis-valuation→borrow/liquidation; callback/reentrancy→intermediate state→invariant violation; rounding drift→amplification→imbalance; signature/replay→unauthorized transition; governance weight→proposal→treasury impact; bridge proof weakness→unauthorized mint; wallet/approval→asset movement; MEV/ordering→extraction; validator scheduling→divergence/liveness; snapshot/restart replay→corruption.
- **Mandatory Web3 state model per step**: chain/block context, contract+version, pre/post state, caller authority, balances/shares/debt/collateral, oracle values+deviation bounds, atomicity/ordering, finality/reorg assumptions, capital required, fees/slippage/profitability.
- Komposisi rules: atomic chains (flash loan — semua step harus survive revert), multi-tx (persistence, front-running exposure), oracle (pisahkan ability to trade vs ability to move protocol's consumed oracle; validasi source, aggregation, TWAP window, deviation, stale handling), governance (pisahkan token ownership vs voting power; snapshot/delegation/quorum/timelock), bridge (trace full trust path source event→relayer→proof→replay checks→destination), signature (domain separator, chain ID, nonce, expiry, malleability), validator (klasifikasi schedule: attacker-forced/biased/network-possible/harness-only/protocol-illegal).
- **Economic impact discipline**: jangan samakan temporary accounting deviation dengan extractable loss. Hitung capital at risk, max executable size under liquidity, fees/slippage, liquidation/arb response, per-block limits, recoverable vs irreversible, profitable vs griefing.
- Web3 chain blockers: CEI, invariant checks after callbacks, revert/atomicity, TWAP/deviation/staleness, caps/pauses/guardians/timelocks, domain separation, replay protection, finality thresholds, quorum/BFT assumptions, slashing cost.

### references (pendukung)
- **capability-taxonomy.md**: label capability standar agar tidak false match — Access (NETWORK_REACH_PUBLIC/INTERNAL, AUTH_USER/TENANT_ADMIN/GLOBAL_ADMIN, LOCAL_*), Read (PUBLIC_METADATA, CROSS_TENANT_OBJECT, SECRET_MATERIAL, SIGNING_KEY, PROTECTED_STATE), Write (OWN/CROSS_TENANT/CONFIG/EXECUTABLE_PATH/PROTOCOL_STATE), Execution (CLIENT_CONTEXT/SERVER_WORKER/SERVICE_IDENTITY/HOST_PRIVILEGED), Identity (ENUMERATE_ACCOUNT, CREATE_OR_FIX_SESSION, OBTAIN_ONE_TIME/REUSABLE_TOKEN, IMPERSONATE_USER/SERVICE), Web3 (INFLUENCE_ORACLE_INPUT, INFLUENCE_TX_ORDER, ACQUIRE_TEMP_LIQUIDITY, ALTER_GOVERNANCE_WEIGHT, SUBMIT_INVALID_STATE, CAUSE_DIVERGENCE, BYPASS_FINALITY, MOVE_OR_LOCK_ASSETS).
- **chain-checklist.md**: checklist primitive quality, composition (context match, timing overlap, no hidden privilege jump), adversarial review (token binding, authz boundaries, rate limits, rollback, finality), impact (incremental capability per step, minimal chain), submission readiness.
- **web2-chain-matrix.md / web3-chain-matrix.md**: tabel primitive→precondition→mandatory proof (contoh web3: inflated shares→borrow/redeem capacity→accounting formula + executable liquidity; crafted validator message→consensus transition→protocol-legal sequence + honest-node acceptance).
- **domain-lenses.md**: lens per domain — Web2 (auth/recovery, sessions, tenant, upload/parser, SSRF, cache/proxy, cloud IAM), DeFi (authority, token movement, accounting invariants, callbacks, oracle, liquidation, rounding, governance, upgradeability, signature domains), Bridges (finality, proof verification, replay, validator thresholds, mint/unlock symmetry), Validators (untrusted messages, ordering, epoch transitions, persistence, replay, quorum, fork choice, equivocation, resource bounds).
- **economic-checklist.md**: 11 poin feasibility — capital, flash/borrow limits, liquidity, slippage+fees, gas, oracle mechanics, arb response, caps, net extractable value, irreversibility, TVL≠loss tanpa executable path.

---

## 2. audit-core/ (13 master + 8 report + README — SEMUA dibaca)

### AUDIT_PROCESS_MASTER.md (teknik inti — "how top firms audit")
- **Phase 0 — pahami protokol dulu**: baca docs, gambar flow diagram (kalau nggak bisa gambar, belum ngerti), identifikasi trust assumptions (siapa dipercaya, apa yang bisa mereka lakukan kalau jahat), identifikasi invariants, tanya tim "apa yang paling lo takutin?".
- **Phase 1 — automated scan**: Slither (human-summary, data-dependency, inheritance-graph), Echidna (tulis properties DULU — supply conservation, no-profit), Manticore symbolic. Triage tool untuk hot spots, bukan final findings.
- **Klasifikasi catch-vs-miss tools**: tools catch reentrancy standar, missing access control, uninitialized storage, tx.origin; MISS = business logic, economic attacks, cross-contract trust, oracle manipulation, governance, rounding direction, composability.
- **Phase 2 — manual review 4 pass**: (1) architecture top-down (constructor, state vars, modifiers, external API grouping, events missing = red flag), (2) function-by-function (access control, input edge cases 0/max/address(0), state-change order vs external call, external call return checks, math rounding direction/mulDiv, token quirks fee-on-transfer/rebasing), (3) cross-function (flash loan combos, state machine stuck/skip states, race/frontrun/sandwich, economic modeling with concrete numbers), (4) external dependencies (oracle staleness/manipulation/fallback, DEX liquidity/slippage, token quirks, bridge trust/replay).
- **Phase 3 — attack pattern checklist (25 item)**: reentrancy (single/cross-fn/cross-contract), access control, overflow, unchecked returns, front-running/MEV, oracle manipulation, DoS, uninitialized storage, delegatecall untrusted, selfdestruct, signature replay, flash loan, governance, sandwich, rounding, donation/inflation (ERC4626), proxy storage collision, initializer re-init, timestamp, tx.origin, unbounded loops, slippage, fee calc, precision loss, stale state.
- **Spearbit "What Would Break"**: untuk setiap function tanya "bagaimana kalau... amount=0? max uint? 100x dalam 1 tx? dari contract? frontrun? admin key compromised? oracle return 0/max? transfer revert/return false? sebelum initialize? di-upgrade malicious? 2 user simultaneous? 0/max liquidity?".
- **Quantstamp formal spec**: pre/post-conditions + invariants; prove violation = CRITICAL, show scenario = HIGH/MEDIUM, theoretical = LOW/INFO.
- **Report format industri**: Title [H-01], Severity, Summary, Vulnerability Details (file:line), Impact (dengan angka), PoC (Foundry test), Recommended Mitigation (before/after code). Severity justification 4-kriteria.
- **Common mistakes report**: vague "could potentially lead to loss", report tanpa impact, gas optimization sebagai finding, overclaim severity, tanpa PoC.
- **Fix review (Phase 5)**: root cause vs symptom, new issues introduced, re-run tools, retest original PoC + variants (bisa di-bypass?), consistency (pattern di tempat lain?).
- **Firm techniques**: ToB property-based (tulis properties sebelum audit), Spearbit independent→collision (2-5 auditor independen, gabung temuan — A nemu missing check, B nemu fungsi exploit → CRITICAL), Cyfrin invariant-first (definisikan invariants SEBELUM baca code, fuzz, root cause = bug), Sherlock economic modeling (profitability setelah gas+capital), Quantstamp formal, Halborn attack surface mapping (impact × probability, 40% loss dari infra/social/key bukan contract), Hacken pattern matching.
- **Audit mindset pyramid**: junior "is code correct?" → senior "how can I break it?" → elite "how can I make money from it?". 3 questions tiap function: WHO can call, WHAT with weird inputs, HOW to profit.
- Quote kunci: *"The bug is never where you first look. It's where two correct things interact incorrectly."*

### AUDIT_WORKFLOW_COMPLETE.md (pipeline 9 phase + red flags)
- Pipeline: Phase 0 recon (bounty page, clone, docs, inheritance map, previous audits, trust model, compiler CVEs) → Phase 1 automated (slither parallel + semgrep defi-logic-rules + aderyn + mythril + forge test) → Phase 2 line-by-line (setiap contract: baca EVERY line, money flow IN→OUT, access control tiap state change, CEI, math, edge cases, events match, assembly, storage layout, cross-contract assumptions) → Phase 3 economic modeling (10 skenario: flash loan $1B, oracle 50%, malicious admin, first user, frontrun, donate 1 wei, public sync, governance cost, sandwich, jadi protocol B) → Phase 4 cross-protocol (map interaction, list assumptions, break each) → Phase 5 formal verification (Z3 BitVec SAT=bug, Halmos, Echidna, Foundry PoC, Medusa 50K+) → Phase 6 bytecode verification (source vs bytecode, storage layout, selectors, EIP-1967, guard decode) → Phase 7 severity calibration → Phase 8 report+submission.
- **RED FLAGS (instant deep dive)**: balanceOf() di vault accounting → inflation; public sync/update/skim → donation; no slippage → sandwich; oracle no staleness → manipulation; admin drain no limit → rug; governance no snapshot → flash vote; reward no time lock → flash claim; delegatecall non-immutable → storage hijack; selfdestruct reachable → forced ether; tx.origin → phishing; inconsistent state tracking → cap bypass; abi.encodePacked multiple dynamic → hash collision; unchecked external call; unbounded loop → DoS.
- Tool cheat sheet: slither/aderyn/mythril/echidna/medusa/halmos/z3/cast/forge inspect commands.

### ECONOMIC_ATTACK_MASTER.md (10 kasus + meta-pattern)
- 10 kategori economic attack dengan detect question: (1) flash loan+governance "bisa vote dalam 1 tx?", (2) flash loan+reward "claim tanpa time lock?", (3) donation/inflation "balanceOf() dipakai pricing?", (4) oracle manipulation "cost move price 10%?", (5) reentrancy compiler bug "compiler version known CVE?", (6) key compromise "admin drain tanpa limit?", (7) cross-protocol arb, (8) sandwich, (9) governance 1 tx, (10) economic griefing.
- **Invariant yang dilanggar per kasus** (Beanstalk: voting power harus dari staked tokens sebelum proposal; Euler: eToken value dari underlying balance bukan total supply inflatable; Mango: oracle harus resisten low-liquidity; BonqDAO: oracle report harus punya dispute period; Curve Vyper: compiler bug reentrancy lock; Penpie: rewards proportional ke TIME staked bukan amount 1 block).
- **Audit checklist economic lens (10 pertanyaan wajib)** — sama dengan workflow phase 3, reusable untuk tiap audit.

### EVM_BYTECODE_MASTER.md (teknik inti bytecode)
- Tabel opcode lengkap (STOP–SELFDESTRUCT) dengan stack effect.
- **Storage layout Solidity**: slot 0..n, struct per-field, mapping = keccak256(key.slot), array = keccak256(slot)+i, packing uint128+uint128 share slot.
- **EIP-1967 slots**: implementation 0x360894..., admin 0xb53127..., beacon 0xa3f0ad... (untuk cast storage).
- **Storage collision bug pattern**: implementation & proxy share storage; safe = ERC-7201 namespaced storage.
- **Assembly patterns**: transient storage reentrancy guard (EIP-1153 TSTORE/TLOAD — check reset di ALL paths, cross-function reentrancy per-contract, Cancun+ only), minimal proxy EIP-1167 (implementation hardcoded, no upgrade, selfdestruct kills all clones), custom error assembly (mstore selector + revert(0x1c,0x04)), bit masking packing (wrong mask/shift = corruption).
- **Real bugs**: Parity wallet (library state var slot 0 + delegatecall + initWallet + kill), incorrect bit shift (overflow uint8), delegatecall user-controlled, TSTORE cross-chain.
- **Audit checklist assembly (10 item)**: slot calc, masking, delegatecall target immutable, guard reset all paths, transient available, returndata size check, memory overlap FMP, no selfdestruct in target, compiler known bugs, storage layout proxy vs impl match.
- Tools: cast disassemble/storage/code/run, forge inspect storageLayout/methodIdentifiers, evm.codes, tenderly.

### SECURITY_TOOLKIT.md (library + tool reference)
- **Solmate vs OZ perbandingan**: solmate NO zero-address check (by design gas), cached domain separator (INITIAL_CHAIN_ID), SafeTransferLib assembly (dirty bits), FixedPointMathLib unsafeDiv/unsafeMod return 0 silently kalau y=0, **Solmate ERC4626 TIDAK ada virtual shares → donation attack PROFITABLE**.
- **PRB-Math**: type-safe fixed point (UD60x18/SD59x18), mulDiv 512-bit, exp 192-bit; wrap() tanpa validation vs into() validate; unchecked blocks rely on range checks.
- **BoringSolidity**: BoringOwnable combined direct/2-step, BoringERC20 returnDataToString, **BoringBatchable msg.value double-spend warning (Paradigm "two rights might make a wrong")**, BoringRebase elastic/base.
- **Slither**: key detectors per severity (reentrancy-eth/no-eth, arbitrary-send-eth, controlled-delegatecall, suicidal, unprotected-upgrade = HIGH; timestamp, incorrect-equality, unchecked-transfer, tx-origin = MEDIUM), printers (vars-and-auth, entry-points, call-graph, data-dependency, function-summary).
- **Mythril**: symbolic execution — kuat di access control/integer/reentrancy proof, bisa analisis deployed bytecode tanpa source; lambat, path explosion.
- **Echidna**: config (testMode assertion/property/optimization/exploration, testLimit, shrinkLimit, seqLen, multi-sender), property patterns (echidna_* invariant), test modes, workflow (tulis invariants dari docs → run high limit → coverage → shrink minimal repro → regression test ke Foundry).
- **Halmos 0.3.3**: symbolic testing — check_* (property), invariant_* (stateful); PROOF untuk ALL inputs vs fuzz probabilistic; nonlinear (mul/div/mod) lambat/timeout → workaround Z3 Int, bound inputs, split properties; **expectRevert TIDAK supported** → workaround: call function + assert(false) → "all paths reverted" = SAFE; minimal project setup untuk hindari compile timeout.
- **Recommended pipeline**: slither (broad, seconds) → mythril (deep, minutes) → echidna (invariant fuzz) → forge test (regression) → manual review (logic, economics, oracle).
- Combo terbaik: Halmos (prove) + Echidna (break) + Slither (patterns) + Mythril (paths).

### SLITHER_MASTER.md
- Workflow: basic scan → exclude noise → specific detectors → **custom detectors (plugin)**: inconsistent-state-tracking (CashbackRewards maxRewardBps bypass), erc4626-inflation-attack (Basin/Beanstalk), cross-chain-signature-replay (hardcoded chainId EIP-712), unlimited-admin-drain. Cara tulis custom detector (AbstractDetector, ARGUMENT/HELP/IMPACT/CONFIDENCE, _detect, entry_points setup.py).
- 27 printers dengan use case; kunci: human-summary (start), vars-and-auth (authz matrix), entry-points (attack surface), call-graph, echidna (guidance).

### HALMOS_MASTER.md
- Property naming: check_* (assert-based), invariant_* (stateful), prove_* (alternative).
- Pattern: simple assertion, stateful property (deploy+interact), **bug existence proof** (verify correct impl catches it), fix verification.
- Linear (fast) vs nonlinear (slow) — workaround list.
- Pitfall: jalankan di minimal project (forge init), bukan monorepo besar (compile timeout).
- Hasil nyata: 19 properties, ketemu 2 bug (noZeroOwner FAIL, period_monotonic uint32 overflow).

### MEDUSA_MASTER.md
- Config medusa.json: workers, testLimit, callSequenceLength, corpusDirectory, coverageEnabled, assertionTesting (IntegerOverflow, InvalidEnumAccess, InvalidMemoryAccess, OutOfBoundsIndexAccess), propertyTesting (echidna_ prefix).
- vs Echidna: Go vs Haskell, advanced coverage (lcov/html), Foundry-compatible cheatcodes, built-in crytic-compile.
- Assertion types list; hasil Coinbase audit (100K runs 48/48 PASS, multi-sender 50K).

### OZ_MASTER.md + OZ_FULL_MASTER.md (OpenZeppelin v5.6.1 reference)
- **ERC20 _update() pattern**: semua transfer/mint/burn lewat 1 internal hook; override _update() bukan _transfer(). Infinite approval optimization (type(uint256).max skip).
- **ERC4626 donation/inflation attack + OZ mitigation virtual shares**: `assets.mulDiv(totalSupply + 10^decimalsOffset, totalAssets + 1)` — +1 dan +10^offset bikin attack non-profitable. CEI: transfer before mint, burn before transfer.
- **ERC4626 variants comparison** (dari AAVE_V3_REFERENCE): OZ balance-based + virtual shares; Morpho stored + virtual; Arcadia balance-based VAS=0 = BUG; **Aave Stata rate-based = IMMUNE** (shares = assets*RAY/rate, rate global monotonik).
- Proxy patterns: ERC1967 slots, Transparent (admin immutable, selector clashing prevented), UUPS (_authorizeUpgrade MUST override, onlyProxy/notDelegated, proxiableUUID anti proxy-loop), Beacon (1 upgrade all proxies, centralized risk), Clones EIP-1167, Initializable (_disableInitializers, reinitializer version).
- **Audit checklist proxy**: implementation punya _authorizeUpgrade? _disableInitializers di constructor? storage layout compatible? storage gap `uint256[50] __gap` — RULE: hanya append, never insert/reorder.
- ReentrancyGuard v5: slot 0x9b779b..., nonReentrantView, deprecated → ReentrancyGuardTransient EIP-1153.
- Governor: lifecycle Pending→Active→Defeated/Succeeded→Queued→Executed/Canceled; required overrides (_quorumReached, _voteSucceeded, _countVote, _getVotes); extensions (GovernorTimelockControl, GovernorPreventLateQuorum, GovernorVotesQuorumFraction, GovernorCrosschain).
- **Governor attack vectors**: flash loan governance (mitigasi votingDelay>0 + snapshot), proposal frontrunning (mitigasi _isValidDescriptionForProposer hash), timelock bypass (always use TimelockController), quorum manipulation via supply burn (absolute quorum).
- OZ Wizard misconfigs: lupa _disableInitializers, storage collision, FlashMint+ERC4626 combo (exchange rate corruption), governor tanpa quorum minimum, UUPS tanpa override, pausable tapi transfer tidak di-pause.
- Defender: Sentinel (event/tx/Forta/block triggers + conditions + notification channels), Autotask (serverless, SDK, auto-pause on exploit), Relay (EIP-2771 meta-tx, trusted forwarder — whitelist functions, jangan kasih admin access), Admin (governance automation — proposal creation bukan execution).
- ECDSA (reject malleable s, 65-byte, hash dulu), EIP712 domain, MerkleProof sorted pairs (anti second-preimage), SignatureChecker (EOA + ERC-1271), v5 baru: P256/RSA/WebAuthn/ERC7913.
- VestingWallet risks: ownership transferable → jual unvested, rebase break math, native ERC20 double-withdraw.

### AAVE_V3_REFERENCE.md (pattern reference)
- **Pattern yang bisa dicuri**: (1) cache pattern — read semua storage sekali ke ReserveCache struct, kerja di memory, tulis balik di akhir (gas + consistency), (2) rate-based ERC4626 immune inflation, (3) virtualUnderlyingBalance stored accounting — jangan pernah derive dari balanceOf(), (4) deficit system — track bad debt per-reserve + external backstop (Umbrella) tanpa cascade/bricking, (5) validation-before-callback anti-reentrancy (validate → transfer → callback → repayment), (6) try/catch permit silent failure (permit = convenience, real validation di transferFrom).
- **Lessons**: mature protocols = fokus di EXTENSIONS dan INTEGRATIONS (Stata token, LM token, custom IRMs, periphery), bukan core; new deployments on new chains = less audited.

### AUDIT_FIRMS_MASTER.md (8 firm methodology)
- **Spearbit/Cantina**: hybrid human+AI, SPECIALIZATION (DeFi→DeFi specialist, ZK→ZK specialist) — deep domain knowledge > broad tool knowledge; independent→collision review.
- **Cyfrin**: education+tools+audits; Solodit (vuln database — cek known patterns SEBELUM audit, solodit.xyz), Aderyn (Rust static analyzer, lebih cepat dari Slither).
- **Quantstamp**: formal verification — define mathematical properties, prove for ALL inputs (bukan samples); Security Beat monthly report = attack pattern database gratis.
- **Halborn**: red team + enterprise + compliance; "What's the easiest path to profit?"; 88% losses dari operational failures bukan code bugs; AI security (LLM prompt injection, agent tool abuse, MCP, vector DB poisoning) = arah masa depan.
- **Sherlock**: competitive audit + insurance; watson best practices — submit EARLY, clear exploit path, PoC, severity match impact, check trust assumptions dulu (jangan report "admin can rug"); judge perspective (is it ACTUALLY exploitable, duplicate?, reproducible?).
- **Hacken**: 3-layer (automated → manual → dynamic), double coverage (2 auditor paralel), HackenProof (bayar hanya verified findings, duplicate = $0), compliance (MiCA, DORA, VARA), Extractor monitoring.
- **8-firm integrated framework (7 step)**: Security Specification (actors, trust model, invariants, state machine) → Recon (Solodit, past reports) → Automated (semgrep/slither/aderyn/mythril) → Fuzzing (medusa/echidna, fokus coverage gaps) → Manual (domain specialist, economic modeling, trust boundary, state transition) → Red Team (profit path, social engineering, infra/key) → Formal Verification (solvency, conservation, access control) → Report.

### reports/ (8 file — metodologi audit nyata)
- **EIGENLAYER_AUDIT.md**: pola arsitektur restaking — magnitude-based slashing (rounding favor operator, multiple slashes compound), **DepositScalingFactor (DSF)** anti-slashing-griefing (new deposits "forgive" prior slashing, blend old/new shares), **withdrawal queue with slashing window** (shares tetap slashable selama delay — cegah slash-and-run), allocation/deallocation delay (deallocate tetap slashable sampai delay lewat). Reusable: pola anti-griefing untuk pending state.
- **KELP_DAO_AUDIT.md**: metodologi **bytecode reverse engineering** (5105+11760 lines disassembly) — reconstruct architecture dari deployed bytecode (proxy→impl, storage slots untuk cap/current/periodStart, selector check isLRTManager), on-chain probing (totalSupply, rate slot, period cap 5000 ETH/24h). Temuan: 1 wei deposit → 0 rsETH silent fund loss; period cap edge case (drifts based on activity).
- **Arcadia_Audit_Notes.md**: temuan CEI-only tanpa nonReentrant (fragile, defense-in-depth recommendation), leverage tanpa redundant health check (single point of failure), donateToTranche inflation threshold 10^decimals + **mathematical proof why it works** (attacker net = 0 profit). Pola: verifikasi mitigasi dengan proof math.
- **Arcadia_V2_Audit_Report.md**: **V1 vs V2 regression audit** — protection REMOVED (donateToTranche minimum share check hilang, relies on virtual shares — verify on-chain via cast call convertToShares), callback-before-payment (bidCallback executes with bidder holding assets → composable exploit risk), division by zero bricking auction (0*0/0 reverts), sequencer downtime auction reset tanpa bound. Metodologi: compare versions, verify mitigation claims on-chain, write verification commands.
- **USUAL_LABS_AUDIT.md**: pipeline bounty (Blockscout extraction 68 files → semgrep → manual) — 7 findings: missing zero check (coefficient=0 → full redemption freeze), precision loss low-decimal tokens (scale down/up truncation), double floor rounding (systematic dust), emergencyWithdraw tanpa timelock, oracle staleness no validation (defense-in-depth gap), nonce threshold griefing, price divergence. + apa yang tidak bisa di-test (PoC mandatory, missing deps).
- **FT_SPARK_FINDING.md**: **deployed-vs-documented divergence** — strategy diubah Aave→Spark tanpa update docs; maxWithdraw() cap = 35-48% collateral locked (bank run = users stuck). Metodologi: fork test 8 proofs on mainnet, contrast with liquid strategies (negative control), distinction from known issue table.
- **BasinDonationReport.md**: **donation/inflation via public sync()** — root cause: sync() baca balanceOf() bukan stored reserves + public + no minimum liquidity. Full PoC Foundry test + math (attacker profit = (X*Y)/(X+Y)), 3 fix options. Ini template finding report terbaik.
- **KELP + Basin + Arcadia**: pola finding report — Summary → Root Cause → Attack Flow → PoC → Impact (dengan angka) → Fix recommendation.

---

## 3. webhunter-os/ (172 file — SKILL, INDEX, workflow, references dibaca penuh; pattern/stub files dibaca representatif)

### SKILL.md (arsitektur 4-5 pillar)
- **4 Pillar + orchestrator**: (1) 8-phase workflow, (2) Attack Pattern Library 33 file (phase1-auth, phase2-injection, phase3-session-api, phase4-advanced), (3) Exploit Knowledge Base 44 file (exploit-kb-1..5: bagaimana vuln manifest di wild — Overview, Root Cause, Recon Signals, Validation Strategy, False Positive Guidance, Business Impact), (4) Protocol Playbooks 43 file (playbook-core/vuln/modern/cloud/advanced — Objective, Preconditions, Workflow, Decision Points, Evidence Collection, Exit Criteria), (5) Orchestrator 44 file (orchestrator-core, decision-engine, memory-state, adaptive-reasoning, reporting-quality).
- **Key principles**: recon first, map all surface, threat model before testing, check false positives, chain vulnerabilities, document evidence, impact-driven reporting.
- Trigger: web/API/cloud targets; smart contract → bughunter-os/audit-core.

### INDEX.md
- Router mapping: vulnerability class → file, tech stack → file, phase → file. Pola index yang reusable untuk framework lain.

### workflow/Phase1-8 (struktur seragam — teknik per fase)
- **Struktur tiap phase**: Objective → Scope → Philosophy → AI Mindset (pertanyaan sebelum mulai) → Workflow 10 modul → Deliverables → Exit Criteria → Common Mistakes → AI Reasoning Checklist → Transition. (Pola template fase yang reusable.)
- **Phase 1 Recon**: 10 modul — target profiling (business domain, user roles, sensitive assets, critical workflows), technology fingerprinting, framework detection, architecture discovery (monolith/microservices/API gateway/trust boundaries), asset discovery (admin portal, swagger, playground, static assets), endpoint enumeration, **JavaScript intelligence** (hidden endpoints, tokens, secrets, source maps, feature flags, API calls), authentication mapping, third-party analysis, attack surface summary.
- **Phase 2 Attack Surface Mapping**: 10 modul — input entry points (forms/query/path/headers/cookies/JSON/multipart/WS), endpoint classification (public/auth/admin/internal/deprecated), auth boundaries, authz boundaries, file handling surface, **business workflow mapping** (registration/login/payments/orders/password reset), client-side surface (JS APIs, localStorage, service workers), external integrations, high-value targets (admin panels, payment, account mgmt, uploads, API gateways), **Attack Surface Matrix** (component/exposure/trust/auth/business impact/priority).
- **Phase 3 Threat Modeling**: critical assets, trust boundaries, threat actors, entry points, **abuse case analysis** (registration/login/password reset/search/upload/payment/notifications), privilege escalation paths, data flow risks, business logic risks (workflow bypass, race, state manipulation, financial abuse), threat prioritization (likelihood/impact/exploitability/business risk).
- **Phase 4 Technical Analysis**: input validation, auth, authz (horizontal/vertical/ownership), session mgmt, API security (rate limiting, mass assignment, excessive data exposure), client-side (DOM, storage, CSP, CORS), server-side, file handling, config review (default creds, debug mode, secrets, TLS), findings summary.
- **Phase 5 Business Logic** ("technically secure ≠ logically secure"): workflow analysis, **state transition analysis** (invalid changes, skipped steps, forced transitions, replay), role/permission abuse, financial logic (discounts/coupons/refunds/pricing/credits/rewards), **resource abuse** (rate limits, quotas, free trials, invitations, storage), multi-step workflow testing, race conditions (concurrent, double-spend, locking failures), business rule validation, abuse scenario development.
- **Phase 6 Exploit Validation**: finding verification (root cause/preconditions/reproducibility), exploit reproducibility, privilege impact, data exposure, business impact (CIA + financial + trust + regulatory), **attack chain analysis**, environmental validation (production relevance, version/config/feature dependency), **false positive elimination** (incorrect assumptions, expected behavior, misconfig vs vuln), severity prioritization (exploitability/impact/scope/privilege/user interaction/business risk).
- **Phase 7 Quality Gate**: evidence review, reproducibility, FP confirmation, severity validation, root cause verification, documentation review, remediation validation, consistency check, final approval (ready/defer/reject).
- **Phase 8 Reporting**: executive summary, scope & methodology, finding documentation, evidence organization, risk assessment, remediation, security posture, report review, final packaging, delivery prep (bug bounty submission checklist).

### references/ (6 file — SESSION-DERIVED, paling kaya teknik konkret)

#### api_discovery_nosqli_express.md
- **5-layer API discovery pipeline**: (1) robots.txt Disallow = attack surface hints, (2) JS bundle analysis (hardcoded API paths, routes config, fetch relative paths, baseUrl; Next.js _buildManifest rewrite rules regex), (3) subdomain enum → separate API backend (api.target.com nginx/Express, cek /v1/ /v2/ /api/ /graphql), (4) Swagger/OpenAPI discovery paths (/docs, /docs/json, /api-docs, /swagger.json, /openapi.json, /v2/api-docs), (5) direct endpoint testing GET+POST.
- **NoSQLi fingerprinting via error taxonomy**: response table — "Permission denied" = sanitized; 500 ONLY untuk operator payloads ($ne, $regex, $gt, $exists, $where) = MongoDB operators reaching query layer; 500 for ALL inputs = no MongoDB. Key signal: string token → 403, object token → 500 = backend IS MongoDB + operators reach query.
- **Express/NestJS fingerprinting**: root GET / returns {"environment","mode","version"} = NestJS/Express; route pattern /{base}/{controller}/{action}.
- **Sails.js dev-mode detection**: SAILS_LOCALS._environment='development', /api/health, X-Server-IP 172.17.0.x Docker leak, blueprint API routes.
- **CORS assessment**: ACAO:* alone NOT vuln untuk token auth; CRITICAL hanya jika + Allow-Credentials:true atau cookie/session auth.
- **False positive guards**: marketplace/public listing endpoints intended public — cek field over-exposure + internal IDs untuk IDOR chain; sequential IDs bukan bug kecuali privileged endpoint pakai format sama.
- **Internal service (bot-api) checklist**: documented? real auth atau token field? operations (send email → spam, account/link → ATO)? enumerate tokens? NoSQLi? version info?

#### api_audit_patterns_obol_session.md
- **Filter-ignoring search endpoints**: spec says required filter, actual returns full DB. Detect: no-params Content-Length huge; bogus filter returns same total_count. Why: undefined req.query → {} matches everything. Look for: internal IDs, crypto material (BLS sigs, ENRs, pubkeys), pre-signed exits, withdrawal addresses.
- **NoSQLi via Express qs parsing**: `?partialAddress[$ne]=nope` → MongoDB operator. Try $gt/$regex/$where; parameter names: id, address, name, email, filter, query, search, where, partialX, q. **Cloudflare WAF gap: blocks SQLi text patterns, NOT MongoDB operators.**
- **Auth contract violations (500 instead of 401)**: missing/malformed/valid-format token → 500 = auth guard broken/skipped. Jangan claim "auth bypass" tanpa bukti lanjut.
- **Disambiguating bypass vs by-design**: test dengan real input format (ENR) — kalau response berubah ke "Authentication verification failed", auth di-enforce di code path lain; test 2 shape-valid tokens (signature-based vs presence-based); test validation order (invalid shareIdx 0 vs valid 1 dengan garbage bearer).
- **Cloudflare WAF coverage map**: SQLi classic blocked; NoSQLi operators NOT; SSTI {{7*7}} NOT; path traversal sometimes; semicolon param pollution NOT. Always test WAF gap directly.
- **Swagger spec = recon map**: swagger-ui-init.js → extract all paths regex → per-endpoint params/security/responses; absence of 401/403 in spec = signal.
- **False-positive checklist registry APIs**: public on-chain identity, merkle proofs (harus public), badges/tiers, public directory = NOT vuln. Vuln = full DB no filter, secret material bukan on-chain state, internal IDs enabling enumeration.
- **Cross-account lookup ≠ IDOR** (Lido fee splitter pattern by-design).

#### api_audit_patterns_circle_session.md
- **401/404 differential untuk endpoint enum**: sweep paths — 401 = real endpoint behind auth wall, 404 = decorative. Why: auth check runs BEFORE routing check. Bonus: /v1/balances/1 → 404 vs /v1/payments/1 → 401 tells collection-only vs per-resource. **Highest-yield recon move untuk walled REST API.**
- **Verbose error leaks API key format**: malformed token → full format spec (separator, lengths, charset, version "after May 2023"). Format oracle: valid-format wrong-secret → "Invalid credentials" vs wrong-format → verbose error = binary oracle (timing-based key recovery potential).
- **GraphQL field-probing bypasses introspection:disabled**: brute force field names — anything not "Cannot query field" exists; arg discovery; required input fields via `mutation{createAccount(input:{})}` multi-error; enum constraint confirmation. Techniques yang TIDAK work: aliases, @skip/@include, subscription root, query batching, APQ.
- **Next.js _buildManifest.js = full route map**: 1 GET → 100+ routes (deep links, admin flows, token routes). Bonus: __rewrites, middleware matchers, i18n routing.
- **security.txt fallback SPA page**: well-known paths return full 404 SPA HTML with i18n JSON (password rules, MFA factors, KYC codes, GraphQL error map, internal flow names). Check: any well-known path >50KB = SPA fallback.
- **Auth-first vs validation-first disambiguation**: 500 on valid-shape arg = resolver runs then auth fails (arg exists, format confirmed); 401 = auth before resolver; 200 = real bypass; 400 = validation rejects shape.
- **JS bundle as schema documentation**: grep operation names per chunk; minified → cari error messages/strings yang tidak di-minify.
- **Source map leak check**: `//# sourceMappingURL=...js.map` → .map public = auto-High (CWE-540). Full GraphQL ops, env names, dependency versions.
- **CORS + bearer nuance**: ACAO:* tanpa credentials ≠ exploitable; exploitable jika cookie auth atau credentials:true.
- **WAF encoding gap**: blocked `1'` → try `1%27`, `1%2527`, `1''`, `\u0027`. At least one slips.
- **Recon script composite** untuk Next.js + Apollo walled target (buildId → route map → 401/404 sweep → graphql probe → field-probe → verbose errors).
- **Limitations honesty**: unauthenticated audit = submit recon report + request test account (pattern untuk target ber-auth).

#### api_audit_patterns_rolly_session.md (no-KYC casino — business logic)
- **First-move: budget discipline** — download everything, grep everything, THEN form hypotheses (batch curl, filter CSS chunks, high-value greps sekali jalan: emit(, getReferral, commissionRate, fetch, ?r=, regex literals).
- **Gitbook .md export = schema**: append .md ke URL docs, llms.txt lists all pages → exact bonus formulas, eligibility thresholds, house edges, expiration mechanics. Cross-reference formula bugs: rounding direction, currency precision, per-bet vs cumulative cap, bp vs percentage.
- **Referral code squatting**: user-chosen code dengan only character-class regex → squat admin/vip/support; server uniqueness wajib; first-user-wins permanent.
- **Socket.io event surface = state machine map**: grep `emit("...")` dari bundles → tiap event = server endpoint; referral.create/edit/withdraw, pointsMining.activateDailyBoost/WagerBoost, profile.updateSettings (mass-assignment candidate).
- **?r= attribution race**: attribution timing (cookie-write vs signup vs first deposit vs first bet); self-attribution farming (n accounts × min bet → n× commission); first-bet gate tidak menyelamatkan (1-cent qualifying bet); cost-benefit: $2 cost → $200 commission = 20,000x ROI.
- **VIP game gating**: list endpoint flags tapi tidak filter; init endpoint enforce client-side → low-tier user bisa start VIP game; probe demo link public.
- **Boost activation race**: activate before earning qualifier; 100 emits dalam 100ms → stack (different workers before lock); "you choose when to activate" doc language hints race.
- **Rakeback rounding/off-by-one**: float vs integer math, basis point vs percentage, cumulative re-rounding, claim threshold $1.999 → $2 floor.
- **Unauth socket leak (Critical pattern)**: per-handler auth default-allow — satu event tanpa check (gamelist.getMainHistory) leak user._id, isVip, isHidden, amount, txHash (join key ke on-chain = deanonymization). Fix: single io.use() middleware + project user object + strip txHash. **Probe whole event surface: beberapa events auth-gated, beberapa tidak.**
- **Welcome bonus time-bomb**: "half instant / half daily-drop, don't accumulate" — cek drop table reused vs new per bonus.
- **Default vs custom campaign collision**: user-chosen code vs server-generated default; uniqueness hanya per-user → same code across users → attribution non-deterministic.
- **Open questions table**: tiap baris = 1 socket emit + 1 boolean answer, ~5 menit test, $5 capital — "confirm/close" pair per question (reusable test table pattern).
- **Bug bounty program constraint strategy**: cap rendah → submit static analysis Medium + request test account; jangan buang 4 jam untuk 5 Small bugs.

#### sap_occ_anonymous_cart_authz.md (SAP Commerce OCC/Spartacus)
- **Fingerprints**: Angular/Spartacus storefront, OCC base /api/v2/{baseSiteId}, basesites?fields=FULL multi-brand map, configurations/group public config (Adyen client key), openid-configuration CDN host, occ-personalization-id header.
- **Recon saat IP DC diblokir**: jangan thrash root api.*, buka storefront di stealth Chromium, capture network (cart create, search, config, OAuth), extract /api/v2/ paths dari JS chunks, rate-limit compliance.
- **Anonymous cart capability-URL matrix**: POST users/anonymous/carts → {guid, code}; GUID = capability URL — semua operasi (entries, email, addresses, deliverymode, paymentdetails, vouchers, orders) authz hanya by GUID knowledge.
- **Authz tests wajib**: cross-session read (credentials:omit + victim GUID), write IDOR, billing IDOR, paymentdetails IDOR (masked PAN + holder + expiry), delete IDOR, guest placeOrder authz (400 validation ≠ 401 = same capability model), numeric code as id, price manipulation (server ignores), cross-brand GUID.
- **PlaceOrder + delivery-slot chain**: authz vs validation (PlaceOrderCartValidationError bukan access control), T&C often SPA-only (setTermsAccepted di NgRx, tidak hit OCC), slots path pattern JS-mined, slot list may need verified address, jangan claim free paid goods tanpa Adyen capture success.
- **PII surface**: guest email di user.uid, paymentInfo masked PAN (full PAN echo = higher sev), RUM/analytics GUID leak = secondary-leak narrative only.
- **Severity/triage**: UUID v4 GUID → Medium tanpa leak chain; fold paymentInfo/billing/paymentmode ke SATU report (same root cause); guest placeOrder = severity amplifier bukan standalone.
- **Usually NOT findings**: Adyen live_ client key, OIDC host fingerprint, WP username list (OOS), client-side price fields, Datadog RUM public key alone, guessed voucher codes, cross-brand cart isolation.
- **Next-chain**: GUID leak primitive (XSS/postMessage/third-party/referrer/RUM), paymentdetails+paymentInfo same GUID, placeOrder bypass → order read IDOR, authenticated /users/current/orders IDOR, coupon race, mobile APK OAuth secrets.
- **Minimal PoC skeleton** (victim/attacker fetch pairs) — reusable template.

#### vdp_code_audit_patterns_nym_session.md
- **Policy-first workflow**: capture safe-testing rules sebelum probing (no DoS, no other users' data, production testing only with own account); prefer local code audit + local reproduction untuk broad VDP; record eligible/ineligible classes verbatim.
- **Candidate triage**: shared bearer-token ≠ auth bypass (cross-principal hanya jika 1 token holder bisa affect others/forge data); agent assignment tables yang hanya store node_id/started_at = red flag; async credential APIs — bedakan service-wide bearer vs per-user ownership; logging auth tokens = sensitive-leak smell (butuh production debug logging utk bounty-grade); javascript: links = weak XSS kecuali upstream data attacker-controlled.
- **Evidence checklist report-grade**: ≥1 LoC untuk authorization decision + 1 LoC untuk state mutation; preconditions (siapa punya token/role, trusted vs semi-trusted); impact konkret; local PoC preferred (start service, seed DB, forged request, read back state).

### Orchestrator/Decision/Memory/Reporting (44 file — SEMUA stub 140-250 bytes, struktur: Purpose/Inputs/Outputs atau Purpose/Decision Logic)
Pola arsitektur (bukan teknik rinci):
- **orchestrator-core/**: Orchestrator (init → select phase → dispatch playbooks → track → finalize), Module_Router (Target Type → Workflow Phase → Relevant Packs), Workflow_Controller, Context_Manager, Knowledge_Loader, Finding_Correlator (root-cause grouping, exploit-chain detection, impact correlation), Report_Generator.
- **decision-engine/**: Target_Classifier, Technology_Profiler, Strategy_Selector, Execution_Planner, Adaptive_Planner (increase focus on related surfaces when validated evidence accumulates), Decision_Rules, Confidence_Scoring, Risk_Prioritizer.
- **adaptive-reasoning/**: Reasoning_Engine (synthesize evidence → decisions), Hypothesis_Manager, Attack_Path_Builder, Correlation_Engine, Confidence_Updater, Priority_Optimizer, Adaptive_Router, Feedback_Loop.
- **memory-state/**: Session_Memory, Context_Compression (summarize completed phases, retain unresolved items verbatim), Checkpoint_Manager, Knowledge_Cache, Evidence_Store, Finding_Repository, Assessment_State_Manager, Resume_Engine.
- **reporting-quality/**: Severity_Normalizer (business impact, exploitability, confidence, scope), Finding_Deduplicator, Evidence_Validator, Report_Assembler, Executive_Summary, Remediation_Engine, Quality_Gate_Automation, Assessment_Packager.

### Pattern files (phase1-4, exploit-kb-1..5, playbook-*) — format seragam
- **Format pattern**: Overview → Root Cause / Recon Indicators → Discovery Strategy → AI Reasoning Checklist (3 pertanyaan) → False Positive Indicators → Business Impact → Related (CWE/OWASP).
- **Format playbook**: Objective → Workflow (3-5 langkah) → Evidence → Related.
- **Format exploit-knowledge**: Overview → Recon Signals → Validation Strategy → Business Impact → Related.
- Format exploit-chain: Scenario → Preconditions → Chain Logic → Validation Strategy → Business Impact.
- Coverage: 42 pattern (IDOR/BOLA/BFLA, broken auth, JWT, session, SQLi/SSTI/command inj, mass assignment, XXE, SSRF, CORS/CSRF, XSS/DOM-XSS, clickjacking, WebSocket, crypto, DoS, info disclosure, debug exposure, workflow bypass, cloud misconfig) + 44 exploit KB (termasuk chains: IDOR→PrivEsc, SSRF→Cloud, payment abuse, account recovery abuse, impact correlation, root-cause correlation) + 43 playbooks (core: recon/API/injection/authz/auth; vuln: RCE/deserialization/path traversal/file upload/SSRF/XSS/CSRF/XXE; modern: SPA/microservices/event-driven/API gateway/WebSocket/GraphQL/JWT/OAuth; cloud: AWS/Azure/GCP/IAM/secrets/CI-CD/Docker/K8s/reverse proxy).
- High-impact bug patterns (dari exploit-kb-5): IDOR+BOLA, SSRF+Cloud Metadata, File Upload+RCE, XSS+CSRF, Weak JWT+PrivEsc — fokus reasoning bukan signatures.
- Multi-step attack planning: Recon → Validation → Pivot → Escalation → Impact; avoid assuming exploitability without evidence.

---

## 4. drills/ (2 file — pointer, bukan isi)

### README.md + LOCATION.md
- Drills adalah pointer ke `tools/security/drills/` (tidak ada di folder ini).
- Kategori: Core Drills Python 40+ (omega, cosmic, dimension, infinity, nirvana, horizon, zenith, quantum, apex, immortal, mythic, absolute, eternity, singularity, transcendent scanner), Web3-Ethers Python (kiln_validation.py), Ethers.js Native JS (master1, deep2-5, expert1, grandmaster1-2, transcendent).
- Makna: latihan drill bertingkat (nama kosmik = level) untuk keahlian DeFi security.

---

## RINGKASAN TEKNIK PALING REUSABLE (cross-framework)

1. **Attack chaining core**: postcondition→precondition composition, capability graph, 8-dimensi scoring + mandatory caps, counter-evidence search, minimal chain, verifier handoff. Berlaku web2 & web3.
2. **Attack surface mapper**: evidence-backed map, trust boundary enumeration, invariant-first, hunter hypotheses.
3. **Capability taxonomy + chain matrix**: label standar + primitive→precondition→proof table = template untuk framework lain.
4. **Audit pipeline 3-layer**: automated (slither/mythril/echidna/medusa/halmos) → manual 4-pass (architecture, function, cross-function, dependencies) → economic modeling (10 skenario). + formal verification (Halmos prove, Echidna break).
5. **Red flags instant deep-dive list** (15 item) + audit checklist 25 attack patterns + "What Would Break" questions.
6. **Bytecode verification workflow**: source-vs-bytecode, storage layout, selectors, EIP-1967, guard decode — untuk deployed contracts.
7. **Session-derived API audit recipes**: 401/404 differential, NoSQLi error taxonomy, GraphQL field-probing, buildManifest route dump, verbose error format oracle, filter-ignoring endpoints, per-handler auth default-allow trap, attribution/boost races, WAF encoding gaps.
8. **False-positive discipline**: disambiguate bypass vs by-design (input format testing, validation order), public-data checklist, cross-account lookup ≠ IDOR, intended-public endpoints.
9. **Reporting**: evidence LoC + impact concrete + local PoC; severity justification; dedupe same-root-cause; contrast table vs known issues; verified on-chain.
10. **Economic discipline**: TVL ≠ loss tanpa executable path; profitability setelah gas+capital; recoverable vs irreversible; griefing vs profit.
