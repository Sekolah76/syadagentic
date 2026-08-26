# Python/FastAPI composite-ID backend-routing audit

## Trigger

A route accepts a composite identifier such as `port:request_id` and forwards a request to an internal backend selected from that client-provided value.

## Review pattern

1. Locate the route converter. In FastAPI, `{value:path}` accepts slashes, unlike a normal path parameter.
2. Follow parsing of every composite component. A numeric parse (`int(port)`) is validation of syntax, **not authorization**.
3. Require the selected backend identifier to be server-issued or check it against the current configured/healthy backend set before dialing.
4. Trace URL creation into the actual HTTP client. String interpolation of a suffix into a URL can make `../` normalize into a different path and let `?` add a query.
5. Determine whether the response is returned to the caller. JSON reflection turns a blind internal request into response-disclosing loopback SSRF.
6. Separate this from any broader missing-auth finding: the distinct root cause is client-controlled backend selection/path construction; it remains material because it crosses the public-to-loopback trust boundary.

## Reproduction approach without touching real internal services

- Monkeypatch the narrow backend-call helper and invoke the route coroutine with a malicious composite identifier.
- Capture `(port, method, path)` passed into the helper.
- Resolve the exact final URL through the same client URL parser (e.g. `httpx.URL`) and assert the normalized path/query.
- For a representative payload `31337:../../health?proof=controlled`, verify that it targets `127.0.0.1:31337`, normalizes to `/api/v1/health`, and retains `proof=controlled` as a query.

This establishes the request primitive deterministically. Do not claim access to a particular local service, secrets, or a successful live response unless separately demonstrated.

## Remediation

Prefer an opaque server-generated request token mapped server-side to a backend. If a composite form must remain, require the port to be in the active backend registry; constrain the backend request ID to an expected format (such as a UUID); reject slashes, encoded traversal, `?`, and fragments; and URL-encode a validated path segment rather than concatenate raw input.
