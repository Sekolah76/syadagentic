# Playwright CDP Timeout Pitfall

**Discovered:** 2026-06-24
**Issue:** The `threads_reply_v6.py` script, which relies on Chrome Headless (CDP) and Playwright, consistently hangs and times out (e.g., `Script timed out after 300s`) when run as a cron job on the user's 8GB MacBook Air.

**Cause:** Heavy RAM swapping when Chrome is already open. Playwright processes stall under memory pressure, causing the cron job to fail silently or timeout.

**Resolution Mandate:**
Do **NOT** use browser automation (Playwright/Selenium/CDP) for the Threads Auto-Reply script.
The script MUST be rewritten to use the internal GraphQL API via standard HTTP `requests`, exactly mimicking the architecture of the `threads-auto-post` skill (which is 100% browser-less, fast, and stable).

**Key Takeaway for Future Upgrades:**
Whenever possible, prioritize raw API/GraphQL requests over headless browsers for cron-based automation on low-RAM machines.
