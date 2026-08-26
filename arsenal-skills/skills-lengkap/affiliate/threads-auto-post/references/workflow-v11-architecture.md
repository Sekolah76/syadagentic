# Threads Post Workflow v11+ Architecture

This reference outlines the advanced pipeline for the `threads-auto-post` cron job, specifically focusing on database management and WAF-bypassing image extraction.

## 1. Database Auto-Reset (Batch Recycling)
The script relies on `affiliate-link-database.md`. When the script detects `0` remaining `❌ UNUSED` links, it automatically recycles the database:
- Replaces all `✅ USED` markers with `❌ UNUSED`.
- Reloads the pool and continues posting.
- Ensures the cron job never crashes due to an empty pool.

## 2. Three-Tier Image Scraping Pipeline
To ensure high-quality, authentic "real user" review photos (anti-slop) for the posts, the pipeline uses a 3-tier fallback system:

### Tier 1: Shopee Direct (via Camoufox CDP Bypass)
Shopee protects its review endpoints (`/api/v4/item/get_ratings`) with aggressive Akamai Bot Manager rules that block `curl_cffi` and standard Playwright.
- **Method**: Use `camoufox` CLI to launch a local Chrome profile (`chrome_local_...`) in `--headed` mode.
- **Trigger Lazy Load**: Scroll to `.product-ratings`.
- **Extraction**: Review images on Shopee Desktop are NOT in `<img>` tags; they are in `div` `background-image` styles hosted on `susercontent.com`.
- **Quality**: The URLs ending in `_cover` are kept as they provide good quality (~60-75KB). Removing `_cover` often results in a `404 Not Found` on the new `down-*.img.susercontent.com` domains.

### Tier 2: Pinterest HQ (Primary Fallback)
If Tier 1 fails, Pinterest provides excellent user-generated content without WAF blocks.
- **Queries**: specific non-catalog searches like `"{product} swatches bibir"`, `"{product} di tangan review"`, `"{product} pemakaian"`, `"{product} review asli"`.
- **Filtering**: Skip the first 4 images (index 0-3) as they are typically catalog/studio shots. Pick from index 4-8.
- **Upscaling**: Replace `/236x/` with `/736x/` in the `i.pinimg.com` URL to get High Quality images.

### Tier 3: Bing Image Search (Last Resort)
Queries Bing for `site:cf.shopee.co.id/file {product} review`.
- Extracts `murl` from the `m` attribute of `a.iusc` nodes.
- Prone to SafeSearch DNS hijacking in some regions, hence it is the last resort.

## 3. Image Scoring (Vision Validation)
When extracting multiple candidate review images, the system uses Vision models to score them based on authenticity:
- **High Score (9-10)**: Real skin swatches, held in hand, messy/used product (shows authenticity), comparison of shades.
- **Low Score (<5)**: Closed boxes, catalog/studio shots, completely irrelevant backgrounds (e.g., messy laundry), overly aesthetic setups.