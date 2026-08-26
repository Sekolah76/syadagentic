# Playwright Hard Verification (Shadowban Detection)

When automating Threads replies, pure HTTP API requests (GraphQL) fail strictly due to `doc_id` and CSRF validation. 
However, raw Playwright actions can result in "shadowbans" where the UI shows "Posted" but the server silently blocks it (e.g., Media integrity block).

**Implementation for robust verification:**
1. **Fetch Interception**: Inject a `window.fetch` monkeypatch via `page.evaluate()` *before* clicking Post, to capture API responses in `window._apiLogs`.
2. Wait for the Post button click.
3. **API Check**: Check `window._apiLogs` for `"status":"fail"`, `"fail"`, or `"Media blocked due to integrity"`. If found, the post was rejected by the backend.
4. **Hard DOM Verification**: Even if the API succeeds, perform a reload: `page.reload()`, wait, and check `document.body.innerText` to ensure the comment snippet and affiliate link actually render on the public page. If they don't, the account is shadowbanned and the reply should not be marked as successful in the database.