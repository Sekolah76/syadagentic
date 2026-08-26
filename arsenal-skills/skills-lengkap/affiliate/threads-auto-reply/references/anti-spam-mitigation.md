# Threads Anti-Spam & Shadowban Mitigation (v6.5)

To prevent Threads action blocks ("Tindakan volume tinggi / Spam") and shadowbans:

1. **Reduce Frequency:** Set cron schedule to a minimum of 4 hours (`every 240m`) or daily to avoid detection. Do not run every 30m or 150m.
2. **Human Delay:** Inject a `time.sleep(random.randint(15, 30))` between typing the comment and clicking the Submit button to simulate natural typing speed. Immediate submission (< 2s) triggers bot detection.
3. **Trigger Words:** Search using "problem" keywords (e.g., "muka break out", "rambut rontok parah", "makeup crack banget") instead of explicit search terms like "rekomendasi skincare" to look more like organic community engagement.
4. **Link Obfuscation:** If shadowbanned frequently, obfuscate direct URLs in the comment (e.g., `s . shopee . co . id / XXXX`) and instruct users to remove spaces to keep the comment visible. Threads aggressively filters comments containing `shopee.co.id` links if posted rapidly.
5. **No Direct Python Requests for TLS endpoints:** If you encounter `urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'` warnings when hitting internal services or doing API checks via `requests` inside cron scripts, use `subprocess.run(["curl", ...])` as a workaround.