# Free Explorer APIs for Contract Auditing (No API Key Required)

When performing smart contract audits, Etherscan API often restricts access with `NOTOK` unless a valid API key is supplied. Use these alternatives to pull verified source code programmatically.

---

## 1. Blockscout API (Ethereum & L2s)

Blockscout is open-source and provides a public API that does not require registration or keys.

**Base URLs:**
- Ethereum Mainnet: `https://eth.blockscout.com/api`
- Other instances can be found directly on Blockscout's instance list.

**Pulling Source Code (Etherscan-compatible action):**
```bash
curl -s "https://eth.blockscout.com/api?module=contract&action=getsourcecode&address=0xa9fd64b5095d626f5a3a67e6db7fb766345f8092"
```

The response matches the Etherscan format exactly:
```json
{
  "status": "1",
  "message": "OK",
  "result": [
    {
      "SourceCode": "...",
      "ContractName": "BridgeLock",
      "CompilerVersion": "v0.8.28+commit.7893614a",
      "OptimizationUsed": "1",
      "Runs": "200",
      "ConstructorArguments": "...",
      "EVMVersion": "Default",
      "Library": "",
      "LicenseType": "MIT",
      "Proxy": "0",
      "Implementation": "",
      "SwarmSource": ""
    }
  ]
}
```

---

## 2. Blockscout REST API (Modern v2)

If the compatibility module fails, query the native REST API v2:

```bash
curl -s "https://eth.blockscout.com/api/v2/smart-contracts/0xa9fd64b5095d626f5a3a67e6db7fb766345f8092"
```

This returns a richer JSON containing:
- `verified_at`
- `compiler_version`
- `source_code` (contains the raw Solidity or multi-file JSON config)
- `abi`

---

## 3. Custom EVM Chain Explorers (Onyx, etc.)

Many custom EVM L2s use customized Blockscout instances or custom API wrappers.

**Onyx Chain Example:**
```bash
curl -s "https://explorer.onyx.org/api?module=contract&action=getsourcecode&address=0xA553a603e2f84fEa6c1fc225E0945FE176C72F74"
```

If the contract contains multiple source files (OpenZeppelin imports), they are returned inside the `AdditionalSources` array within the `result[0]` object.

---

## 4. Python Automation Helper

Use this script to pull and organize multi-file verified source contracts to `/tmp/contracts/`:

```python
import urllib.request
import json
import os

def fetch_source(address, api_url):
    url = f"{api_url}?module=contract&action=getsourcecode&address={address}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r:
        res = json.loads(r.read().decode('utf-8'))
        if res.get('status') == '1' and res.get('result'):
            result = res['result'][0]
            name = result.get('ContractName', 'Contract')
            source = result.get('SourceCode', '')
            additional = result.get('AdditionalSources', [])
            
            os.makedirs(f"/tmp/contracts/{name}", exist_ok=True)
            
            # Save main file
            with open(f"/tmp/contracts/{name}/{name}.sol", "w") as f:
                f.write(source)
                
            # Save imports
            for src in additional:
                filename = src.get('Filename', '').replace('/', '_')
                with open(f"/tmp/contracts/{name}/{filename}", "w") as f:
                    f.write(src.get('SourceCode', ''))
            print(f"[+] Saved {name} and {len(additional)} additional files")
        else:
            print(f"[-] API Error: {res.get('message')}")
```
