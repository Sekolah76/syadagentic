# Threads Shadowban & Hard Verification (v8)

Threads actively shadowbans automated replies. The UI will show the comment as successfully posted, but it is silently hidden from the public.

## Key Constraints
1. **Raw API Fails:** Raw `requests` to the GraphQL endpoint fail immediately due to heavy integrity checks (`doc_id`, CSRF tokens, app ID mismatch). You MUST use Playwright to mimic a real browser.
2. **Fake Success:** Playwright detecting the "Post" button click or a 200 OK from the API is NOT proof of delivery.

## Hard Verification Protocol
To detect a shadowban and prevent the database from marking a link as `USED` falsely, "Hard Verification" is required:
1. **Fetch Interception:** Inject `window._apiLogs` to intercept `window.fetch` and catch `"Media blocked due to integrity"` or `"status":"fail"` responses.
2. **DOM Reload Verification:** Even if the API returns 200 OK, you MUST `page.reload()` and check if the comment text exists in `document.body.innerText`. If the text is missing, the account is shadowbanned and the reply failed silently.
3. **SSO Login Flow:** To ensure session stability, always navigate to `instagram.com` first, wait 5 seconds, then navigate to `threads.net`, and click the "Log in with Instagram" / "Continue" SSO button.