# Threads Shadowban & Ghosting Verification Protocol

Threads aggressively silent-blocks automated comments. It will accept the click, show no error in the UI, but the comment will never appear publicly (ghosting/shadowbanning).

## 1. Network Interception (API Catch)
The reply script must inject a `fetch` interceptor to capture the `configure_text_only_post` API call.
Meta will return HTTP 200 even for blocks, but the JSON body will contain indicators:
- `"status":"fail"`
- `"fail"`
- `"Media blocked due to integrity"`

If any of these are found in the intercepted response body, the post FAILED. Do not log it as a success.

## 2. Hard DOM Verification (The Reload Check)
Even if the API response is clean, you must verify the post actually rendered.
1. Wait 5-8 seconds after clicking "Post".
2. `page.reload()`
3. Wait 5-8 seconds for the DOM to settle.
4. Extract `document.body.innerText`.
5. Check if the unique `s.shopee.co.id` link OR the exact comment snippet appears in the text.
If it does NOT appear, it is a shadowban. Log it as a silent failure and do not mark the affiliate link as "USED" in the database so it can be attempted again later on a different post.

## Vercel Claim Setup
When verifying domains for Pinterest on Vercel:
Do not waste time trying to use Cloudflare API tokens if they lack zone permissions.
Create a temp Vercel project (`/tmp/vercel_project`), initialize with `npx vercel pull`, copy the verification HTML file into the directory, and deploy with `npx vercel deploy --prod --yes`. This instantly hosts the file for Pinterest to verify without touching DNS records.