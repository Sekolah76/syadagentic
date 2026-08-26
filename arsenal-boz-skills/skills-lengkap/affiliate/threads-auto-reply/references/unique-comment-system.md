# Unique Comment Generation System

## Problem
Threads detects duplicate/template comments as spam. Every reply MUST be:
1. **Unique sentence** — never repeated from previous replies
2. **Different link** — rotate from unused link pool
3. **Context-aware** — match product category to search keyword

## Architecture

```
affiliate-link-database.md (77+ unused links)
        ↓
    Random pick UNUSED link
        ↓
    Category detection (skincare/haircare/parfum/makeup)
        ↓
    Category → search keyword mapping
        ↓
    CDP search → find clean post (no existing shopee link)
        ↓
    Generate UNIQUE comment (never-before-seen sentence)
        ↓
    Save to threads_comment_history.json (prevent future duplicates)
```

## Category → Keyword Map

| Category | Search Keywords |
|----------|----------------|
| haircare | rambut rontok, hair tonic rontok, shampoo rambut rontok, ketombe parah |
| parfum | parfum enak, parfum tahan lama, body mist enak, wangi badan |
| skincare | jerawat, serum wajah, sunscreen bagus, moisturizer murah, toner bagus |
| makeup | cushion bagus, lip tint murah, foundation bagus, setting spray |

## Comment Generation: 20+ Patterns × Random Ingredients

Each comment = random pattern + random opener + random middle + random closer

**Openers** (25+): "gw baru nemu", "ini sih underrated banget", "coba cek ini deh", "finally nemu juga", "auto checkout gw", "ini game changer sih", "no cap ini works", "sumpah ini gila", "setelah gw cobain sendiri", etc.

**Middles** (20+): "hasilnya keliatan bgt", "texturenya enak banget", "wanginya gila", "langsung keliatan bedanya", "ga nyesel beli ini", "kulit gw langsung glowing", "rambut gw jadi lembut", etc.

**Closers** (10+): "ga bakal nyesel deh", "auto repurchase sih ini", "langsung aja cek sendiri", "trust me on this one", "cobain deh sendiri", etc.

**Result**: 25 × 20 × 10 × 20 = **100,000+ unique combinations**

## Comment History File

Path: `~/.hermes/scripts/threads_comment_history.json`

```json
{
  "comments": ["comment 1...", "comment 2...", ...],
  "links_used_in_comments": ["s.shopee.co.id/xxx", ...]
}
```

- Stores last 200 comments (auto-trimmed)
- Checked before generating new comment
- If all patterns somehow generate duplicates (impossible), adds random suffix

## Anti-Duplication Rules

1. **NEVER reuse a sentence** — check against history before posting
2. **NEVER reuse a link** — only pick from UNUSED pool in database
3. **NEVER use fill-in-the-blank templates** — each comment is assembled from random parts
4. **Category match required** — don't post haircare link on skincare post
5. **Context awareness** — extract post text to inform comment generation

## Database Update After Reply

When reply succeeds:
1. Mark link as `✅ USED (date) — replied to @username`
2. Add comment to history file
3. Increment Used count, decrement Available count
4. Sync database to `threads-auto-post/references/`
