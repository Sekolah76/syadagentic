# 9router Model Selection (for in-script LLM gen) — HARD-WON

When using 9router (`http://127.0.0.1:20128/v1/chat/completions`) for content generation from a Python script (e.g. reply generation, comment crafting), the `model` field matters and the response format is non-standard.

## Model Picks

| Model | Status | Why |
|-------|--------|-----|
| `kr/claude-sonnet-4.5` | ❌ 404 not found (2026-07-02) | OpenRouter/9router returns 404. Endpoint dead. |
| `ag/gemini-3-flash-agent` | ✓ Active (steered) | Swapped on 2026-07-02. Needs clean Regex strip to bypass formatting traps (e.g. `**Agreement:**` or lists). |
| `kr/claude-opus-4.7` | ✓ clean | Slower, higher quality. Use when single-shot quality > throughput. |
| `ag/gemini-3.1-pro-low` | ✓ clean | Cheaper alternative for high-volume gen. |

## Reasoning-Model Leak Symptoms

Content field contains meta-commentary instead of the requested reply:
- `"Let's look closer. The instruction:..."`
- `"The user wants me to..."`
- `"I need to generate a reply that..."`
- Empty content with `completion_tokens_details.reasoning_tokens: 47`

**Always verify with 3 test gens before deploying.** If output has those phrases, swap to a non-reasoning model immediately.

## Formatting Traps & Regex Cleanup
Models like Gemini can return formatted Markdown bullet lists or bold metadata tags. Ensure python scripts strip these out:
```python
text = re.sub(r'^\s*(Start|Agreement|\*\*|\*).*?:\s*', '', text)
text = text.replace('\n', ' ')
text = re.sub(r' +', ' ', text)
```

## SSE Streaming Default

9router responds with `Content-Type: text/event-stream` by default, NOT `application/json`. Your `json.loads(response.read())` will fail with:

```
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

Because the body is:
```
data: {"id":"...","choices":[{"delta":{"role":"assistant"}}]}

data: {"id":"...","choices":[{"delta":{"content":"wah"}}]}

data: {"id":"...","choices":[{"delta":{"content":" gue"}}]}

data: [DONE]
```

## Defensive Parser (Dual JSON/SSE Handler)

Set `"stream": False` in payload as a hint, but ALWAYS parse defensively — some models stream even when asked not to:

```python
def _parse_router_response(raw: bytes) -> dict:
    body = raw.decode('utf-8', errors='replace').strip()
    if not body:
        raise ValueError("empty response body")
    # Plain JSON?
    if body.startswith('{'):
        return json.loads(body)
    # SSE: collect all delta.content chunks
    content_parts = []
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
        if delta.get('content'):
            content_parts.append(delta['content'])
        # Also handle non-streaming-but-chunked case
        msg = choices[0].get('message', {})
        if msg.get('content'):
            content_parts.append(msg['content'])
    if not content_parts:
        raise ValueError("no content in stream")
    return {
        "choices": [{
            "message": {"role": "assistant", "content": ''.join(content_parts)}
        }]
    }
```

Use this for ANY 9router script call. Reference impl: `scripts/threads_content_gen.py` in this skill.

## Quick Probe to List Available Models

```bash
curl -s http://127.0.0.1:20128/v1/models | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"
```

Sample output (2026-06-30): `MIMO`, `GEMINI`, `KG`, `ev/evomap-claude-opus-4-7`, `ev/evomap-gpt-5.5`, `mimo/mimo-v2.5-pro`, `kr/claude-sonnet-4.5`, `kr/claude-opus-4.8`, `kr/claude-opus-4.7`, `kr/claude-opus-4.6`, `ag/gemini-3-flash-agent`, `ag/gemini-3.5-flash-low`, `ag/gemini-pro-agent`, `ag/gemini-3.1-pro-low`, `ag/claude-sonnet-4-6`, `ag/claude-opus-4-6-thinking`, `ag/gpt-oss-120b-medium`, `ag/gemini-3-flash`.

NB: `groq/*`, `openai/*`, `anthropic/*` raw model names are NOT routable through 9router. Stick to the prefixed namespace shown by `/v1/models`.
