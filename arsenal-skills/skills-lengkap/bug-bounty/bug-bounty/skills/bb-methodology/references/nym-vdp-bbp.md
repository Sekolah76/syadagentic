# Nym VDP + Bug Bounty (class notes)

## Program channel (verify live)

| Item | Value |
|------|--------|
| Policy | https://nym.com/vdp-bbp |
| Report | `security@nym.com` (PGP preferred; FAQ may also mention support@ — prefer security@) |
| Immunefi slug | Often **404** — do not assume Immunefi host page |
| Payouts (indicative NYM tokens) | Critical ~$10k · High ~$1k · Medium ~$200 · Low ~$50 |
| Critical language | Direct user **privacy** compromise, **VPN encryption bypass**, **account takeover** |

## Eligible (examples)

CSRF, XSS, code execution, SQLi, SSRF, privilege escalation, auth bypass, data leaks.

## Explicitly ineligible / OOS

Rate limiting · stack traces · **self-XSS** · MitM · **DoS** · cache poisoning · clickjacking · missing DNS · brute force · **third-party** services · vulns only in **past versions** · outdated browsers/OS · support (Zendesk) · social engineering / physical · destroy other users' data.

## Testing rules

- Production: **own account only**
- Or run own instance of open source
- First unique report only; Nym decides severity
- 60-day no public disclosure after ack without coordination
- PoC required; scripts as non-executable attachments

## High-value surfaces (repo `github.com/nymtech/nym`)

1. **nym-wallet** (Tauri desktop) — funds/mnemonic/IPC
2. **NymVPN / clients** — privacy Crit language
3. **nym-credential-proxy** — ticketbook issuance (auth bearer)
4. **mixnet / gateway / nym-node**
5. **contracts/** — fund theft; lower privacy CVSS unless economic

## Wallet hardening notes (do not overclaim)

| Observation | Ship? |
|-------------|--------|
| CSP `script-src` has `'unsafe-inline'` + `'unsafe-eval'` | **Hardening debt only** until XSS sink proven |
| React/MUI text render (no `dangerouslySetInnerHTML`) | Default escape → moniker XSS chain often **dead** |
| Tauri v2 `capabilities` + custom `#[tauri::command]` | Custom IPC not gated by plugin allow-list the same way; still need **injection + unlocked session** for fund theft narrative |
| `send` / `sign` without re-password after unlock | **Session model**, not alone a bug |
| `show_mnemonic_*` requires password | Expected |
| `open_url` http(s) only | Hardened — reject file/js schemes |
| Updater signed artifacts on nymtech.net `.wellknown` | Integrity surface — check signature path before claiming |

Verifier pattern (Opus etc.): CSP finding without sink → `NEEDS_MORE_EVIDENCE` / reject standalone. Dig render path + IPC args before any High/Critical wallet claim.

## Credential-proxy class

- Migrations: unique index on `(credential_id, device_id)` may be **dropped** after recreate → async `obtain-async` replay / duplicate pending rows.
- Ticketbook routes sit behind **Bearer** `NYM_CREDENTIAL_PROXY_AUTH_TOKEN` — schema-only PoC is valid for code bug; impact needs auth + deposit/ticket economics for higher tiers.
- De-dupe: check local `nym-credential-proxy-duplicate-issuance-report.md` / PGP packages before re-emailing.

## NymVPN native-client classes

- Mixed DNS answers are a high-signal privacy boundary: inspect whether one `any(excluded)` decision is applied to the full unfiltered address vector.
- Unit route classification is not enough. Use the real proxy plus isolated tunnel/direct network namespaces and the product's actual Linux fwmark; require listener evidence showing the same non-excluded endpoint switches from tunnel (control) to direct (PoC).
- Audit the **distributed installer asset**, not only repository source. Raw installer paths that assign caller ownership to `/usr/bin/nym-vpnd` or adjacent helpers can create root execution when systemd/daemon later launches them.
- Shared `nym-vpnd` RPC leads involving another local user's mnemonic or PID require a disposable two-user Polkit runtime proof before reporting; successful `auth_self` is authentication, not resource authorization.
- Full reusable workflow: `references/native-client-privacy-and-installer-validation.md`.

## Session start checklist for Nym

1. Write `/home/ubuntu/recon/nym/SCOPE_FENCE.md` from live vdp-bbp
2. Inventory prior reports on disk
3. Define goal (privacy / ATO / funds)
4. Select 1–2 classes; kill self-XSS / DoS / CSP-only early
