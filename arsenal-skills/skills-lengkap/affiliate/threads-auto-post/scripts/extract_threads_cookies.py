#!/usr/bin/env python3
"""extract_threads_cookies.py — Extract IG/Threads cookies from Chrome Profile 16."""
import browser_cookie3, json, os, sys, shutil, tempfile, re, urllib.request
from pathlib import Path

COOKIE_PATH = Path.home() / "instagram_cookies.json"
THREADS_PATH = Path.home() / "threads_cookies.json"
P16 = Path.home() / "Library/Application Support/Google/Chrome/Profile 16/Cookies"
P16_DEFAULT = Path.home() / "Library/Application Support/Google/Chrome/Profile 16/Default/Cookies"

def load(cookie_file, domain):
    tmp = Path(tempfile.mkstemp(suffix=".db")[1])
    shutil.copy2(cookie_file, tmp)
    try:
        return {c.name: c.value for c in browser_cookie3.chrome(cookie_file=str(tmp), domain_name=domain)}
    finally:
        tmp.unlink(missing_ok=True)

def who(cookies):
    if "sessionid" not in cookies:
        return None
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
    req = urllib.request.Request(
        "https://www.instagram.com/api/v1/accounts/edit/web_form_data/",
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "Cookie": cookie_str,
            "X-IG-App-ID": "936619743392459",
            "X-CSRFToken": cookies.get("csrftoken", ""),
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            body = r.read().decode("utf-8", "ignore")
        m = re.search(r'"username"\s*:\s*"([^"]+)"', body)
        return m.group(1) if m else None
    except Exception as e:
        return f"err:{e}"

def main():
    try:
        src = P16 if P16.exists() else None
        if not src:
            print("❌ **Threads — Cookie Refresh**\n\n| Status | Keterangan |\n| :--- | :--- |\n| ❌ Gagal | Profile 16 Cookies tidak ditemukan. |")
            sys.exit(1)
        ig = load(src, ".instagram.com")
        th = load(src, ".threads.com")
        # merge Default threads cookies if present
        if P16_DEFAULT.exists():
            th2 = load(P16_DEFAULT, ".threads.com")
            for k, v in th2.items():
                if v and (k not in th or not th.get(k)):
                    th[k] = v
        if "sessionid" not in ig:
            print("❌ **Threads — Cookie Refresh**\n\n| Status | Keterangan |\n| :--- | :--- |\n| ❌ Gagal | sessionid IG kosong di Profile 16. Login dulu. |")
            sys.exit(1)
        user = who(ig)
        COOKIE_PATH.write_text(json.dumps(ig, indent=2))
        THREADS_PATH.write_text(json.dumps(th, indent=2))
        ok = isinstance(user, str) and user and not user.startswith("err:")
        if ok:
            print(f"✅ **Threads — Cookie Refresh**\n\n| Status | Keterangan |\n| :--- | :--- |\n| ✅ Berhasil | user=`{user}` · IG {len(ig)} cookie · Threads {len(th)} cookie · Profile 16. |")
            sys.exit(0)
        print(f"❌ **Threads — Cookie Refresh**\n\n| Status | Keterangan |\n| :--- | :--- |\n| ❌ Weak | Cookie tersimpan tapi verify user gagal: `{user}`. |")
        sys.exit(1)
    except Exception as e:
        print(f"❌ **Threads — Cookie Refresh**\n\n| Status | Keterangan |\n| :--- | :--- |\n| ❌ Error | {e} |")
        sys.exit(1)

if __name__ == "__main__":
    main()
