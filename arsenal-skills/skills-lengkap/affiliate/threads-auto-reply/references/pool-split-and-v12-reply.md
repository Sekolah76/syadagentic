# Pool Split & Threads Auto-Reply v12 Upgrade

Knowledge and architecture notes from the session on 2026-07-13.

## 1. Multi-Pool Affiliate Database Isolation

To prevent fast exhaustion of the affiliate link database when multiple channels run concurrently, the database copies are **completely isolated**. 
Cross-sync logic is disabled (no auto-sync of USED/UNUSED flags between channels).

| Channel | Database Path | Used-set Tracker JSON |
| :---: | :--- | :--- |
| **Threads Post** | `~/.hermes/skills/affiliate/threads-auto-post/references/affiliate-link-database.md` | `threads_post_used_links.json` |
| **Threads Reply** | `~/.hermes/skills/affiliate/threads-auto-reply/references/affiliate-link-database.md` | `threads_reply_used_links.json` |
| **Pinterest** | `~/.hermes/skills/pinterest-auto-post/references/affiliate-link-database.md` | `pinterest_used_links.json` |

### Rules:
- **1 Action = 1 Link Affiliate Forever (No Recycle)**: Auto-reset or recycling of USED links back to UNUSED is disabled. Once a link is marked USED, it is permanently locked out using its channel's specific `used_links.json` tracker.
- **Independent Pool Operations**: A successful post on Threads Post does not mark that product as USED on Threads Reply or Pinterest.

---

## 2. Threads Auto-Reply v12 (Nimbrung / Sok Asik)

Transitioned from an "explicit recommendation request reply" only model to a general contextual engagement model (sok asik).

### A. Dual Funnel Search
1. **Reco Keywords (40% weight)**: Explicit requests (e.g., "rekomendasi skincare jerawat").
2. **Nimbrung Keywords (60% weight)**: General Gen-Z curhat/story/flex (e.g., "muka kusam bgt hari ini", "wangi seharian").

### B. Intent Classifier
Reads the target post text to classify into one of:
- `reco`: Need recommendation (Link: **ALWAYS ON**)
- `relate`: Curhat/empathy (Link: **SOFT ON, 50% chance**)
- `story`: Journey/before-after (Link: **SOFT ON, 45% chance**)
- `banter`: Casual flex/sok asik (Link: **OFF by default, 25% chance**)
- `light`: Fallback casual (Link: **OFF, 15% chance**)

### C. Link Ratio Rebalancer
Keeps the comment feed natural. Re-evaluates recent history to ensure **at least 50% of recent replies have no affiliate links**. If the link ratio goes high, non-reco intents are forced to link-off mode.

---

## 3. Shopee Buyer-Review HQ Scraper (camoufox headed)

To pull real user-review photos instead of sterile studio catalog renders:
1. **Headed open**: camoufox opens headed instance on Chrome Profile 16.
2. **Dynamic Scroll**: Scroll step-by-step 35-40 times to trigger React component mount for rating list.
3. **Filter**: Click "5 Bintang" filter and "Dengan Media" filter.
4. **i.src original**: Extract image source from `i.src` or `i.getAttribute('src')` instead of `currentSrc` (which resolves to `@resize_w144` 5KB thumbnail).
5. **HD upgrade**: Suffixes like `@resize_w144_nl.webp` and `_tn` are stripped to pull original high-resolution JPG from `susercontent.com`.
6. **Max Pixel Selector**: Sort candidates by resolution (`width * height`) and pick the highest resolution image as the winner.
