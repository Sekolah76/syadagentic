# Report Templates

Referensi Fase 4 di `workflow.md`. Dua template: **email disclosure** (kontak awal) + **laporan teknis** (lampiran). Tersedia ID & EN. Sesuaikan nada, jangan filler.

---

## 1. Email disclosure — Bahasa Indonesia

```
Subject: [Security] Vulnerability disclosure — <projek/aset>

Halo tim <projek>,

Saya <nama/handle>, melakukan riset keamanan good-faith. Saya menemukan
kerentanan pada <aset: domain/kontrak/repo> dan ingin melaporkannya secara
privat agar bisa diperbaiki sebelum berpotensi disalahgunakan.

Ringkasan:
- Jenis: <mis. IDOR / reentrancy / auth bypass>
- Lokasi: <URL/endpoint/alamat kontrak/file>
- Dampak: <apa yang bisa dilakukan attacker + skala>

Saya sudah menyiapkan langkah reproduksi dan PoC minimal (non-destruktif).
Bila ada kanal aman (PGP/email security), saya kirim detail lengkapnya ke sana.

Saya mengikuti coordinated disclosure: tidak mempublikasikan apa pun sebelum
ada perbaikan atau kesepakatan timeline (default 90 hari; bisa dipercepat bila
mendesak). Tidak ada tuntutan/ancaman — tujuan saya membantu.

Mohon konfirmasi penerimaan dan kanal aman untuk detail teknis.

Terima kasih,
<nama/handle, kontak, PGP key ID bila ada>
```

## 1b. Email disclosure — English

```
Subject: [Security] Vulnerability disclosure — <project/asset>

Hi <project> team,

I'm <name/handle>, a good-faith security researcher. I found a vulnerability
in <asset: domain/contract/repo> and would like to report it privately so it
can be fixed before it could be abused.

Summary:
- Type: <e.g. IDOR / reentrancy / auth bypass>
- Location: <URL/endpoint/contract address/file>
- Impact: <what an attacker could do + scale>

I have reproduction steps and a minimal, non-destructive PoC ready. If you have
a secure channel (PGP/security email), I'll send full details there.

I follow coordinated disclosure: I won't publish anything before a fix or an
agreed timeline (default 90 days; sooner if urgent). No demands, no threats —
I just want to help.

Please confirm receipt and a secure channel for technical details.

Thanks,
<name/handle, contact, PGP key ID if any>
```

**Catatan:** kontak awal sengaja ringkas. Kirim detail teknis + PoC lengkap hanya setelah kanal aman dikonfirmasi, terutama untuk bug unpatched berdampak besar / dana at-risk.

---

## 2. Laporan teknis (lampiran)

```
# <Judul: kelas bug — lokasi singkat>

## Ringkasan
<2–3 kalimat: apa bug-nya + dampak>

## Aset terdampak
- Target: <domain/kontrak/repo + versi/commit/chain>
- Komponen: <endpoint/fungsi/file:line>

## Security boundary yang dilanggar
<siapa harusnya tidak bisa apa, tapi bisa — dan kenapa>

## Langkah reproduksi
1. <langkah persis>
2. <langkah persis>
PoC / payload:
<literal; untuk web3 sertakan skrip fork/simulasi, bukan exploit on-chain nyata>

## Bukti
- Log request/response / tx hash / screenshot
- Reproduksi: <n dari m percobaan>

## Impact
- Yang bisa dilakukan attacker:
- Skala: <single-user / semua user / seluruh protokol>
- Prasyarat: <privilege/interaksi yang dibutuhkan>

## Severity
<Critical/High/Medium/Low> — rasional: <kaitkan ke boundary, dampak, likelihood>
(web3: sebutkan dana at-risk & likelihood eksploitasi)

## Rekomendasi mitigasi
<fix di level akar: validasi input, akses kontrol, checks-effects-interactions,
rate limit, dsb — sesuai kelas bug>

## Disclosure
- Ditemukan lewat: <cara legit: repo publik / on-chain / testnet / in-scope>
- Timeline yang diusulkan: <mis. fix dalam 90 hari, publikasi setelah fix>
- Kredit: <nama/handle bila diinginkan>
```

Bahasa laporan ikut target (ID/EN). Untuk web3 dana at-risk: tegaskan urgensi, tawarkan bantuan, dan jangan publikasikan sebelum aman.
