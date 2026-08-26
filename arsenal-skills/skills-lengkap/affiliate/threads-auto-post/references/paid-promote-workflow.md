# Paid Promote / Sponsored Content Workflow

## When to Use
User says: "paid promote", "sponsored post", "campaign brief", "klien minta post", "draft buat klien"

## Flow

### 1. Read Campaign Brief
- PDF → use `pymupdf` (`pip3 install pymupdf`): `pymupdf.open(path)[page].get_text()`
- Image → `vision_analyze` (if available) or ask user to describe contents
- Always extract: **NOTES WAJIB**, **CTA targets**, **client request**, **posting deadline**

### 2. Extract Requirements Checklist
From brief, identify ALL mandatory elements:
- Referral/affiliate links (check domain requirements, e.g. okx.ac vs okx.com)
- Telegram/community links
- Campaign URLs
- Download links
- In-app navigation paths
- Any specific wording to avoid (e.g. "financial advice", "guaranteed profit")

### 3. Draft Content
- **Ask user format preference first**: single post vs 3-post thread
- Single post = all info in 1 concise post (client briefs usually prefer this)
- 3-post thread = hook → value → CTA (for affiliate Shopee style)
- **Include ALL NOTES WAJIB elements** — missing even 1 = client rejects draft
- Match tone to brief style (formal vs casual)
- End with: "Mau langsung post, atau submit dulu ke klien buat approval?"

### 4. Post via Threads
- `threads_post_v6.py` works fine with non-Shopee links — no script changes needed
- Content JSON format same as regular posts
- `affiliate_link` field = primary CTA link from brief
- `image_path` = optional, generate via CF/Pollinations if not provided by client

## Pitfalls
- ⚠️ **Always check NOTES WAJIB section** — briefs hide critical CTAs there, not in the overview
- ⚠️ **Submit draft for approval FIRST** — most briefs say "Draft wajib submit terlebih dahulu untuk approval". Don't auto-post.
- ⚠️ **Multiple Telegram links** — briefs may list 2+ Telegram URLs (community + support). Include ALL of them.
- ⚠️ **Campaign URL may differ from referral URL** — e.g. `okx.ac/id/okx-outcomes-campaign-2026` (campaign) vs `okx.ac/join/39614109` (referral). Include both.
- ⚠️ **Domain restrictions** — some clients require specific domains (okx.ac not okx.com). Always check brief.
- ⚠️ **Non-Shopee paid promotes should NOT be tracked in affiliate-link-database.md** — separate tracking or no tracking needed.

## Verification Checklist (before sending draft)
- [ ] All referral/CTA links present
- [ ] All Telegram links present
- [ ] Download links present
- [ ] No restricted wording (financial advice, guarantees, etc.)
- [ ] Format matches user preference
- [ ] Draft submitted for approval before posting
