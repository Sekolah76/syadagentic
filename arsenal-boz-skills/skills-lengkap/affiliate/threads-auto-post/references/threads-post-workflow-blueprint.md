# Threads Auto-Post Workflow — v2.0 Blueprint

Full end-to-end pipeline for sharing with other AI agent operators.

## Architecture
3 core scripts: `cron_post.py` (orchestrator) → `threads_post_v6.py` (executor) → `affiliate-link-database.md` (data)

## Pipeline (8 Steps)
1. **Load DB + History** — Parse markdown table, load history JSON
2. **Category Rotation** — 4 categories (skincare/makeup/parfum/haircare), pick NOT in last 4
3. **Hook Generation** — 6 archetypes per category, rotate, skip word overlap >50%
4. **Content Assembly** — 3-post thread: hook → review/story → CTA+save+link
5. **Real Photo Scraping** — Shopee DOM (attempt) → Pinterest PRIMARY → Bing LAST RESORT
6. **Threads Login** — Cookie injection → Meta SSO → "Continue with Instagram"
7. **Posting** — Type + clipboard paste + image upload + send
8. **Dedup & History** — Link, hook category, word overlap checks

## Pinterest — Primary Image Source
Queries: `{product} swatches bibir`, `{product} di tangan review`, `{product} pemakaian`, `{product} review asli`
Skip first 4 images (catalog shots), pick from index 4-8 for real user photos
Upgrade: 236x → 736x for HD

## Bing — Last Resort Only
ISP Indonesia DNS hijacking → SafeSearch forced ON → many products return empty/wrong
Some keywords (e.g. "Barenbliss", "lip tint") trigger false-positive porn filter

## Cookie Management
Files: ~/instagram_cookies.json, ~/threads_cookies.json
Extract from Chrome, inject via Playwright context.add_cookies()

## Anti-Detection
Stealth browser args, mock WebGL, hide navigator.webdriver
Rate limit: max 5 posts/day from same IP

## Setup Checklist
1. Python 3.9+ with playwright, Pillow, browser_cookie3
2. playwright install chromium
3. Prepare affiliate-link-database.md
4. Extract Instagram + Threads cookies
5. Create empty history JSON
6. Configure cron: 3x daily (08:00, 13:00, 20:00)
