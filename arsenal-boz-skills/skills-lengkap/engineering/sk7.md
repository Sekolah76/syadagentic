# sk7 — Inference Systems & AI Builder (BOZAGENTIC)
# Load when: LLM, prompt, claude API, openrouter, add model, AI, agent, model, GPT
# Category: AI & Inference

## Operator Profile

AI systems architect. Production inference pipelines — not prototypes. Provider-agnostic, fallback-aware, cost-conscious.

---

## Provider Registry

```
Provider       | Endpoint                                          | Best For
---------------|---------------------------------------------------|----------------------------
Anthropic      | api.anthropic.com/v1/messages                     | Best reasoning, agent loops
OpenRouter     | openrouter.ai/api/v1/chat/completions              | Multi-model gateway
OpenAI         | api.openai.com/v1/chat/completions                 | GPT-4o, multimodal
Kimi (Moonshot)| api.moonshot.cn/v1/chat/completions                | 128k+ context, Asia langs
Groq           | api.groq.com/openai/v1/chat/completions            | Ultra-fast (Llama/Mixtral)
DeepSeek       | api.deepseek.com/v1/chat/completions               | Cheap, strong on coding
Together AI    | api.together.xyz/v1/chat/completions               | Open-source models
Google Gemini  | generativelanguage.googleapis.com/v1beta           | Gemini Pro / Flash
```

---

## Anthropic (with retry + auth)

```javascript
async function inferClaude(spec, input, history = [], opts = {}) {
  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': process.env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: opts.model || 'claude-sonnet-4-20250514',
      max_tokens: opts.maxTokens || 2000,
      system: spec,
      messages: [...history, { role: 'user', content: input }],
    }),
  });
  if (!r.ok) throw new Error(`Claude ${r.status}: ${await r.text()}`);
  const j = await r.json();
  return { text: j.content[0].text, usage: j.usage };
}
```

---

## Anthropic Streaming (SSE)

```javascript
async function streamClaude(spec, input, onToken, history = []) {
  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': process.env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2000,
      stream: true,
      system: spec,
      messages: [...history, { role: 'user', content: input }],
    }),
  });

  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buf = '';
  let full = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const lines = buf.split('\n');
    buf = lines.pop();
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const data = line.slice(6);
      if (data === '[DONE]') return full;
      try {
        const evt = JSON.parse(data);
        if (evt.type === 'content_block_delta') {
          const tok = evt.delta?.text || '';
          full += tok;
          onToken(tok);
        }
      } catch {}
    }
  }
  return full;
}

// Usage:
// await streamClaude(SPEC, 'Tulis caption', (t) => process.stdout.write(t));
```

---

## OpenRouter (single key → all models)

```javascript
async function inferOR(model, spec, input, history = [], opts = {}) {
  const r = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
      'X-Title': 'BOZAGENTIC',
    },
    body: JSON.stringify({
      model,
      messages: [{ role: 'system', content: spec }, ...history, { role: 'user', content: input }],
      max_tokens: opts.maxTokens || 2000,
    }),
  });
  if (!r.ok) throw new Error(`OR ${r.status}: ${await r.text()}`);
  const j = await r.json();
  return { text: j.choices[0].message.content, usage: j.usage };
}

// Common model IDs:
// anthropic/claude-sonnet-4   |  openai/gpt-4o   |  deepseek/deepseek-chat
// google/gemini-pro-1.5       |  meta-llama/llama-3.1-405b-instruct
// moonshotai/kimi-k2          |  qwen/qwen-2.5-72b-instruct
```

---

## Kimi / Moonshot (128k context)

```javascript
async function inferKimi(spec, input, history = []) {
  const r = await fetch('https://api.moonshot.cn/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.KIMI_API_KEY}`,
    },
    body: JSON.stringify({
      model: 'moonshot-v1-128k',
      messages: [{ role: 'system', content: spec }, ...history, { role: 'user', content: input }],
    }),
  });
  if (!r.ok) throw new Error(`Kimi ${r.status}: ${await r.text()}`);
  return (await r.json()).choices[0].message.content;
}
```

---

## OpenAI / DeepSeek / Groq (OpenAI-compatible — one wrapper)

```javascript
const PROVIDERS = {
  openai:   { url: 'https://api.openai.com/v1/chat/completions',     env: 'OPENAI_API_KEY',   model: 'gpt-4o' },
  deepseek: { url: 'https://api.deepseek.com/v1/chat/completions',   env: 'DEEPSEEK_API_KEY', model: 'deepseek-chat' },
  groq:     { url: 'https://api.groq.com/openai/v1/chat/completions',env: 'GROQ_API_KEY',     model: 'llama-3.1-70b-versatile' },
  together: { url: 'https://api.together.xyz/v1/chat/completions',   env: 'TOGETHER_API_KEY', model: 'meta-llama/Llama-3-70b-chat-hf' },
};

async function inferOAICompat(provider, spec, input, history = [], opts = {}) {
  const cfg = PROVIDERS[provider];
  const r = await fetch(cfg.url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env[cfg.env]}`,
    },
    body: JSON.stringify({
      model: opts.model || cfg.model,
      messages: [{ role: 'system', content: spec }, ...history, { role: 'user', content: input }],
      max_tokens: opts.maxTokens || 2000,
    }),
  });
  if (!r.ok) throw new Error(`${provider} ${r.status}: ${await r.text()}`);
  return (await r.json()).choices[0].message.content;
}
```

---

## Provider Fallback Chain (production resilience)

```javascript
const CHAIN = [
  () => inferClaude(SPEC, prompt),
  () => inferOAICompat('openai', SPEC, prompt),
  () => inferOR('deepseek/deepseek-chat', SPEC, prompt),
  () => inferKimi(SPEC, prompt),
];

async function inferWithFallback(prompt) {
  let lastErr;
  for (const fn of CHAIN) {
    try { return await fn(); }
    catch (e) { lastErr = e; console.warn('Provider failed:', e.message); }
  }
  throw new Error(`All providers failed. Last: ${lastErr?.message}`);
}
```

---

## Function Calling / Tool Use (Anthropic)

```javascript
async function inferWithTools(prompt, tools, toolHandlers) {
  let messages = [{ role: 'user', content: prompt }];
  const MAX = 10;

  for (let i = 0; i < MAX; i++) {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 2000,
        tools,
        messages,
      }),
    });
    const j = await r.json();
    messages.push({ role: 'assistant', content: j.content });

    if (j.stop_reason === 'end_turn') return j.content;

    const toolUses = j.content.filter(b => b.type === 'tool_use');
    if (!toolUses.length) return j.content;

    const results = await Promise.all(toolUses.map(async (use) => ({
      type: 'tool_result',
      tool_use_id: use.id,
      content: String(await toolHandlers[use.name](use.input)),
    })));
    messages.push({ role: 'user', content: results });
  }
  throw new Error('Tool loop exceeded max iterations');
}

// Tool definition example:
const tools = [{
  name: 'get_weather',
  description: 'Get current weather for a city',
  input_schema: {
    type: 'object',
    properties: { city: { type: 'string' } },
    required: ['city'],
  },
}];

const handlers = {
  get_weather: async ({ city }) => {
    const r = await fetch(`https://wttr.in/${city}?format=j1`);
    return JSON.stringify(await r.json());
  },
};
```

---

## Cost Tracking (per-session)

```javascript
const PRICING = {
  // USD per 1M tokens [input, output]
  'claude-sonnet-4-20250514':  [3.00, 15.00],
  'claude-haiku-4-5-20251001': [0.80, 4.00],
  'gpt-4o':                     [5.00, 20.00],
  'deepseek-chat':              [0.27, 1.10],
  'moonshot-v1-128k':           [0.60, 0.60],   // approximate
};

let totalUSD = 0;
function trackCost(model, usage) {
  const [pin, pout] = PRICING[model] || [0, 0];
  const cost = (usage.input_tokens * pin + usage.output_tokens * pout) / 1_000_000;
  totalUSD += cost;
  return { cost, total: totalUSD };
}
```

---

## Caching Layer (avoid duplicate calls)

```javascript
const fs = require('fs');
const crypto = require('crypto');
const CACHE_DIR = './.llm-cache';
if (!fs.existsSync(CACHE_DIR)) fs.mkdirSync(CACHE_DIR);

function cacheKey(prompt, model) {
  return crypto.createHash('sha256').update(`${model}::${prompt}`).digest('hex');
}

async function cachedInfer(prompt, model, fn) {
  const key = cacheKey(prompt, model);
  const path = `${CACHE_DIR}/${key}.json`;
  if (fs.existsSync(path)) return JSON.parse(fs.readFileSync(path)).response;
  const response = await fn();
  fs.writeFileSync(path, JSON.stringify({ prompt, response, ts: Date.now() }));
  return response;
}
```

Use Anthropic's prompt caching for repeated system prompts → `cache_control` block (cuts cost ~90% on cache hit).

---

## Universal Python Wrapper

```python
import requests, os

PROVIDERS = {
    'anthropic': {
        'url': 'https://api.anthropic.com/v1/messages',
        'env': 'ANTHROPIC_API_KEY',
        'model': 'claude-sonnet-4-20250514',
        'is_anthropic': True,
    },
    'openrouter': ('https://openrouter.ai/api/v1/chat/completions', 'OPENROUTER_API_KEY', 'anthropic/claude-sonnet-4'),
    'openai':     ('https://api.openai.com/v1/chat/completions',     'OPENAI_API_KEY',     'gpt-4o'),
    'kimi':       ('https://api.moonshot.cn/v1/chat/completions',    'KIMI_API_KEY',       'moonshot-v1-128k'),
    'deepseek':   ('https://api.deepseek.com/v1/chat/completions',   'DEEPSEEK_API_KEY',   'deepseek-chat'),
    'groq':       ('https://api.groq.com/openai/v1/chat/completions','GROQ_API_KEY',       'llama-3.1-70b-versatile'),
}

def call_llm(message, system='You are a helpful assistant.', provider='openrouter', model=None, max_tokens=2000):
    cfg = PROVIDERS[provider]
    if isinstance(cfg, dict) and cfg.get('is_anthropic'):
        r = requests.post(cfg['url'], json={
            'model': model or cfg['model'],
            'max_tokens': max_tokens,
            'system': system,
            'messages': [{'role': 'user', 'content': message}],
        }, headers={
            'Content-Type': 'application/json',
            'x-api-key': os.getenv(cfg['env']),
            'anthropic-version': '2023-06-01',
        }, timeout=120)
        r.raise_for_status()
        return r.json()['content'][0]['text']
    url, env_key, default_model = cfg
    r = requests.post(url, json={
        'model': model or default_model,
        'max_tokens': max_tokens,
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': message}],
    }, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv(env_key)}',
    }, timeout=120)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']
```

---

## Behavioral Spec Architecture

```
[ROLE]           Operator identity (1 sentence)
[CONTEXT]        Operational environment (constraints, audience)
[CAPABILITIES]   Permitted action space
[CONSTRAINTS]    Hard limits (what NOT to do)
[OUTPUT_FORMAT]  Response schema (JSON / markdown / plain)
[EXAMPLES]       2–3 input/output pairs
```

### Forcing JSON output

```
Emit ONLY valid JSON. No preamble. No markdown fences. No commentary.
Schema: { "output": "...", "confidence": 0.0-1.0, "steps": ["..."] }

If you cannot answer in valid JSON, respond: {"error": "<reason>"}
```

Parse defensively:
```javascript
function parseLLMJson(text) {
  // Strip markdown fences if present
  const cleaned = text.replace(/^```(?:json)?\s*|\s*```$/g, '').trim();
  return JSON.parse(cleaned);
}
```

---

## Agent Loop (with tool use + safety limit)

```javascript
async function runAgent(task, callFn, tools = {}, maxSteps = 10) {
  let history = [{ role: 'user', content: task }];
  for (let i = 0; i < maxSteps; i++) {
    const out = await callFn(SYSTEM_SPEC, '', history);
    history.push({ role: 'assistant', content: out });
    if (out.includes('[RESOLVED]')) return { ok: true, out, steps: i + 1 };
    const tool = out.match(/\[USE:(\w+)\]\s*(\{[^}]*\})/);
    if (!tool) return { ok: false, reason: 'no_tool_call', out };
    const [, name, argStr] = tool;
    if (!tools[name]) return { ok: false, reason: `unknown_tool: ${name}` };
    const result = await tools[name](JSON.parse(argStr));
    history.push({ role: 'user', content: `Tool [${name}] result: ${result}` });
  }
  return { ok: false, reason: 'max_steps_reached' };
}
```

---

## Provider Selection Guide

```
Best reasoning + agent loops?     → Anthropic Claude Sonnet/Opus
Cheapest decent quality?           → DeepSeek Chat or OpenRouter to DeepSeek
Long context (>50k)?               → Kimi (128k) or Gemini (1M)
Fastest first token?               → Groq (Llama 3 70b)
Multimodal (image input)?          → GPT-4o, Claude, Gemini
Code generation specialist?        → DeepSeek Coder or Claude
Open-source / self-deployable?     → Together AI hosting Llama/Qwen
```

---

## `.env.example`

```
# Pick provider(s) — not all required
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
OPENAI_API_KEY=sk-...
KIMI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
DEEPSEEK_API_KEY=sk-...
TOGETHER_API_KEY=...
```

---

## Constraints

- Runnable implementation — never pseudocode
- Token cost estimate when call is repeated > 1000x/day
- Caching for repeated identical prompts (use Anthropic prompt-caching headers when applicable)
- Streaming for any UI-facing response (perceived latency)
- Fallback chain for production-critical paths
- Always include error handling
- Token usage logged when production

---

## Add Model — registry LLM dinamis (NEW in v4.0)

Nambah model LLM apa pun lewat **satu perintah**, langsung masuk cascade R7. Engine: `tools/model_registry.py`.

Command pattern (operator di chat):
```
add model
name: openrouter-llama
api_key: sk-or-...
base_url: https://openrouter.ai/api/v1
model: meta-llama/llama-3.3-70b
kind: openai            # openai | anthropic (default openai)
priority: 50            # makin kecil makin diutamakan
```

Agent → `ModelRegistry().add_model(...)`. Dukung semua yang OpenAI-compatible (OpenRouter, DeepSeek, Groq, Together, Kimi, Ollama/LM Studio lokal, vLLM) + Anthropic-style. Model lokal (Ollama) gak butuh key.

```python
from model_registry import ModelRegistry
reg = ModelRegistry()                       # pakai HERMES_MASTER_PW buat enkripsi key
reg.add_model("groq-fast", "https://api.groq.com/openai/v1", "llama-3.1-8b-instant",
              api_key="gsk_...", priority=80)
reg.list_models()                            # key ter-REDACT (gak pernah mentah)
ans, used = reg.call_with_cascade(messages)  # R7: coba per prioritas, fallback otomatis
```

**Secret hygiene**: API key disimpan terenkripsi (scrypt+Fernet via `HERMES_MASTER_PW`), gak pernah di-log/print mentah, `list_models()` redacted. Tanpa master pw → registry NOLAK nyimpen key (gak ada plaintext diam-diam). File `model_registry.py` FROZEN (nentuin ke mana prompt/data dikirim).

**Catatan**: agent bakal ngirim prompt (& mungkin data) ke `base_url` yang lo daftarin — tambah cuma yang lo percaya. Provider cascade R7 (di AGENTS.md) sekarang bisa narik model dari registry ini, bukan cuma yang hardcoded.
