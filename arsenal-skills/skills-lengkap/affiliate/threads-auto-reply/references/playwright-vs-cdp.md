# Playwright vs CDP Comparison

## Overview

Two approaches for Threads automation:
1. **Playwright** — headless Chromium, lighter, managed
2. **CDP** — full Chrome with remote debugging, heavier, more control

## Comparison Table

| Feature | Playwright | CDP |
|---------|------------|-----|
| Resource Usage | Light (headless) | Heavy (full Chrome) |
| Startup Time | Fast | Slow (Chrome launch) |
| Browser Management | Managed by Playwright | Manual Chrome process |
| Anti-bot Detection | Works ✅ | Works ✅ |
| Cookie Injection | context.add_cookies() | Network.setCookie |
| Text Input | execCommand('insertText') | execCommand('insertText') |
| Button Click | page.evaluate('btn.click()') | cdp_eval(ws, 'btn.click()') |
| Debugging | Harder (headless) | Easier (port 9222 visible) |
| Port Conflicts | None | Port 9222 lock issues |
| Script Files | threads_reply_playwright.py | threads_reply_v6.py |

## When to Use Playwright

- **Default choice** — lighter, faster
- **Cron jobs** — better for scheduled runs (no port conflicts)
- **Batch operations** — multiple runs without resource exhaustion
- **Production** — more stable for long-term automation

## When to Use CDP

- **Debugging** — can inspect browser via Chrome DevTools
- **Anti-bot issues** — real Chrome fingerprint if Playwright gets blocked
- **Complex interactions** — better for multi-step flows requiring debugging
- **Manual testing** — easier to see what's happening

## Verified Test Results

**Playwright v7.0 (`threads_reply_playwright.py`) — Tested 2026-06-12:**
- Login: ✅ Success (Meta SSO via "Continue with Instagram")
- Search: ✅ Found posts for keyword
- Reply: ✅ Posted successfully
- Product: Hanasui Acne Expert Series
- Target: @totally.tiramisu
- **Bug fixed:** `browser.close()` throws "Event loop is closed" → wrapped in try/except
- **Run command:** `cd /Users/user/.hermes/scripts && /Users/user/.hermes/hermes-agent/venv/bin/python3 threads_reply_playwright.py`

## TLS Fingerprinting (Verified 2026-06-16)

Meta's servers check TLS fingerprint (JA3/JA4) on ALL API endpoints. This determines which HTTP clients can make API calls:

| Client | TLS Fingerprint | GraphQL API | REST API |
|--------|----------------|-------------|----------|
| `requests`/`urllib3` | Python | ❌ Error 1357004 | ❌ Blocked |
| Playwright headless | Chromium | ✅ Works | ✅ Works |
| CDP (real Chrome) | Chrome | ✅ Works | ✅ Works |
| `curl` (standard) | curl | ❌ Blocked | ❌ Blocked |
| `curl-impersonate` | Chrome-mimicking | ✅ Should work | ✅ Should work |

**Key insight:** "Truly browserless" (pure HTTP library without any browser engine) is IMPOSSIBLE for Threads. Even with correct cookies, headers, and session tokens, the TLS fingerprint mismatch causes rejection.

**Practical approach for browserless API calls:**
Use Playwright's `page.evaluate()` to make `fetch()` calls FROM within the browser context. This uses Chromium's HTTP stack (correct TLS fingerprint) while still being "browserless" from the automation perspective (no visible browser, no manual interaction).

```python
result = page.evaluate("""async () => {
    const body = new URLSearchParams();
    body.set('fb_api_caller_class', 'RelayModern');
    body.set('doc_id', '26572510379048070');
    body.set('variables', JSON.stringify({"first": 3, "query": "skincare"}));
    const r = await fetch('/api/graphql', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded', 'X-IG-App-ID': '238260118697367'},
        body: body.toString(),
    });
    const text = await r.text();
    return text.startsWith('for (;;);') ? text.substring(9) : text;
}""")
data = json.loads(result)
```

## Account Safety Pattern (SYADAGENTIC Directive 2026-06-12)

When account is at risk of suspension:
1. **Immediately pause ALL Threads automation** — Reply, Post, Cookie Refresh
2. **Resume only when user confirms safe**
3. **Pattern:** `cronjob(action='pause', job_id='...')` for all 3 jobs

### Job IDs
- Reply: `67a687f2978a`
- Post: `23199a7b2d5b`
- Cookie Refresh: `f1902736896e`

### Pause Command
```python
cronjob(action='pause', job_id='67a687f2978a')  # Reply
cronjob(action='pause', job_id='23199a7b2d5b')  # Post
cronjob(action='pause', job_id='f1902736896e')  # Cookie Refresh
```

### Resume Command
```python
cronjob(action='resume', job_id='67a687f2978a')  # Reply
cronjob(action='resume', job_id='23199a7b2d5b')  # Post
cronjob(action='resume', job_id='f1902736896e')  # Cookie Refresh
```
