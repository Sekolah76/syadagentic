# Threads API Endpoints

## 1. Reply/Comment REST Endpoint (legacy, intercepted via fetch monkey-patch)

**Endpoint:** `POST /api/v1/media/configure_text_only_post/`

### Success Response (200)
```json
{
  "media": {
    "strong_id__": "3906381404377234600_38122991886",
    "pk": "3906381404377234600",
    "id": "3906381404377234600_38122991886",
    "fbid": "17970078131903850",
    "code": "DY2QTC9GLyo",
    "integrity_review_decision": "pending",
    "media_type": 19,
    "product_type": "text_post"
  }
}
```

### Key Fields
- `integrity_review_decision`:
  - `"pending"` — Comment under spam review, invisible to all
  - Other values may indicate approved/rejected (not yet observed)
- `code` — Post URL slug, e.g., `https://www.threads.com/p/DY2QTC9GLyo`
- `strong_id__` — Composite of {post_id}_{user_id}

### Detection of Flagged Account
When `integrity_review_decision` is `"pending"` on EVERY reply attempt (even plain text comments), the account is flagged. The API returns 200 and the dialog closes normally, but comments are invisible.

---

## 2. Threads GraphQL API (discovered 2026-06-16)

Threads web app uses GraphQL for ALL data fetching. Two interchangeable endpoints:

### Endpoints
- `POST https://www.threads.com/api/graphql` (newer, preferred)
- `POST https://www.threads.com/graphql/query` (legacy, also works)

### Required Headers
```
Content-Type: application/x-www-form-urlencoded
X-IG-App-ID: 238260118697367
X-CSRFToken: <csrftoken from cookies>
X-FB-Friendly-Name: <query_name>  (e.g., BarcelonaFeedDirectQuery)
Origin: https://www.threads.com
Referer: https://www.threads.com/
```

### POST Body Format
```
av=17841438156605373&__user=0&__a=1&__req=<hex_counter>&__hs=<session>&dpr=2&__ccg=GOOD&__rev=<revision>&__s=<session_token>&__hsi=<request_id>&__dyn=<dynamic_config>&__csr=<csrf_hash>&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=<query_name>&doc_id=<doc_id>&variables=<json>
```

### Critical Parameters
| Param | Description | Replay-safe? |
|-------|-------------|--------------|
| `doc_id` | Query identifier (numeric) | ✅ Stable per query |
| `variables` | JSON query variables | ✅ Standard |
| `av` | App version/viewer ID (`17841438156605373`) | ✅ Stable |
| `__user` | Always `0` (not user ID) | ✅ Stable |
| `__s` | Session token | ❌ Expires in seconds |
| `__hsi` | Request ID | ❌ Per-request |
| `__csr` | CSRF hash | ❌ Per-session |
| `__dyn` | Dynamic module config | ❌ Per-session |
| `__hs` | Session header | ❌ Per-session |
| `__rev` | Build revision (`1041545003`) | ⚠️ Changes per deploy |

### Response Format
All responses are prefixed with `for (;;);` (anti-JSON-hijacking). Strip before parsing:
```python
body = response.text
if body.startswith('for (;;);'):
    body = body[9:]
data = json.loads(body)
```

### Known doc_ids (captured 2026-06-16)

**Queries (read):**
| doc_id | Friendly Name | Variables | Description |
|--------|---------------|-----------|-------------|
| `27051092951185691` | BarcelonaFeedDirectQuery | `{"data":{"pagination_source":"text_post_feed_threads","reason":"cold_start_fetch"},"variant":"for_you","__relay_internal__pv__BarcelonaIsLoggedInrelayprovider":true}` | Home feed |
| `26572510379048070` | BarcelonaCommunityEntityCardsPanelSportGamesQuery | `{"first":5,"query":"<search_term>"}` | Search posts |
| `26775939545431500` | BarcelonaCommunityEntityCardsPanelQuery | `{"tag_name":"<tag>"}` | Tag/community |
| `26880892648257836` | useBarcelonaBatchedDynamicPostCountsSubscriptionQuery | `{"post_ids":["<pk>"]}` | Post counts |
| `27283777334592180` | BarcelonaFeedTimelineViewerQuery | `{"__relay_internal__pv__BarcelonaIsLoggedInrelayprovider":true}` | Feed viewer |
| `24829571333311082` | BarcelonaFeedsTabGroupViewerQuery | `{"feed_types":["composite_list"],"__relay_internal__pv__BarcelonaIsFediverseFeedEnabledrelayprovider":true}` | Feed tabs |
| `27448173834778572` | BarcelonaFeedPaginationDirectQuery | `{"after":"<cursor>","before":null,"data":{...}}` | Feed pagination |

**Utility queries:**
| doc_id | Description |
|--------|-------------|
| `26445309001763311` | Like animations loader |
| `25733604246267556` | Messages mailbox |
| `27324958417099511` | Badge count |
| `25559269557086115` | Side nav home |
| `26832517353036792` | Feeds list |
| `24179286691677063` | Quick promotion interstitial |
| `35874382745539608` | Feed interstitial |

### ⚠️ CRITICAL: Pure `requests` library CANNOT call Threads GraphQL

**Even with correct cookies + session tokens, `requests` library gets error 1357004:**
```
"Sorry, something went wrong" / "Please try closing and re-opening your browser window"
```

**Root cause:** Meta checks TLS fingerprint (JA3/JA4). `requests`/`urllib3` has a different TLS handshake than Chrome. Even with identical headers and cookies, the TLS fingerprint mismatch causes rejection.

**Working approaches:**
| Method | TLS Fingerprint | Works? |
|--------|----------------|--------|
| `requests` library | Python/urllib3 | ❌ Blocked (JA3 mismatch) |
| Playwright headless | Chromium | ✅ Works |
| CDP (real Chrome) | Chrome | ✅ Works |
| `curl-impersonate` | Chrome-mimicking | ✅ Works (not tested) |

**Practical implication:** To make browserless API calls to Threads GraphQL, must use Playwright's `page.evaluate(fetch(...))` or `context.request.post()` — NOT standalone `requests`.

### Session Token Lifecycle
The `__s`, `__hsi`, `__csr`, `__dyn` parameters are generated by Threads' JavaScript bundle on each page load. They:
- Are unique per page load (not reusable across sessions)
- Expire within seconds (cannot be captured and replayed)
- Are tied to the browser's HTTP/2 fingerprint

**Hybrid approach tested (failed):** Capture tokens via Playwright → use in `requests` → still fails because TLS fingerprint changes between Playwright and requests.

**Only reliable browserless approach:** Use Playwright's JavaScript context to make `fetch()` calls FROM the browser page, using the page's own session state.

---

## 3. How to Capture API Response (Debugging)

Monkey-patch `window.fetch` before clicking Post:

```javascript
// Inject BEFORE clicking Reply button
const origFetch = window.fetch;
window._apiLogs = [];
window.fetch = async function(...args) {
    const req = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
    const opts = args[1] || {};
    const logEntry = {url: req, method: opts.method || 'GET', body: opts.body};
    const resp = await origFetch.apply(this, args);
    const clone = resp.clone();
    try {
        logEntry.status = resp.status;
        logEntry.responseBody = (await clone.text()).substring(0, 2000);
    } catch(e) {}
    window._apiLogs.push(logEntry);
    return resp;
};
```

After clicking Post and waiting:
```python
page.evaluate("() => window._apiLogs.filter(l => l.url.includes('configure_text_only_post'))")
```

---

*Last updated: 2026-06-16 — Added GraphQL API discovery, TLS fingerprinting pitfall, doc_id capture*
