"""
threads_content_gen.py — Per-reply LLM generation via 9router.
Story-mode soft reply (empathy first, no hard sell).
"""
import json
import re
import random
import urllib.request
import os
import sys
from pathlib import Path

# Story-mode helpers
sys.path.insert(0, str(Path.home() / ".hermes/scripts"))
try:
    from threads_story_engine import build_story_reply_prompt, story_reply_fallback
except Exception:
    build_story_reply_prompt = None
    story_reply_fallback = None

# 9router local proxy
ROUTER_URL = "http://127.0.0.1:20128/v1/chat/completions"
# Prefer fast non-reasoning ID-friendly model
MODEL = "ag/gemini-3-flash-agent"

EMOJI_POOL = ["✨", "🔥", "💯", "😭", "🥹", "🫶", "👌", "✅", "💖", "🤝",
              "😩", "❤️", "👏", "🙌", "💕", "🌸", "💅", "💗", "😍", "🤤"]


def _parse_router_response(raw: bytes) -> dict:
    """9router defaults to SSE. Parse either JSON or SSE stream."""
    body = raw.decode('utf-8', errors='replace').strip()
    if not body:
        raise ValueError("empty response body")
    # Plain JSON?
    if body.startswith('{'):
        return json.loads(body)
    # SSE: collect all chunks, reconstruct final message
    content_parts = []
    final_chunk = None
    for line in body.split('\n'):
        line = line.strip()
        if not line.startswith('data:'):
            continue
        data = line[5:].strip()
        if data == '[DONE]':
            break
        try:
            obj = json.loads(data)
        except json.JSONDecodeError:
            continue
        choices = obj.get('choices', [])
        if not choices:
            continue
        delta = choices[0].get('delta', {})
        if 'content' in delta and delta['content']:
            content_parts.append(delta['content'])
        # Also handle non-streaming-but-chunked case
        msg = choices[0].get('message', {})
        if msg.get('content'):
            content_parts.append(msg['content'])
        final_chunk = obj
    if not content_parts:
        raise ValueError(f"no content in stream (final_chunk: {final_chunk})")
    return {
        "choices": [{
            "message": {"role": "assistant", "content": ''.join(content_parts)}
        }]
    }


def _load_history():
    """Load recent replies for dedup."""
    hist_file = os.path.expanduser("~/.hermes/state/threads_reply_history.jsonl")
    if not os.path.exists(hist_file):
        return []
    try:
        with open(hist_file) as f:
            entries = [json.loads(line) for line in f if line.strip()]
        return [e.get("comment", "") for e in entries[-50:]]
    except (json.JSONDecodeError, IOError):
        return []


def _too_similar(new_text: str, recent: list, threshold: float = 0.7) -> bool:
    """Simple word-overlap similarity (cheap, no embeddings needed)."""
    new_words = set(re.findall(r'\w+', new_text.lower()))
    if len(new_words) < 4:
        return False
    for old in recent:
        old_words = set(re.findall(r'\w+', old.lower()))
        if not old_words:
            continue
        overlap = len(new_words & old_words) / max(len(new_words), len(old_words))
        if overlap > threshold:
            return True
    return False


def _add_typo(text: str) -> str:
    """30% chance: insert common Indo typo (not for the product/url part)."""
    if random.random() > 0.30:
        return text
    typos = {
        "yang": "yg", "banget": "bgt", "aja": "aj", "udah": "udh",
        "engga": "ga", "enggak": "gak", "bukan": "bkn", "juga": "jg",
        "kayak": "kyk", "tapi": "tp", "kalo": "kalo", "gimana": "gmn"
    }
    for full, short in typos.items():
        if full in text.lower():
            return re.sub(full, short, text, count=1, flags=re.IGNORECASE)
    return text


def generate_reply(product: str, url: str, op_text: str = "") -> str:
    """
    Generate single contextual STORY-MODE reply via 9router.
    Empati / lanjut cerita dulu, soft product, no hard sell.
    Falls back to story templates if API fails.
    """
    clean_product = re.sub(r'\d+\s*(g|gr|ml|g\b).*', '', product).strip()[:40]
    emoji = random.choice(EMOJI_POOL)

    if build_story_reply_prompt:
        system_prompt, user_prompt = build_story_reply_prompt(op_text, product, url)
    else:
        op_snippet = (op_text or "")[:200]
        system_prompt = (
            "Lo gen-z Indo di Threads. Reply kayak temen curhat, BUKAN seller. "
            "8-18 kata. Empati dulu. Soft product max 1x. End with plain url. No hard sell."
        )
        user_prompt = (
            f'Post OP: "{op_snippet}"\nProduk soft: {clean_product}\nURL: {url}\n'
            "1 baris story-mode. End with url."
        )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 1.05,
        "max_tokens": 220,
        "top_p": 0.95,
        "stream": False
    }

    hard_sell = (
        "cek sekarang", "beli di sini", "flash sale", "terbaik", "rekomendasi",
        "wajib coba", "limited", "diskon besar", "order sekarang"
    )

    try:
        req = urllib.request.Request(
            ROUTER_URL,
            data=json.dumps(payload).encode(),
            method="POST",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            resp = _parse_router_response(r.read())
        text = resp["choices"][0]["message"]["content"].strip()

        text = re.sub(r'^\s*(Start|Agreement|\*\*|\*|Reply|Balasan).*?:\s*', '', text, flags=re.I)
        text = text.replace('\n', ' ')
        text = re.sub(r' +', ' ', text)
        text = text.strip('"\'')

        # Drop hard-sell generations
        low = text.lower()
        if any(h in low for h in hard_sell):
            raise ValueError("hard_sell_detected")

        if url not in text:
            text = f"{text} {url}"
        if not any(e in text for e in EMOJI_POOL):
            text = text.replace(url, f"{emoji} {url}", 1)
        text = _add_typo(text)

        recent = _load_history()
        if _too_similar(text, recent):
            payload["temperature"] = 1.25
            req = urllib.request.Request(
                ROUTER_URL,
                data=json.dumps(payload).encode(),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                resp = _parse_router_response(r.read())
            text = resp["choices"][0]["message"]["content"].strip('"\'')
            text = text.replace('\n', ' ')
            if url not in text:
                text = f"{text} {url}"
            if any(h in text.lower() for h in hard_sell):
                raise ValueError("hard_sell_retry")

        return text

    except Exception as e:
        print(f"  [content_gen] LLM failed ({type(e).__name__}: {str(e)[:60]}), story fallback")
        if story_reply_fallback:
            return story_reply_fallback(product, url)
        templates = [
            f"ih iya bgt, gw juga gitu… belakangan nemu {clean_product} yang nyambung {url}",
            f"relate banget. dulu overthinking mulu, skrg lebih tenang {emoji} {url}",
            f"sama, gw jg pernah. soft aja ya: {clean_product} {url}",
            f"real talk, case gw mirip. save dulu biar ga ilang {emoji} {url}",
            f"ceritanya nyambung. yang bantu gw: {clean_product} {url}",
        ]
        return random.choice(templates)


if __name__ == "__main__":
    # Test
    print("=== Sample generations ===")
    for op_text in [
        "udah nyari skincare anti jerawat ampe pusing belom nemu yg cocok",
        "rekomendasi parfum buat cowo dong yang awet",
        "rambut gue rontok parah huhu",
    ]:
        reply = generate_reply(
            product="Skintific 5x Serum",
            url="https://s.shopee.co.id/xyz123",
            op_text=op_text
        )
        print(f"\nOP: {op_text}")
        print(f"Reply: {reply}")
