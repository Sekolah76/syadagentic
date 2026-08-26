Script use `mail.tm` API. Query active domain, generate random credentials, register account, write list to `accounts.json`.

Requirement: `pip install requests`

```python
import json
import secrets
import string
import requests

BASE_URL = "https://api.mail.tm"


def get_domain():
    res = requests.get(f"{BASE_URL}/domains")
    res.raise_for_status()
    data = res.json()
    return data["hydra:member"][0]["domain"]


def generate_random_string(length=10, use_punctuation=False):
    chars = string.ascii_letters + string.digits
    if use_punctuation:
        chars += "!@#$%^&*"
    return "".join(secrets.choice(chars) for _ in range(length))


def create_account(domain):
    username = generate_random_string(8).lower()
    email = f"{username}@{domain}"
    password = generate_random_string(14, use_punctuation=True)

    payload = {"address": email, "password": password}

    res = requests.post(f"{BASE_URL}/accounts", json=payload)
    if res.status_code == 201:
        return {"email": email, "password": password}
    return None


def main():
    domain = get_domain()
    accounts = []

    for _ in range(10):
        acc = create_account(domain)
        if acc:
            accounts.append(acc)

    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)


if __name__ == "__main__":
    main()
```

Run script: `python script.py`. Output save to `accounts.json`.