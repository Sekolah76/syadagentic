"""
threads_human_behavior.py — Stealth layer untuk Threads auto-reply v10
Burst-rest scheduler + log-normal delay + warmup sequence.

Drop-in module. Import as:
    import threads_human_behavior as hb
    allowed, reason = hb.should_act_now()
    hb.register_action()
    time.sleep(hb.human_delay("between_replies"))
"""
import math
import random
import time
import os
import json
from datetime import datetime, timezone, timedelta

# ─── Config ──────────────────────────────────────────────────────────────
WIB = timezone(timedelta(hours=7))
STATE_FILE = os.path.expanduser("~/.hermes/state/threads_burst_state.json")
SLEEP_HOUR_START = 1   # 01:00 WIB
SLEEP_HOUR_END = 7     # 07:00 WIB
BURST_MIN = 2          # min replies per burst window
BURST_MAX = 4          # max replies per burst window
BURST_DURATION_MIN = 8 * 60    # 8 min in sec
BURST_DURATION_MAX = 15 * 60   # 15 min in sec
COOLDOWN_MIN = 45 * 60         # 45 min cool down
COOLDOWN_MAX = 120 * 60        # 120 min cool down

# Delay distributions (log-normal mean, sigma)
DELAY_PROFILES = {
    "between_chars": (0.12, 0.5),       # typing: ~120ms mean, wide variance
    "before_click": (0.6, 0.4),         # hover before clicking
    "after_paste": (3.0, 0.6),          # read what you typed
    "before_post": (8.0, 0.5),          # human reviews before post
    "between_replies": (45.0, 0.7),     # between consecutive replies
    "page_settle": (2.5, 0.4),          # after navigation
}


def _load_state():
    if not os.path.exists(STATE_FILE):
        return {"burst_started_at": 0, "burst_count": 0, "last_action_at": 0,
                "cooldown_until": 0}
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"burst_started_at": 0, "burst_count": 0, "last_action_at": 0,
                "cooldown_until": 0}


def _save_state(s):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(s, f)


def is_sleep_window() -> bool:
    """01:00-07:00 WIB = sleep, no replies."""
    now = datetime.now(WIB)
    return SLEEP_HOUR_START <= now.hour < SLEEP_HOUR_END


def should_act_now() -> tuple[bool, str]:
    """Returns (allowed, reason)."""
    if is_sleep_window():
        return False, f"sleep_window ({SLEEP_HOUR_START:02d}:00-{SLEEP_HOUR_END:02d}:00 WIB)"

    state = _load_state()
    now = time.time()

    # Still in cooldown?
    if now < state.get("cooldown_until", 0):
        remaining = int(state["cooldown_until"] - now)
        return False, f"cooldown ({remaining // 60}m remaining)"

    return True, "ok"


def register_action():
    """Call after each successful reply. Tracks burst & triggers cooldown."""
    state = _load_state()
    now = time.time()

    # New burst window?
    burst_age = now - state.get("burst_started_at", 0)
    burst_duration = random.uniform(BURST_DURATION_MIN, BURST_DURATION_MAX)

    if burst_age > burst_duration or state.get("burst_count", 0) == 0:
        state["burst_started_at"] = now
        state["burst_count"] = 1
    else:
        state["burst_count"] += 1

    state["last_action_at"] = now

    # Cap burst per window
    burst_cap = random.randint(BURST_MIN, BURST_MAX)
    if state["burst_count"] >= burst_cap:
        cooldown = random.uniform(COOLDOWN_MIN, COOLDOWN_MAX)
        state["cooldown_until"] = now + cooldown
        state["burst_count"] = 0
        state["burst_started_at"] = 0
        _save_state(state)
        return True, f"burst_complete, cooldown {int(cooldown/60)}m"

    _save_state(state)
    return True, f"burst {state['burst_count']}/{burst_cap}"


def human_delay(profile: str = "between_chars") -> float:
    """Log-normal delay (more human than uniform random)."""
    mean, sigma = DELAY_PROFILES.get(profile, (1.0, 0.5))
    # log-normal centered on mean
    mu = math.log(mean) - (sigma**2) / 2
    delay = random.lognormvariate(mu, sigma)
    # Clamp to sane range
    delay = max(0.05, min(delay, mean * 6))
    return delay


def sleep_human(profile: str = "between_chars"):
    """time.sleep with log-normal distribution."""
    time.sleep(human_delay(profile))


def human_type(page, text: str):
    """Type with per-char log-normal delay + occasional pauses."""
    for i, char in enumerate(text):
        page.keyboard.type(char)
        # Occasional micro-pause (mid-word thinking)
        if random.random() < 0.03:
            sleep_human("after_paste")
        else:
            sleep_human("between_chars")


def warmup_sequence(page, scroll_count: int = None):
    """Pre-action behavior: scroll feed, optional like, simulate browsing."""
    if scroll_count is None:
        scroll_count = random.randint(2, 5)

    print(f"  [warmup] scroll x{scroll_count} + browse")
    for _ in range(scroll_count):
        scroll_y = random.randint(300, 900)
        page.mouse.wheel(0, scroll_y)
        time.sleep(human_delay("page_settle"))

    # 20% chance: scroll back up a bit (re-read)
    if random.random() < 0.2:
        page.mouse.wheel(0, -random.randint(200, 500))
        time.sleep(human_delay("page_settle"))


if __name__ == "__main__":
    # CLI: check status
    allowed, reason = should_act_now()
    print(f"should_act_now: {allowed} ({reason})")
    state = _load_state()
    print(f"state: {json.dumps(state, indent=2)}")
    print(f"\nSample delays:")
    for p in DELAY_PROFILES:
        samples = [round(human_delay(p), 2) for _ in range(5)]
        print(f"  {p:20s} : {samples}")
