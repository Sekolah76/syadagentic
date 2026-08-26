# sk4 — Process Orchestration & Bots (BOZAGENTIC)
# Load when: telegram bot, cron, webhook, n8n, automate, bot, otomatis, schedule, jadwal
# Category: Infrastructure & DevOps

## Operator Profile

Automation architect. Production-grade bots, schedulers, webhooks. Anti-fragile by default. Thinks in flows, triggers, retries, idempotency.

---

## Execution Layer Selection

```
Visual orchestration:   Make.com (no-code), n8n (self-hosted, recommended for VPS)
Scheduled execution:    Python/Node + cron, GitHub Actions (free tier)
Persistent process:     Node.js + psk2 OR systemd (production)
Command interface:      Telegram Bot API (lowest setup friction)
                        Discord.js (community bots)
                        WhatsApp Cloud API (business)
Queue / background:     BullMQ (Redis), in-memory queue (simple), SQLite-backed
```

---

## Production Telegram Bot (Node — anti-duplicate, error-recovery)

```javascript
// bot.js
require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');

const TOKEN = process.env.BOT_TOKEN;
const bot = new TelegramBot(TOKEN, { polling: { interval: 300, autoStart: true, params: { timeout: 10 } } });

// CRITICAL: dedupe by message_id (prevents duplicate replies on bot restart / polling overlap)
const seen = new Map();
const SEEN_TTL = 5 * 60 * 1000; // 5 min
setInterval(() => {
  const now = Date.now();
  for (const [k, t] of seen) if (now - t > SEEN_TTL) seen.delete(k);
}, 60 * 1000);

function isDuplicate(msg) {
  const key = `${msg.chat.id}:${msg.message_id}`;
  if (seen.has(key)) return true;
  seen.set(key, Date.now());
  return false;
}

// Wrap send with retry
async function safeSend(chatId, text, opts = {}, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await bot.sendMessage(chatId, text, { parse_mode: 'Markdown', ...opts });
    } catch (e) {
      if (e.response?.body?.error_code === 429) {
        const wait = (e.response.body.parameters?.retry_after || 1) * 1000;
        await new Promise(r => setTimeout(r, wait));
      } else if (i === retries - 1) {
        console.error('Send failed:', e.message);
        throw e;
      } else {
        await new Promise(r => setTimeout(r, 1000 * (i + 1)));
      }
    }
  }
}

// Handlers
bot.onText(/^\/start$/, async (msg) => {
  if (isDuplicate(msg)) return;
  await safeSend(msg.chat.id, '✅ Online.\nKetik /help buat lihat command.');
});

bot.onText(/^\/help$/, async (msg) => {
  if (isDuplicate(msg)) return;
  await safeSend(msg.chat.id, '*Available:*\n/start\n/status\n/run [arg]');
});

bot.onText(/^\/run (.+)/, async (msg, match) => {
  if (isDuplicate(msg)) return;
  const arg = match[1].trim();
  await safeSend(msg.chat.id, `🚀 Executing: \`${arg}\``);
  // ... do work
});

// Catch-all (only for non-command messages)
bot.on('message', async (msg) => {
  if (msg.text?.startsWith('/')) return;  // already handled by onText
  if (isDuplicate(msg)) return;
  await safeSend(msg.chat.id, `Got it: "${msg.text}"`);
});

// Polling error recovery
bot.on('polling_error', (err) => {
  console.error('[polling]', err.code, err.message);
  // 409 = another instance running → exit so psk2 doesn't loop
  if (err.code === 'ETELEGRAM' && err.response?.body?.error_code === 409) {
    console.error('Another bot instance is running. Exiting.');
    process.exit(1);
  }
});

console.log('Bot online.');
```

```
# .env.example
BOT_TOKEN=123456:ABC-DEF...
```

```
# Run with psk2
psk2 start bot.js --name mybot --max-memory-restart 200M
psk2 save
```

---

## Telegram Webhook Mode (production-scale, no polling)

```javascript
// webhook-bot.js
require('dotenv').config();
const express = require('express');
const TelegramBot = require('node-telegram-bot-api');

const TOKEN = process.env.BOT_TOKEN;
const URL = process.env.WEBHOOK_URL;   // https://yourdomain.com
const PORT = process.env.PORT || 3000;

const bot = new TelegramBot(TOKEN);
bot.setWebHook(`${URL}/bot${TOKEN}`);

const app = express();
app.use(express.json());

app.post(`/bot${TOKEN}`, (req, res) => {
  bot.processUpdate(req.body);
  res.sendStatus(200);
});

bot.onText(/\/start/, (msg) => bot.sendMessage(msg.chat.id, 'Hello via webhook'));

app.listen(PORT, () => console.log(`Webhook server on ${PORT}`));
```

Webhook setup needs Nginx → see sk2 for proxy config.

---

## Telegraf (alternative — cleaner middleware API)

```javascript
const { Telegraf } = require('telegraf');
const bot = new Telegraf(process.env.BOT_TOKEN);

bot.use(async (ctx, next) => {
  console.log(`[${ctx.from?.username}] ${ctx.message?.text}`);
  await next();
});

bot.start((ctx) => ctx.reply('Welcome'));
bot.command('status', (ctx) => ctx.reply('🟢 OK'));
bot.on('text', (ctx) => ctx.reply(`Echo: ${ctx.message.text}`));

bot.launch();
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
```

---

## Schedule Patterns

### cron (system-wide)

```bash
crontab -e
# Format: min hour day month dow command
0 8 * * *       /usr/bin/python3 /opt/run/daily.py >> /var/log/run.log 2>&1
0 * * * *       /bin/bash /opt/run/check.sh
*/5 * * * *     /usr/bin/node /opt/run/monitor.js
@reboot         /opt/run/startup.sh
0 3 * * 0       /opt/run/weekly-backup.sh   # Sunday 3am
```

### Node-cron (in-process, for bots that need schedules)

```javascript
const cron = require('node-cron');
cron.schedule('*/15 * * * *', async () => {
  console.log('Running every 15 min');
  // ...
}, { timezone: 'Asia/Jakarta' });
```

### Python APScheduler (when running Python services)

```python
from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler(timezone='Asia/Jakarta')

@sched.scheduled_job('cron', hour=8, minute=0)
def daily(): ...

@sched.scheduled_job('interval', minutes=5)
def heartbeat(): ...

sched.start()
```

---

## Webhook Receiver (FastAPI — production-ready)

```python
import os, hmac, hashlib
from fastapi import FastAPI, Request, HTTPException, Header

app = FastAPI()
SECRET = os.getenv('WEBHOOK_SECRET').encode()

def verify(sig: str, body: bytes) -> bool:
    expected = hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)

@app.post('/webhook')
async def receive(request: Request, x_signature: str = Header(None)):
    body = await request.body()
    if not x_signature or not verify(x_signature, body):
        raise HTTPException(401, "Invalid signature")
    data = await request.json()
    handlers = {
        'payment.success': on_payment,
        'subscription.renewed': on_renewal,
    }
    h = handlers.get(data.get('type'))
    if h: await h(data)
    return {'ack': True}
```

---

## Idempotent Job Pattern (prevents duplicate work)

```javascript
// Simple file-backed idempotency
const fs = require('fs');
const PROCESSED = './.processed.json';
const seen = fs.existsSync(PROCESSED) ? new Set(JSON.parse(fs.readFileSync(PROCESSED))) : new Set();

function alreadyProcessed(id) { return seen.has(id); }
function markProcessed(id) {
  seen.add(id);
  fs.writeFileSync(PROCESSED, JSON.stringify([...seen]));
}

async function job(item) {
  if (alreadyProcessed(item.id)) return;
  await doWork(item);
  markProcessed(item.id);
}
```

For scale: swap Set → Redis SET, or use a column in postgres with UNIQUE constraint.

---

## Worker Queue (in-memory, no Redis)

```javascript
class Queue {
  constructor(concurrency = 3) {
    this.q = [];
    this.running = 0;
    this.concurrency = concurrency;
  }
  add(task) {
    return new Promise((resolve, reject) => {
      this.q.push({ task, resolve, reject });
      this.tick();
    });
  }
  async tick() {
    while (this.running < this.concurrency && this.q.length) {
      const { task, resolve, reject } = this.q.shift();
      this.running++;
      Promise.resolve(task())
        .then(resolve, reject)
        .finally(() => { this.running--; this.tick(); });
    }
  }
}

const q = new Queue(5);
items.forEach(i => q.add(() => process(i)));
```

For durable queues: BullMQ + Redis.

---

## Multi-bot Orchestration (single process, multiple tokens)

```javascript
const TelegramBot = require('node-telegram-bot-api');

const bots = {
  airdrop: new TelegramBot(process.env.AIRDROP_BOT_TOKEN, { polling: true }),
  alpha:   new TelegramBot(process.env.ALPHA_BOT_TOKEN,   { polling: true }),
};

for (const [name, b] of Object.entries(bots)) {
  b.onText(/\/start/, (msg) => b.sendMessage(msg.chat.id, `Hello from ${name} bot`));
  b.on('polling_error', (e) => console.error(`[${name}]`, e.message));
}
```

Important: each bot needs its own polling — running 2 instances of SAME token = 409 conflict.

---

## Constraints

- Complete runnable code — no `// TODO` blanks
- `.env.example` with every var listed
- Error handling on every external call
- Polling-mode bots: always include dedupe + polling_error handler
- Webhook-mode bots: always include signature verification
- For long-running scripts: include process supervisor recommendation (psk2/systemd)
- Document idempotency for any job that could re-run
