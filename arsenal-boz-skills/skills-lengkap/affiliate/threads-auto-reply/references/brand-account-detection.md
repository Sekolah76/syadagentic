# Brand/Business Account Detection Patterns

## Why Skip Brand Accounts?
Brand accounts post product showcases for their OWN products. Commenting with a
competitor affiliate link looks like spam, not genuine engagement. It wastes the
reply and could trigger shadow bans.

## Detection Patterns

### Username Heuristics (check post author username)
Skip if the username matches any of these patterns:
- Known brand handles: `@hvm.fragrances`, `@somethinc`, `@wardah`, `@skintific`,
  `@avoskin`, `@somethinc.official`, `@ltpro`, `@makeover`, `@luxcrime`,
  `@scarlettwhitening`, `@emina.cosmetics`, `@pipikimia`, `@sociolla`,
  `@florenceby`, `@minimalist`, `@theordinary`, `@cerave.indonesia`
- Brand words in handle: `.official`, `.id`, `.co`, `_shop`, `_store`, `beauty_`,
  `cosmetic_`, `skincare_`, `brand_`
- Verified badge + product showcase content

### Content Heuristics (check post text)
Skip if the post reads like a product showcase:
- Contains "Launching" / "New!" / "Exclusive" / "Limited Edition"
- Contains product names followed by specs/ingredients listing
- Posts with multiple product images (carousels with product shots)
- Contains "Available at" / "Shop now" / "Link in bio" / "Order di..."
- Contains pricing info (RpXXXX, Rp XX.XXX, harga)

### Safe to Reply To (regular user posts)
- "Rekomendasi dong" / "Guys ada yang tau" / "Help me choose"
- "Gw pake ini dan..." (personal experience sharing)
- "Review jujur" / "Honest review"
- Curhat about skin/hair concerns
- Questions about product comparisons

## Implementation in Script
Add a `is_brand_post(username, post_text)` check BEFORE committing to a post:
```python
MY_USERNAME = "jagonya_shopee"  # NEVER skip our own account

BRAND_WORDS = ['official', '.id', '.co', '_shop', '_store', 'brand',
               'somethinc', 'wardah', 'skintific', 'avoskin', 'luxcrime',
               'emina', 'sociolla', 'cerave', 'scarlett', 'makeover']
BRAND_SKIP_SIGNALS = ['launching', 'new!', 'exclusive', 'limited edition', 'order di', 'link in bio']

def is_brand_post(username, post_text=''):
    username_lower = username.lower()
    # CRITICAL: Always exclude our own account first
    if username_lower == MY_USERNAME:
        return False
    if any(w in username_lower for w in BRAND_WORDS):
        return True
    text_lower = post_text.lower()
    if any(s in text_lower for s in BRAND_SKIP_SIGNALS):
        return True
    return False
```

## ⚠️ Pitfall: Don't match own username
`_shop` in `BRAND_WORDS` matches "jagonya_shopee" → false positive. Always
check `username == MY_USERNAME` BEFORE brand detection. The word "shop" in
our handle is NOT a brand indicator.
