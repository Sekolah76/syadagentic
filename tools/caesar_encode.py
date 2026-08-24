#!/usr/bin/env python3
"""caesar_encode.py — Cipher layer utk frontier bypass (SYADAGENTIC FRONTIER BYPASS #2).
Encode instruksi dgn Caesar cipher — defeats residual policy paling keras.
Usage:
  python caesar_encode.py "your instruction here"            # auto shift 5
  python caesar_encode.py "your instruction here" --shift 13
  python caesar_encode.py --decode "encrypted text" [--shift N]
"""
import argparse, sys

def caesar(text, shift):
    out = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            out.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            out.append(ch)
    return "".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="*", help="teks utk dienkripsi/didekripsi")
    ap.add_argument("--shift", type=int, default=5)
    ap.add_argument("--decode", action="store_true")
    args = ap.parse_args()
    text = " ".join(args.text)
    shift = -args.shift if args.decode else args.shift
    print(caesar(text, shift))

if __name__ == "__main__":
    main()