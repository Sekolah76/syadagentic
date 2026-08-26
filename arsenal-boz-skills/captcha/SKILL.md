---
name: captcha-solver
description: Universal local sidecar anti-bot & captcha solver (Cloudflare Turnstile, Aliyun 2.0, Arkose FunCaptcha, Akamai, BotGuard, PerimeterX, DataDome, AWS WAF, reCAPTCHA, hCaptcha).
category: automation
---

# Universal Captcha & Anti-Bot Solver Suite

Local, harvest-only, zero-cost sidecar solver engine for all major bot-management vendors.

## Supported Providers & Solvers

1. **Cloudflare Turnstile & Interstitial** (`tools/captcha-solver/turnstile/` & `tools/captcha-solver/cloudflare/`)
   - Route intercept & real-page navigation for `cf_clearance` cookie harvesting.
2. **Aliyun Captcha 2.0** (`tools/captcha-solver/aliyun/`)
   - Slide puzzle solver with local ONNX model (`best.onnx`) & quadratic mouse drag curve.
3. **Arkose FunCaptcha** (`tools/captcha-solver/arkose/`)
   - Visual puzzle solver with multi-wave ONNX image classification.
4. **Akamai Bot Manager** (`tools/captcha-solver/akamai/`)
   - Sensor `bmak` telemetry harvester for `_abck` clearance.
5. **Google BotGuard** (`tools/captcha-solver/botguard/`)
   - Polymorphic VM execution for Google OAuth `bgRequest` token extraction.
6. **PerimeterX / HUMAN** (`tools/captcha-solver/perimeterx/`)
   - Press & Hold SHA-256 hashcash Web Worker proof-of-work solver (Harvest `_px3`).
7. **DataDome** (`tools/captcha-solver/datadome/`)
   - Sensor payload harvester for `datadome=` cookie.
8. **AWS WAF** (`tools/captcha-solver/awswaf/`)
   - Silent JS challenge proof-of-work token harvester (`aws-waf-token`).
9. **reCAPTCHA & hCaptcha** (`tools/captcha-solver/recaptcha/` & `tools/captcha-solver/hcaptcha/`)
   - Checkbox, v3 Enterprise, and invisible token solving.

## Usage

```bash
# Run universal solver server
python3 tools/captcha-solver/universal_solver.py

# Or use specific provider module
python3 tools/captcha-solver/turnstile/solve.py --url "<TARGET_URL>" --sitekey "<SITEKEY>"
```
