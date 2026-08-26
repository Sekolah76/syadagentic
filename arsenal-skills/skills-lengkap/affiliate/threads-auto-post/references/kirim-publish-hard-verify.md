# Kirim / Publish Hard Verify (2026-07-12)

## Rule
**Kirim click ≠ success.** UI can click, React `onClick` can fire, editor can show 3-beat + link — and still **zero** GraphQL Create/Publish.

Mark history / DB `USED` **only** if:
1. Network POST has `fb_api_req_friendly_name` matching `Create|Publish|PostMedia|TextPost|Configure|Barcelona.*Create`, **or**
2. Profile `@jagonya_shopee` **inner_text** contains unique hook snip (≥24 chars) or product snip (≥8) or link tail — verified in a **fresh** navigation (not leftover composer draft / HTML shell false match).

If soft “verified” without mutation → treat as **fail** unless independent re-check confirms body has snip after scroll.

## False-success traps
| Trap | Why |
|------|-----|
| `has-text("Post").last` | Feed has many “Post”/repost nodes (count can be 12+) |
| Prefer Kirim at y≈114 | Top feed/composer chrome — often dead for publish |
| Profile `content()` HTML match alone | Huge SSR/HTML can false-hit; use `inner_text` + unique snip |
| Soft success after failed mutation | History pollution + wrong USED mark |

## Working send order (skill-proven + 2026-07-12)
1. Score Kirim/Post buttons: `(y>300?100:0)+(x>700?50:0)+(y>500?20:0)` — **require score≥100**
2. Mouse click bottom-right Kirim first
3. Fallback: `div[role=button]:has-text("Kirim").last.click(force=True)` — **Kirim before Post**
4. Never prioritize `has-text("Post").last` when any Kirim score≥100 exists
5. Optional: Meta+Enter after editor focus
6. Wait ≤20s for create mutation; retry Kirim.last + Meta+Enter once
7. Profile verify strict; on fail → exit 1, **no** history/USED

## Auth preflight (before live post)
- `ds_user_id == 3310347890` **and** `web_form_data` username == `jagonya_shopee`
- Wrong: olivia `46398254032` — SSO/onboarding/signup wall
- See `auth-preflight-jagonya.md`

## When UI publish is dead
If mutation stays 0 on headless **and** real Chrome CDP with same account:
- Not story/dedup/cookie-empty issue if preflight OK + composer types
- Manual 1 post in user Chrome P16 proves account can still publish
- Next path: GraphQL create / non-headless Camoufox — **only after** manual OK or SYADAGENTIC directs

## Revert on false success
If history/USED written without live post: remove Cultusia/link entry, keep DB `❌ UNUSED`.