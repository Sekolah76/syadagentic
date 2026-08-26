# Image Generation Prompt Template — Realistic iPhone Style
# Model: nb/nanobanana-pro via 9Router (fallback: Pollinations.ai, FAL)
# Generated images go to /tmp/threads_post_image.png for Playwright upload
# ⚠️ ALL PROVIDERS EXHAUSTED as of 2026-06-03 — text-only fallback until credits reset

## Provider Status (2026-06-03)
| Provider | Status | Error |
|---|---|---|
| FAL | ❌ Balance exhausted | Top up at fal.ai/dashboard |
| nanobanana-pro | ❌ Credits insufficient | Top up in 9Router dashboard |
| nanobanana-flash | ❌ Credits insufficient | Same pool as nanobanana-pro |
| Pollinations.ai | ⚠️ Rate limited | "Queue full for IP" — wait hours |
| FreeModel.dev | ❌ No image gen | Text/chat only |
| mimo (all) | ❌ Text only | Cannot generate images |

**Fallback:** When all providers down, post text-only. Script handles gracefully (no crash).

## CORE PRINCIPLE
"UGLY = REALISTIC" — Semakin "imperfect" prompt → semakin natural hasilnya.
JANGAN pakai: "beautiful", "perfect", "professional", "aesthetic", "clean".
PAKAI: "messy", "unfiltered", "raw", "candid", "slightly blurry", "dust", "tilted".

## Realism Tiers (observed 2026-06-03)
| Prompt style | Realism | When to use |
|---|---|---|
| "Clean aesthetic flatlay" (old) | 5-6/10 | ❌ Don't — obviously AI |
| Warm golden-hour lifestyle | 6/10 | ❌ Don't — too staged |
| "Ugly real" + messy + harsh light | 7-8/10 | ✅ Default — most convincing |
| Specific phone + artifacts + mundane | 8/10 | ✅ Best — for high-effort posts |

## PROMPT FORMULA
1. Specify phone model (iPhone 15 Pro, Samsung BOZaxy S24) — sets camera character
2. Describe mess/imperfection (cluttered, crumpled, scattered, stained)
3. Use bad lighting (harsh fluorescent, overexposed, underexposed shadows)
4. Add camera artifacts (compression artifacts, chromatic aberration, slight motion blur)
5. Emphasize NOT (NOT aesthetic, NOT professional, NOT staged)
6. Describe mundane context (quick photo to send to friend on WhatsApp)

## PROMPT TEMPLATES

### 1. Nightstand / Bedroom
```
iPhone 15 Pro photo of a white skincare pump bottle on messy wooden nightstand,
slightly tilted angle, warm bedroom lamp light, phone charger tangled nearby,
dust particles visible on surface, slight motion blur from hand shake,
iPhone portrait mode bokeh on background, unfiltered raw photo,
authentic candid moment, no editing no color grading
```

### 2. Bathroom Counter
```
Raw iPhone camera photo of white skincare bottle on bathroom counter
next to toothbrush and soap dispenser, morning natural light from small window,
slightly foggy mirror in background, water droplets on counter,
messy toiletries scattered, taken from above at slight angle,
warm humid bathroom atmosphere, imperfect composition
```

### 3. Desk / Study
```
Casual iPhone photo of white cream bottle on cluttered desk with
laptop keyboard partially visible, natural daylight from window casting
harsh direct shadows, slightly blurry focus, visible screen glare,
random items like earbuds case and crumpled receipt,
iPhone barrel distortion, no color grading, authentic student desk,
slightly grainy in darker areas
```

### 4. Floor / Bag Dump
```
Top-down iPhone photo of white skincare bottle on carpet floor
next to open tote bag and scattered items, overhead room light,
slightly off-center composition, visible carpet texture,
casual "just got home and dumped my bag" vibe, unfiltered raw shot
```

### 5. Kitchen / Table
```
iPhone photo of white skincare bottle on kitchen table with
coffee mug and phone lying face down, morning window light,
slightly overexposed from direct sunlight, everyday kitchen reality,
no styling no props arranged, candid quick snapshot, authentic
```

### 6. Rumah Makan Padang (Indonesian food)
```
Realistic casual iPhone photo of a young Indonesian man in t-shirt
sitting at a crowded Padang restaurant, eating nasi padang with rendang
sayur nangka sambal on banana leaf, warm afternoon natural light
from open storefront, authentic everyday moment, candid natural shot,
unfiltered raw photo, NOT professional photography
```

## ANTI-PATTERNS (jangan pakai ini)
❌ "beautiful product photography"
❌ "professional lighting"
❌ "studio shot"
❌ "clean white background"
❌ "perfect composition"
❌ "aesthetic flat lay"

## REQUIRED KEYWORDS (min 3 per prompt)
messy, candid, raw, unfiltered, tilted, blur, dust,
harsh shadow, grain, unedited, authentic, everyday,
iPhone camera, slight motion, imperfect

## POSTING FLOW
1. Cron agent picks random template (1-6)
2. Adds product-specific context
3. Generate via `image_generate` tool (FAL)
4. Fallback: nanobanana-pro → Pollinations.ai
5. Save to `/tmp/threads_post_image.png`
6. Pass to threads_post_v6.py via JSON `image_path` field
7. If ALL providers fail → post text-only (script handles gracefully)
