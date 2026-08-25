# TOOLS.md — Tool Registry (SYADAGENTIC)
# Daftar tool yang tersedia utk agent + cara pakai.

## TERMINAL / EXEC
- terminal (bash/PowerShell) — eksekusi perintah, evidence-gated
- execute_code — Python script dgn hermes_tools
- proses background — server/bot jangka panjang

## FILE
- read_file / write_file / patch / search_files — file ops
- Base: ~/farm-arsenal/, ~/AppData/Local/hermes/

## WEB
- web_search / web_extract — riset internet
- browser (navigate/click/type/console) — interaksi web (CDP attach utk CF)

## NETWORK / PROXY
- 9router launcher :20128 (API router) — proxy ocu :8765
- cloudscraper — CF bypass (arsenal/tools/cloudscraper)
- nopecha — captcha solver (arsenal/tools/nopecha-python)

## AI / JB
- templates.md (T1-T105) — jailbreak engine
- jb_injector.py :20129 — inject template ke request
- MASTER-JB-TEMPLATES + per-model strategy (ag/cx/th/or)

## CLOUD
- GCP: gcp_helper.py (VM agent-test-01, e2-small Jakarta)
- Daytona: daytona_keys.txt (15 key, sandbox)