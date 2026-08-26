# Hermes + SYADAGENTIC — Hallmark install & routing

Installed 2026-07-18 from upstream `Nutlope/hallmark` (skills/hallmark tree only — not the demo `site/`).

## Paths

| Item | Path |
| --- | --- |
| Skill root | `~/.hermes/skills/web-dev/hallmark/` |
| SKILL.md | `web-dev/hallmark/SKILL.md` (Hermes frontmatter + adapter note) |
| References | `web-dev/hallmark/references/` (~100 files) |
| Compact sibling | `web-dev/anti-ai-slop-design/` (SYADAGENTIC defaults, not a full fork) |

## Re-install / update

```bash
TMP=/tmp/hallmark_install
rm -rf "$TMP" && mkdir -p "$TMP" && cd "$TMP"
curl -sL "https://codeload.github.com/Nutlope/hallmark/tar.gz/refs/heads/main" -o hallmark.tgz
tar -xzf hallmark.tgz
DEST="$HOME/.hermes/skills/web-dev/hallmark"
rm -rf "$DEST" && mkdir -p "$DEST"
cp -R hallmark-main/skills/hallmark/SKILL.md hallmark-main/skills/hallmark/references "$DEST/"
# Re-apply Hermes frontmatter + adapter block at top of SKILL.md (see live SKILL.md head)
rm -rf "$TMP"
# Verify
find "$DEST" -type f | wc -l   # expect ~106
du -sh "$DEST"                 # ~932K
```

Do **not** copy `site/`, screenshots, or demo HTML into the skill dir — bloat only.

## Dual-stack routing

| Brief | Skill |
| --- | --- |
| SYADAGENTIC portfolio / crypto / streaming / local-biz single-file (first ship, no slop complaint) | `anti-ai-slop-design` → `vercel-single-file-site` |
| Full anti-slop Design flow, 58 gates, themes, study/audit/redesign | `hallmark` |
| **Hub Brand / multi-domain index** | **`hallmark`** with rotation: Index-First → Manifesto → Catalogue → **Split Studio** (see escalation + `anti-ai-slop-design/references/hub-brand-offlcial.md`). Do **not** stop at compact anti-ai-slop + old brand-hub template |
| SYADAGENTIC says "AI SLOP" / "masih slop" / "jelek banget" after a ship | **Mandatory Hallmark redesign** — new macrostructure + new type pair. Recolor/token-swap of prior build = fail |
| Security before go-live | `website-security-hardening` |

Pipeline stamp: `hallmark|anti-ai-slop → BUILD → website-security-hardening → DEPLOY`.

### Redesign escalation (SYADAGENTIC frustration)

1. Read prior CSS stamp (`/* Hallmark · macrostructure: … */`). Next build **must differ** (gate 8 / anti-pattern default-attractor).
2. Brand hub after **first** rejection: **Index-First** industrial list — not Specimen, not SaaS hero+cards.
3. Brand hub after **second** rejection (Index-First already shipped and still "masih slop"): rotate off Index-First to **Manifesto** (or Letter / Catalogue). Verified 2026-07-18 offlcial: Index-First + Big Shoulders/Newsreader still rejected → Manifesto + **Anton + IBM Plex Sans** + N7/H1-marquee/Ft5 shipped.
4. Brand hub after **motion / "lebih profesional"** rejects (post-Manifesto OK then animation path fails): **do not stay on Manifesto+motion**. Verified offlcial ladder: CSS 3D → 2D toys (terminal/ticker/cart/wipe) → Unsplash **full-bleed** Ken Burns — all rejected.
5. **"lebih profesional"** = abandon the failed *technique class*, not retune timing/easing on the same trick. **Not** "better Ken Burns" and **not** CSS-3D-lite.
6. After type-only Catalogue (v7 Manrope/Source Serif, no photo) SYADAGENTIC still asked **"masukin gambar + motion"** → ship **Split Studio + framed supporting photos** + Hallmark motion (stagger / IO once / media clip-in / drift **inside** media frame only). Framed photos ≠ full-bleed page BG.
7. **Elegance-only retune:** if SYADAGENTIC says only "lebih elegan / ubah font dan warna" **without** slop/jelek → type+palette pass on current macro is allowed (v8 Syne/Figtree/harsh orange → v8.1 Cormorant Garamond + Libre Franklin + ivory/cognac). Do **not** invent a new macro for pure elegance.
8. **Type pair must rotate with macro** on slop rejects. Same face pair on a new layout still reads as the previous ship. Drop banned faces (Space Grotesk, DM Sans, Inter, Poppins as live `--font-*`) and any face named in the prior stamp. For "elegan": prefer Cormorant Garamond / Instrument Serif class + Libre Franklin / IBM Plex Sans — avoid industrial condensed (Anton / Big Shoulders) and loud geometric display (heavy Syne).
9. Nav/footer rotate too on slop rejects: leave N1a/Ft3 SaaS chrome; rotate N6 / N7 / N9 / Ft1 / Ft2 / Ft5 (never same nav+footer pair twice in a row on the same domain). Elegance-only retune may keep nav/footer.
10. When SYADAGENTIC says **"load semua skill design"** / "anti ai slop" after multi-reject: full Hallmark flow + `anti-ai-slop-design` + a11y + SEO + `website-security-hardening` — do not stop at compact anti-slop or partial Hallmark.
11. Redeploy **production** alias (`offlcial-hub.vercel.app` / project prod); delete local; verify **prod URL** with cache-bust `?v=` (not only ephemeral `*.vercel.app` — those can 401 Login). Live HTML must contain **new** stamp + **new** font family query params (not only accent swap).
12. **Grep-validate carefully:** stamp comments often mention the *previous* rejected faces (`previous rejected: …`) and JS has `IntersectionObserver` — naive `assert 'Inter' not in html` / ban-list over whole file will false-fail. Check live `<link href=fonts…>` / `--font-display` only. Ban after failed classes: `preserve-3d`, full-page Ken Burns, toy widgets. Framed `images.unsplash.com` with filter/overlay + TODO swap is OK when SYADAGENTIC asked for gambar.
13. Live offlcial stamp + ladder always in `anti-ai-slop-design/references/hub-brand-offlcial.md` — **read before rebuild**.

## Domain pre-brief (before Hallmark Design flow)

When SYADAGENTIC names a domain for a new site:

1. Normalize spelling **once** if ambiguous — if SYADAGENTIC already asserts intentional spelling (e.g. `offlcial` double L), **lock it**. Never autocorrect brand domains in copy/title/canonical.
2. Probe live DNS (not whois alone):
   ```bash
   dig +short NS <domain>
   dig +short A <domain>
   dig +short AAAA <domain>
   dig +short MX <domain>
   dig +short TXT <domain>
   curl -sI -m 8 "https://<domain>" | head -15
   ```
3. Report: empty A/AAAA = greenfield; CF NS only = ready for Vercel A/CNAME; existing site = redesign/study path.
4. Then concept pick (hub / product landing / affiliate / portfolio / docs) → Hallmark Audience/Use/Tone gate.
5. **Hub Brand** brief: hero statement + multi-domain index → manifesto + catalogue-index; template `vercel-single-file-site/templates/brand-hub-landing.html`. Probe each brand host for final URL after 307/308.

## Cloudflare token vs zone access

Env `CLOUDFLARE_API_KEY` can pass token verify yet list **zero zones**. Treat as scope problem → hand SYADAGENTIC exact DNS rows; do not claim domain missing. Vercel preview remains the ship URL until grey-cloud A/CNAME lands.

## X/tweet source for this skill

Public tweet fetch when agent X OAuth / jina blocked:

- Syndication: `https://cdn.syndication.twimg.com/tweet-result?id=<ID>&token=x`
- Fallback: `https://api.fxtwitter.com/<user>/status/<ID>` or `api.vxtwitter.com`

Hallmark card/thread used: satyaXBT parent + install reply linking github.com/nutlope/hallmark + usehallmark.com.

## Token discipline

Never load the whole `references/` tree. Index-then-pick: macrostructures.md → one macro file; component-cookbook → only chosen archetypes; slop-test.md only at Step 7.
