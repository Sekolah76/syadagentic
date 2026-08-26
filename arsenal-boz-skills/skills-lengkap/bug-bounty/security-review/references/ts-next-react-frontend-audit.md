# TypeScript / Next / React Frontend Security Review Notes

Use this reference when auditing Next.js, React SPAs, docs sites, wallets, or explorer-style apps for XSS/auth/data-leak candidates.

## High-signal checks

- Treat CMS, markdown/MDX content, on-chain metadata, node/operator self-descriptions, and API-fed link lists as untrusted unless the code proves otherwise.
- Search sinks: `dangerouslySetInnerHTML`, `innerHTML`, `srcDoc`, dynamic `<script>`, `react-markdown`, `rehypeRaw`, `marked`, `DOMPurify`, `next/link`/MUI `Link`, raw `<a href>`, `next/image`, `router.push`, `window.location`, `localStorage`, Tauri `openUrl`, and `invoke` playgrounds.
- For API routes, map `app/api/**/route.ts` or `pages/api/**` first, then inspect auth, cookie/header trust, SSRF/open proxy behavior, and response leakage.
- Verify markdown renderer defaults before reporting: `react-markdown` without `rehypeRaw` escapes HTML and normally uses a safe URL transform; don't report raw markdown XSS without proving the installed config permits it.
- `javascript:` / `data:` URLs in anchors are real XSS candidates when the value is attacker-controlled and clickable on a trusted origin. Check whether wrappers validate schemes or simply pass `href` through.
- CSP is a mitigation, not a root-cause fix. If production CSP contains `'unsafe-inline'`/`'unsafe-eval'`, don't rely on it to downgrade a clickable `javascript:` link candidate.

## Evidence bar

For findings-only requests, only report candidates that include: attacker-controlled source, exact sink, user/browser action required if any, why framework escaping does not neutralize it, impact on the trusted origin, and a PoC idea. Reject self-XSS, clickjacking-only issues, and admin-only CMS edits unless the CMS/content role is in scope or the content is decentralized/user-controlled.

## Useful search patterns

```text
dangerouslySetInnerHTML|innerHTML|srcDoc|document.createElement\("script"\)|script.src
react-markdown|Markdown|rehypeRaw|remark|marked|DOMPurify|sanitize
href=\{|<a href|next/link|router.push|window.location|new URLSearchParams
app/api|pages/api|NextRequest|NextResponse|export async function (GET|POST|PUT|DELETE)
localStorage|sessionStorage|openUrl|invoke\(|readText|writeText
```
