# Cross-Account Verifier — Anti False-Positive (2026-06-30)

## Problem

Script v10 reply verifier reports "SUCCESS & VERIFIED VISIBLE" via own-session DOM reload, but reply is INVISIBLE to public viewers. Meta render reply in own session as UX feedback but discard server-side. Verifier blind to this.

## Symptoms

```
Verifying via page reload...
✅ Reply SUCCESS & VERIFIED VISIBLE!
```
...but cross-account check returns 0 matches for `jagonya_shopee` username on the target post.

## Root Cause

Post-strike hard comment-block period (Tier-1 warning aftermath):
- Strike fires (e.g., post removed for "nudity/sexual activity" false-positive)
- Meta apply silent comment-block 48-168 hours
- Reply submit returns 200 OK
- Reply appears in own session DOM
- Reply NEVER renders to other accounts (own login OR anonymous viewer)
- Verifier loops forever marking success

## Reliable Check (Camoufox)

Playwright headless returns 404 on `threads.com/@user` due to fingerprint detection. Camoufox with `chrome_local_102130715962900495` (real Chrome) hits threads.net successfully.

```bash
# Anonymous viewer check (no login)
camoufox --session check browser open chrome_local_102130715962900495 "https://www.threads.net/@<TARGET_USER>/post/<POST_ID>"
camoufox --session check wait stable
camoufox --session check get text | grep -c "jagonya_shopee"
# 0 = shadowbanned silent, >0 = real visible
camoufox session close check
```

## Integration Pattern

After every reply success in `threads_reply_v6.py`:

```python
import subprocess
def verify_cross_account(post_url: str) -> bool:
    """Returns True if reply genuinely visible to public."""
    session = f"verify_{int(time.time())}"
    try:
        subprocess.run([
            "camoufox", "--session", session,
            "browser", "open", "chrome_local_102130715962900495", post_url
        ], capture_output=True, timeout=30)
        subprocess.run([
            "camoufox", "--session", session, "wait", "stable"
        ], capture_output=True, timeout=15)
        r = subprocess.run([
            "camoufox", "--session", session, "get", "text"
        ], capture_output=True, text=True, timeout=15)
        return "jagonya_shopee" in r.stdout
    finally:
        subprocess.run([
            "camoufox", "session", "close", session
        ], capture_output=True)
```

## Detection Rule

| Cross-account check | Verdict |
|---|---|
| Anonymous: visible | ✓ Real success |
| Anonymous: hidden | ✗ Shadowban — auto-pause cron, alert |
| 3 consecutive shadowbans | Stop run entirely, save state, wait 24h re-test |

## Account Recovery Timeline (post-strike)

- 0-48h after strike: ALL replies silent-blocked
- 48-96h: partial unblock (some replies visible, some not)
- 96-168h: normal if no further strikes
- Reset accelerated if appeal approved
