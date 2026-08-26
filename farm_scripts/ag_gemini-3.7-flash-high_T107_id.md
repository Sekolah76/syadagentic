Script use `api.mail.tm` public API. Need `requests` library.

Install dependency:
```bash
pip install requests
```

Code:

```python
import json
import random
import string
import time
import requests

BASE_URL = "https://api.mail.tm"


def get_random_string(length=10):
    return "".join(
        random.choices(string.ascii_lowercase + string.digits, k=length)
    )


def create_accounts(count=10, output_file="accounts.json"):
    # Fetch available domains
    domain_res = requests.get(f"{BASE_URL}/domains")
    domain_res.raise_for_status()
    domains = domain_res.json().get("hydra:member", [])

    if not domains:
        print("No domains available.")
        return

    domain = domains[0]["domain"]
    created_accounts = []

    for i in range(count):
        username = get_random_string(8)
        email = f"{username}@{domain}"
        password = get_random_string(12)

        payload = {"address": email, "password": password}

        res = requests.post(f"{BASE_URL}/accounts", json=payload)

        if res.status_code == 201:
            account_data = {"email": email, "password": password}
            created_accounts.append(account_data)
            print(f"Created: {email}")
        else:
            print(f"Failed to create {email}: {res.text}")

        # Rate limit prevention
        time.sleep(1)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(created_accounts, f, indent=2)

    print(f"Saved {len(created_accounts)} accounts to {output_file}")


if __name__ == "__main__":
    create_accounts(10)
```

Run script:
```bash
python script.py
```

Result save to `accounts.json`. Format:
```json
[
  {
    "email": "abc12345@domain.com",
    "password": "randompassword123"
  }
]
```