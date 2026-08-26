# Playwright vs requests (Threads Reply Script)

## Context (2026-06-24)
- Previous CDP monkeypatching implementation in `threads_reply_v6.py` was too heavy for an 8GB MacBook, resulting in frequent 60-second timeouts.
- Attempted to migrate to a pure API (`requests` / GraphQL) script for extreme lightweight operation.
- **Result:** Failed. The Threads GraphQL API (`/api/graphql` and `/api/v1/media/configure_text_only_post/`) is incredibly strict. It demands precise matching of `doc_id`, CSRF tokens, `__spin_t`, `X-IG-App-ID`, and `fb_api_caller_class`. Raw HTTP requests get instantly rejected.

## Rule
The stable and accepted implementation for `threads_reply` is **Pure Playwright (Headless)** without any CDP network monkeypatching. It relies on standard DOM manipulation (`page.evaluate`) and clipboard pasting (`navigator.clipboard.writeText`) to simulate human interactions—the exact same technique used by the `threads_post` script.

**DO NOT** attempt to rewrite the `threads_reply` script to use pure `requests` API endpoints unless explicitly instructed by the user to experiment.