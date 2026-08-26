# Passive CT + DNS-brute + curl fingerprinting (no ProjectDiscovery tools installed)

A proven, low-traffic recon path that works with ONLY `curl`, `dig`/`host`, and Python stdlib
(`socket`, `concurrent.futures`, `subprocess`) — no subfinder/httpx/dnsx/amass required.
Use when the target is a large org and you want passive-only, or when PD tools aren't installed.
Validated on Tencent Cloud (cloud.tencent.com platform, ~1600 candidates → 806 resolved → 619 probed).

## 1. crt.sh certificate transparency (flaky — MUST retry)

crt.sh frequently returns `502 Bad Gateway` or an HTML `ERROR!` page, and large domains
(cloud.tencent.com, qcloud.com) can time out. A naive one-shot curl fails ~50% of the time.

```bash
# Retry loop with UA + size/error guard (run in background for big domains):
for i in $(seq 1 12); do
  curl -s --max-time 50 -A "Mozilla/5.0" "https://crt.sh/?q=%25.$DOMAIN&output=json" -o out.json
  s=$(wc -c < out.json)
  if [ "$s" -gt 500 ] && ! grep -q "ERROR" out.json; then break; fi
  sleep 5
done
```

- Query pattern: `?q=%25.$DOMAIN&output=json` (the `%25.` prefix = `%.` wildcard).
- crt.sh has NO rate-limit complaints but is just slow/flaky — retry with backoff, don't give up.
- **Truncated JSON**: large responses sometimes cut mid-string. `json.load()` throws
  `Unterminated string`. Fall back to regex extraction:
  `re.findall(r'"name_value"\s*:\s*"([^"]+)"', text)` then split on `\n` (the JSON escapes newlines as `\n`).
- Query multiple sibling domains in parallel/background (e.g. `example.com`, `api.example.com`,
  `cdn.example.com`, `intl.example.com`) — each is a separate CT surface.

## 2. DNS brute for cloud-related names

Wordlist of product + infra names (console, api, capi, portal, uat, staging, stage, dev, test,
pre, gray, admin, internal, gw, gateway, edge, sso, auth, login, cdn, static, assets, billing,
pay, cam, iam, + product names). Resolve with Python stdlib for concurrency:

```python
import socket, concurrent.futures
def resolve(h):
    try:
        return h, sorted({a[4][0] for a in socket.getaddrinfo(h, None)})
    except Exception:
        return h, []
with concurrent.futures.ThreadPoolExecutor(max_workers=200) as ex:
    resolved = dict(ex.map(resolve, candidates))
```

## 3. INTERPRETING RESOLUTION RESULTS — the critical step

Before probing, classify resolved IPs. This is where most recon mistakes happen:

| Pattern | Meaning | Action |
|---|---|---|
| Many names → **same 3-4 IPs** | **Wildcard DNS** (e.g. `*.api.example.com` → same gateway IPs). NOT distinct assets. | EXCLUDE from probing; they're one host. |
| Name → `0.0.0.1` (or `0.0.0.0`) | **DNS sinkhole** — org deliberately parked the name (often to kill dangling-CNAME takeover). | NOT a takeover candidate. Verify: `dig +short name CNAME` empty + A=0.0.0.1 = intentional sinkhole. |
| Name → `9.x`, `10.x`, `11.x`, `21.x`, `169.254.x` | **Internal-only** IPs. Resolve publicly but not reachable from the internet. | Note as internal; expect connection failures (000). |
| Name → public IP | Real externally-reachable asset. | Probe. |

Filter script logic: keep a host for probing only if its IP set is NOT a subset of the wildcard
set AND does not contain `0.0.0.1`. Log sinkholes and wildcards separately for the report.

## 4. curl-only fingerprinting (status / server / title)

**Gotcha #1 — which `httpx` is on PATH?** `httpx` may be the *Python* HTTP client CLI
(`httpx --help` shows `-m/--method`, `-p/--params`), NOT ProjectDiscovery's httpx
(`httpx -silent -status-code -title`). Check `httpx --help` / `httpx -version` before relying on
PD flags. If it's the Python client, just use curl.

**Gotcha #2 — subprocess text-mode newline mangling.** With `subprocess.run(..., text=True)`,
`\r\n` is normalized to `\n`, so `out.partition("\r\n\r\n")` returns an empty body. Partition on
`"\n\n"` (fall back to `"\r\n\r\n"`).

**Gotcha #3 — don't mix `-D -` headers with `-w`.** Cleaner to capture the `-w` summary only and
read the body from a file for the title:

```python
r = subprocess.run(
  ["curl","-s","-k","-L","--max-time","8","-A","Mozilla/5.0",
   "-w","STATUS:%{http_code}\tURL:%{url_effective}\tCT:%{content_type}\tSERVER:%header{server}\tREDIR:%{redirect_url}",
   "-o","/tmp/body.html", url],
  capture_output=True, text=True, timeout=12)
# parse STATUS:/URL:/CT:/SERVER: from r.stdout; grep <title> from /tmp/body.html
```

- `%header{server}` gives the LAST response's server header (after `-L` redirects).
- `-L` follows redirects so you capture the effective URL (e.g. login redirect) and final title.
- Concurrency ~60 workers is fine for light single-GET probing; keep `--max-time` low.

## 5. Prioritization heuristics for the report

Rank findings by "less-saturated / forgotten asset" signal, not just by being live:
- **dev/test/pre/gray/staging** subdomains that return 200 with a real app → high value (least tested).
- **Default nginx welcome page** on an api/test subdomain → forgotten/unattended service (probe ports/paths).
- **Login pages / SSO bootstrap / admin panels** → auth surface.
- **BFF / API subdomains** returning `{"code":"NORMAL","result":"<Product> BFF"}` → authz/IDOR surface.
- **JSON error leaking internal service names** (e.g. `trpc.<svc>.api`) → info disclosure + endpoint map.
- **Regional console variants** (`bj-*`, `cd-*`, `gz-*`, `sg-*`) → cross-region IDOR potential.
- Separate **customer-owned** subdomains (e.g. COS bucket domains like `*.myqcloud.com`) from the
  org's own assets — bucket domains are customer data and usually out of scope.
