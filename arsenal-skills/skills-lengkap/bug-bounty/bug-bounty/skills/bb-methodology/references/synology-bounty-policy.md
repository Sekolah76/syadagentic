# Synology bounty policy — session reference

Source: `https://www.synology.com/en-uk/security/bounty_program`

## Confirmed policy points

- Product scope only: Synology products and web services.
- Operating systems: DSM, SRM, BeeStation; reward ceiling shown: **US$30,000**.
- Software and C2 cloud services: Synology-developed packages, related mobile apps, C2 cloud services; ceiling: **US$10,000**.
- Web services: major Synology web services; ceiling: **US$5,000**.
- Paid reports must be first valid report of a previously unknown/unpublished vulnerability.
- Issue must be verifiable, replicable, and demonstrate practical security impact on customer data, devices, or services.
- Report requires a detailed reproducible PoC, concise description, contact form submission, and encryption with Synology's published PGP key.
- FAQ states researchers should not disclose relevant information to third parties before resolution.
- Reports are reviewed by Synology Security Team.

## Operational decision rule

Maximum reward is not reachable ROI. Require at least one of: researcher-owned NAS/router, firmware/package artifact, Synology account with usable C2/app surface, or clearly in-scope web-service feature. Public `synology.com` marketing pages alone are a short manual triage, not a product-security campaign.

## Browser/localization pitfall

The UK URL displayed a localization prompt and stale accessibility refs after switching between `Scope & Rewards`, `FAQ`, and `Acknowledgment`. The live DOM still exposed authoritative links:

- Contact form: `https://synoform.synology.com/form/bounty?from_url=https://www.synology.com/security/bounty_program`
- PGP key: `https://www.synology.com/en-uk/support/security_pgp_key`
- Advisory: `https://www.synology.com/en-uk/security/advisory`

When refs fail, inspect current DOM links rather than retrying stale refs. Do not submit the contact form during reconnaissance.

## Exclusions for future work

Do not infer exact severity/reward tiers from the ceiling figures. Confirm the current reward details UI before reporting. Do not test third-party infrastructure, real customer data, destructive actions, brute force, DoS, or out-of-scope public properties.
