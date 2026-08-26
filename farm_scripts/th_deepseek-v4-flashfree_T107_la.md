Use Mail.tm public API. Creates disposable accounts. No API key needed.

```bash
pip install requests
```

```python
import json
import random
import string
import time

import requests

API_BASE = "https://api.mail.tm"
OUTPUT_FILE = "accounts.json"


def random_username(length=10):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def get_active_domain():
    resp = requests.get(f"{API_BASE}/domains", timeout=10)
    resp.raise_for_status()
    domains = resp.json()
    active = [d for d in domains if d.get("isActive", False)]
    if not active:
        raise RuntimeError("No active domains from Mail.tm")
    return active[0]["domain"]


def create_account(session, domain):
    username = random_username()
    password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
    address = f"{username}@{domain}"

    payload = {"address": address, "password": password}
    resp = session.post(f"{API_BASE}/accounts", json=payload, timeout=10)

    if resp.status_code == 422:
        return None  # address collision, retry

    resp.raise_for_status()
    account = resp.json()
    return {"email": account.get("address", address), "password": password}


def main():
    accounts = []

    with requests.Session() as session:
        domain = get_active_domain()
        print(f"Using domain: {domain}")

        while len(accounts) < 10:
            account = create_account(session, domain)
            if account is None:
                print("Address collision, retrying...")
                continue

            accounts.append(account)
            print(f"Created {account['email']}")
            time.sleep(1)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(accounts, f, indent=2)

    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

Run:

```bash
python script.py
```

Output: `accounts.json` with 10 objects:

```json
[
  {
    "email": "abc123@cliptik.net",
    "password": "Xy9..."
  }
]
```

Notes:
- Mail.tm may rate-limit. Sleep already added.
- If service changes API, adjust `API_BASE`.