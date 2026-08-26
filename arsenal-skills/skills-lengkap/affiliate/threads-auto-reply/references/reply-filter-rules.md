# Reply Filter Rules (SYADAGENTIC Directive 2026-06-11)

## MUA Filter
- **Rule:** Skip posts containing "MUA" or "makeup artist"
- **Implementation:** `re.search(r'\b(MUA|makeup\s*artist)\b', body, re.IGNORECASE)`
- **Why word boundary:** Substring match `"mua" in body.lower()` matches "semua", "kemua" etc. — false positives.
- **Verified:** 3 test runs, zero false positives on Indonesian text with "semua"

## Shopee Link Filter
- **Rule:** Skip posts where ORIGINAL POST has shopee link
- **OK:** Shopee link in COMMENTS from other users (not post creator)
- **Implementation:** Extract first post container text only, check for `s.shopee.co.id`
- **Why post-only:** Old logic checked entire page body including comments. Posts where other affiliates already replied were incorrectly skipped.
- **Selector:** `document.querySelectorAll('[data-pressable-container="true"]')[0].innerText` (original post)
- **Fallback:** First 1000 chars of body text

## Keyword Prioritization
**Priority 1 (men's skincare — fresh, low saturation):**
- `skincare cowok`
- `bodycare bapak`
- `perawatan pria`
- `skincare laki laki`
- `rekomendasi skincare bapak`
- `skincare pria murah`

**Priority 2 (general — may be saturated):**
- `rekomendasi skincare` — HEAVILY SATURATED
- `jerawat`
- `rekomendasi makeup` — HEAVILY SATURATED
- `parfum enak` — DEGRADED
- `sunscreen terbaik`

## Config Sync
- Script `REPLIES_TARGET = 1` MUST match skill doc safety limit
- Cron interval: `every 2h`
- When reducing safety limit, update BOTH: skill doc AND script constant
