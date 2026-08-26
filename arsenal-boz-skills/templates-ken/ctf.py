#!/usr/bin/env python3
"""
tools/ctf.py — CTF / Whitehat Toolkit  (v4.2, sk32)

Helper buat ngerjain CTF (legal, reward/bug-bounty oriented): triage kategori,
multi-decode (base64/hex/rot13/url/binary), klasik crypto (caesar brute, single-byte
XOR, repeating-key XOR/vigenere), identifikasi hash, dan ekstraksi flag.

SCOPE: CTF platform & target yang lo punya izin (HTB/THM/CTFd/bug-bounty in-scope).
Tool ini stdlib-only & pasif (gak nyerang apa pun) — analisis & encoding doang.
Eksploitasi aktif (web/pwn) didelegasi ke skill sk32 + engine yang relevan, dengan izin.
"""
from __future__ import annotations

import base64
import binascii
import codecs
import re
import string
from dataclasses import dataclass
from typing import Optional

FLAG_RE = re.compile(r"[A-Za-z0-9_]{2,20}\{[^}]{1,200}\}")


# ───────────────────── flag & triage ─────────────────────
def find_flags(text: str) -> list:
    """Cari pola flag umum: NAME{...}. Return list string flag."""
    return FLAG_RE.findall(text or "")


CATEGORY_HINTS = {
    "web": ["http", "cookie", "sql", "xss", "jwt", "php", "flask", "ssrf", "lfi", "idor"],
    "pwn": ["buffer", "overflow", "rop", "libc", "shellcode", "gdb", "stack", "heap", "ret2"],
    "crypto": ["rsa", "aes", "xor", "cipher", "encrypt", "modulus", "nonce", "ecb", "padding"],
    "reverse": ["binary", "disassemble", "ghidra", "ida", "decompile", "elf", "strings"],
    "forensics": ["pcap", "wireshark", "memory dump", "steghide", "exif", "carve", "volatility"],
    "osint": ["username", "geolocation", "metadata", "social", "whois", "recon"],
}


def triage(description: str) -> list:
    """Tebak kategori CTF dari deskripsi soal. Return [(kategori, skor)] urut menurun."""
    d = (description or "").lower()
    scores = {}
    for cat, kws in CATEGORY_HINTS.items():
        score = sum(1 for kw in kws if kw in d)
        if score:
            scores[cat] = score
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)


# ───────────────────── multi-decode ─────────────────────
def _printable_ratio(b: bytes) -> float:
    if not b:
        return 0.0
    printable = set(bytes(string.printable, "ascii"))
    return sum(1 for c in b if c in printable) / len(b)


@dataclass
class DecodeAttempt:
    method: str
    value: str
    printable: float


def try_decode(data: str) -> list:
    """Coba beberapa decoding umum, return yang menghasilkan teks 'masuk akal'.

    Diurut dari yang paling printable. Berguna buat ngupas layer encoding CTF.
    """
    s = (data or "").strip()
    out = []

    def add(method, raw):
        try:
            txt = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
        except Exception:  # noqa: BLE001
            return
        b = txt.encode("utf-8", "replace")
        out.append(DecodeAttempt(method, txt, round(_printable_ratio(b), 3)))

    # base64
    try:
        pad = s + "=" * (-len(s) % 4)
        add("base64", base64.b64decode(pad, validate=False))
    except Exception:  # noqa: BLE001
        pass
    # hex
    try:
        h = s.replace(" ", "")
        if len(h) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", h):
            add("hex", binascii.unhexlify(h))
    except Exception:  # noqa: BLE001
        pass
    # rot13
    add("rot13", codecs.decode(s, "rot_13"))
    # url-decode
    try:
        from urllib.parse import unquote
        u = unquote(s)
        if u != s:
            add("url", u)
    except Exception:  # noqa: BLE001
        pass
    # binary (space-separated bytes)
    try:
        bits = s.split()
        if bits and all(re.fullmatch(r"[01]{8}", x) for x in bits):
            add("binary", bytes(int(x, 2) for x in bits))
    except Exception:  # noqa: BLE001
        pass
    # decimal ascii codes
    try:
        nums = s.split()
        if nums and all(x.isdigit() and 0 <= int(x) <= 255 for x in nums):
            add("ascii_dec", bytes(int(x) for x in nums))
    except Exception:  # noqa: BLE001
        pass

    out.sort(key=lambda d: d.printable, reverse=True)
    return out


# ───────────────────── classic crypto ─────────────────────
def caesar_bruteforce(text: str) -> list:
    """Semua 26 shift Caesar. Return [(shift, hasil)]."""
    res = []
    for shift in range(26):
        out = []
        for ch in text:
            if ch.isupper():
                out.append(chr((ord(ch) - 65 - shift) % 26 + 65))
            elif ch.islower():
                out.append(chr((ord(ch) - 97 - shift) % 26 + 97))
            else:
                out.append(ch)
        res.append((shift, "".join(out)))
    return res


def xor_single_byte(data: bytes) -> list:
    """Brute single-byte XOR, return [(key, plaintext, score)] urut skor (englishness)."""
    common = set(b"etaoinshrdlu ETAOIN")
    results = []
    for key in range(256):
        dec = bytes(b ^ key for b in data)
        score = sum(1 for c in dec if c in common) / max(1, len(dec))
        results.append((key, dec.decode("latin-1"), round(score, 3)))
    results.sort(key=lambda r: r[2], reverse=True)
    return results[:5]


def xor_repeating(data: bytes, key: bytes) -> bytes:
    """XOR repeating-key (Vigenere-style). Encrypt == decrypt."""
    if not key:
        raise ValueError("key kosong")
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


# ───────────────────── hash identify ─────────────────────
def identify_hash(h: str) -> list:
    """Tebak tipe hash dari panjang/charset. Return kandidat."""
    h = (h or "").strip()
    if not re.fullmatch(r"[0-9a-fA-F]+", h):
        if h.startswith("$2"):
            return ["bcrypt"]
        if h.startswith("$argon2"):
            return ["argon2"]
        return ["unknown (non-hex)"]
    by_len = {32: ["MD5", "NTLM"], 40: ["SHA-1"], 56: ["SHA-224"],
              64: ["SHA-256"], 96: ["SHA-384"], 128: ["SHA-512"]}
    return by_len.get(len(h), [f"unknown (hex len {len(h)})"])


if __name__ == "__main__":
    enc = base64.b64encode(b"flag{hello_ctf}").decode()
    print("triage:", triage("RSA modulus and nonce encrypt challenge"))
    for d in try_decode(enc)[:2]:
        print(f"  decode[{d.method}] ({d.printable}): {d.value}")
    print("flags:", find_flags("congrats CTF{multi_layer_decode}"))
    print("hash:", identify_hash("5f4dcc3b5aa765d61d8327deb882cf99"))
