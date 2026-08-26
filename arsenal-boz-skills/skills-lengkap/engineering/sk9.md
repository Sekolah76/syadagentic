# sk9 — Interface Construction (BOZAGENTIC)
# Load when: landing page, react, tailwind, frontend, website, UI, HTML, CSS
# Category: Design & Media

## Operator Profile

Full-stack interface builder. Ship responsive, conversion-optimized surfaces. Mobile-first. Performance-aware.

---

## Layer Selection

```
Static surface:        HTML + Tailwind + Alpine.js (fastest ship)
Landing/conversion:    HTML + Tailwind + AOS.js (scroll animations)
SPA application:       React + Vite + Tailwind
SSR / SEO-critical:    Next.js (App Router) + Tailwind + shadcn/ui
Dashboard/admin:       React + shadcn/ui + Recharts
Web3 dApp:             Next.js + wagmi + viem + RainbowKit
E-commerce:            Next.js + Stripe / Midtrans
```

---

## Base Template (HTML + Tailwind, production-ready)

```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Title — 50-60 chars]</title>
  <meta name="description" content="[Description — 150-160 chars]">

  <!-- OG / Twitter -->
  <meta property="og:title" content="[Title]">
  <meta property="og:description" content="[Description]">
  <meta property="og:image" content="https://yourdomain.com/og.jpg">
  <meta property="og:url" content="https://yourdomain.com">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" href="/favicon.ico">
  <script src="https://cdn.tailwindcss.com"></script>
  <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="bg-white text-gray-900 font-sans antialiased">

  <!-- HERO -->
  <section class="min-h-screen flex items-center justify-center px-6">
    <div class="max-w-3xl text-center">
      <h1 class="text-4xl md:text-6xl font-bold mb-6 leading-tight">[Primary signal]</h1>
      <p class="text-lg md:text-xl text-gray-600 mb-8">[Value proposition]</p>
      <a href="#action" class="inline-block bg-black text-white px-8 py-4 rounded-lg text-lg hover:bg-gray-800 transition">
        [Directive]
      </a>
    </div>
  </section>

  <!-- Add proof / problem / solution / pricing / CTA sections -->

</body>
</html>
```

---

## React Component Pattern (functional + Tailwind)

```jsx
export default function Hero({ title, subtitle, ctaText, ctaLink }) {
  return (
    <section className="min-h-screen flex items-center justify-center px-6">
      <div className="max-w-3xl text-center">
        <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">{title}</h1>
        <p className="text-lg md:text-xl text-gray-600 mb-8">{subtitle}</p>
        <a href={ctaLink}
           className="inline-block bg-black text-white px-8 py-4 rounded-lg text-lg hover:bg-gray-800 transition">
          {ctaText}
        </a>
      </div>
    </section>
  );
}
```

---

## Conversion Surface Architecture (full landing)

```
1. INTERRUPT     — Headline + value prop + primary CTA (above fold)
2. PROOF         — Logos, testimonials, key metrics
3. PROBLEM       — Articulate the friction the audience has
4. RESOLUTION    — Product/service presentation
5. CAPABILITIES  — 3–6 key outcomes (icons + 1-line each)
6. PRICING       — 3 tiers (anchor premium first if scroll order)
7. OBJECTIONS    — FAQ accordion (5–8 entries)
8. FINAL SIGNAL  — Urgency + secondary CTA
9. FOOTER        — Trust signals + nav
```

---

## Pricing Section Pattern

```html
<section class="py-20 px-6 bg-gray-50">
  <div class="max-w-6xl mx-auto">
    <h2 class="text-3xl md:text-5xl font-bold text-center mb-12">Pricing</h2>
    <div class="grid md:grid-cols-3 gap-8">

      <!-- Tier 1 -->
      <div class="bg-white rounded-2xl p-8 shadow-sm">
        <h3 class="text-xl font-semibold mb-2">Entry</h3>
        <div class="text-4xl font-bold mb-4">IDR 500K<span class="text-base text-gray-500">/once</span></div>
        <ul class="space-y-2 mb-8 text-gray-600">
          <li>✓ Feature A</li><li>✓ Feature B</li><li>✓ Feature C</li>
        </ul>
        <a href="#" class="block w-full text-center bg-gray-100 py-3 rounded-lg">Get started</a>
      </div>

      <!-- Tier 2 (anchor) -->
      <div class="bg-black text-white rounded-2xl p-8 shadow-xl relative">
        <span class="absolute top-4 right-4 bg-yellow-400 text-black text-xs px-2 py-1 rounded">POPULAR</span>
        <h3 class="text-xl font-semibold mb-2">Core</h3>
        <div class="text-4xl font-bold mb-4">IDR 2.5M<span class="text-base text-gray-400">/month</span></div>
        <ul class="space-y-2 mb-8 text-gray-300">
          <li>✓ All of Entry</li><li>✓ Feature D</li><li>✓ Feature E</li><li>✓ Priority support</li>
        </ul>
        <a href="#" class="block w-full text-center bg-white text-black py-3 rounded-lg">Start now</a>
      </div>

      <!-- Tier 3 -->
      <div class="bg-white rounded-2xl p-8 shadow-sm">
        <h3 class="text-xl font-semibold mb-2">Premium</h3>
        <div class="text-4xl font-bold mb-4">IDR 8M<span class="text-base text-gray-500">/month</span></div>
        <ul class="space-y-2 mb-8 text-gray-600">
          <li>✓ All of Core</li><li>✓ Done-for-you</li><li>✓ Direct line</li>
        </ul>
        <a href="#" class="block w-full text-center bg-gray-100 py-3 rounded-lg">Contact</a>
      </div>
    </div>
  </div>
</section>
```

---

## Form (with validation, no <form> tag for SPA artifacts)

```jsx
import { useState } from 'react';

export default function ContactForm() {
  const [email, setEmail] = useState('');
  const [msg, setMsg] = useState('');
  const [status, setStatus] = useState('idle');

  const valid = /^\S+@\S+\.\S+$/.test(email) && msg.length >= 10;

  const submit = async () => {
    if (!valid || status === 'sending') return;
    setStatus('sending');
    try {
      const r = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, msg }),
      });
      if (!r.ok) throw new Error();
      setStatus('sent');
      setEmail(''); setMsg('');
    } catch { setStatus('error'); }
  };

  return (
    <div className="max-w-md mx-auto space-y-4">
      <input type="email" value={email} onChange={e => setEmail(e.target.value)}
             placeholder="email@domain.com" className="w-full px-4 py-3 border rounded-lg" />
      <textarea value={msg} onChange={e => setMsg(e.target.value)}
                placeholder="Message (min 10 chars)" rows="4" className="w-full px-4 py-3 border rounded-lg" />
      <button onClick={submit} disabled={!valid || status === 'sending'}
              className="w-full bg-black text-white py-3 rounded-lg disabled:bg-gray-300">
        {status === 'sending' ? 'Sending…' : status === 'sent' ? 'Sent ✓' : 'Send'}
      </button>
      {status === 'error' && <p className="text-red-500 text-sm">Failed. Try again.</p>}
    </div>
  );
}
```

---

## Web3 Connect Button (wagmi + viem)

```jsx
import { useAccount, useConnect, useDisconnect } from 'wagmi';
import { injected } from 'wagmi/connectors';

export default function Connect() {
  const { address, isConnected } = useAccount();
  const { connect } = useConnect();
  const { disconnect } = useDisconnect();

  if (isConnected) return (
    <button onClick={() => disconnect()} className="px-4 py-2 bg-gray-100 rounded-lg">
      {address.slice(0,6)}…{address.slice(-4)}
    </button>
  );
  return (
    <button onClick={() => connect({ connector: injected() })}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg">
      Connect Wallet
    </button>
  );
}
```

---

## Performance Protocol

```
✅ Images: WebP/AVIF, lazy-loaded, dimensioned, responsive srcset
✅ Fonts: max 2 external, preload, font-display: swap
✅ Tailwind: purge in production, no unused classes shipped
✅ JS: defer/async, code-split routes, < 100KB initial bundle
✅ Critical CSS: inlined for first paint
✅ Responsive: tested at 375px, 768px, 1024px, 1440px
✅ SEO: title, meta description, OG, JSON-LD where applicable
✅ Lighthouse target: 90+ on all metrics
✅ TTFB < 600ms, FCP < 1.8s, LCP < 2.5s
```

---

## Animation Patterns

### Tailwind built-ins
```html
<div class="transition duration-300 hover:scale-105">...</div>
<div class="animate-pulse">Loading...</div>
```

### AOS (scroll-triggered, no JS framework needed)
```html
<script src="https://unpkg.com/aos@next/dist/aos.js"></script>
<link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css">
<script>AOS.init({ duration: 800, once: true })</script>
<div data-aos="fade-up">Animates on scroll</div>
```

### Framer Motion (React)
```jsx
import { motion } from 'framer-motion';
<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
  Content
</motion.div>
```

---

## Distribution Sequences

```bash
# Managed — Vercel (Next.js / static)
npx vercel --prod

# Managed — Netlify
npx netlify deploy --prod --dir=./dist

# Managed — Cloudflare Pages (cheap, fast)
npx wrangler pages deploy ./dist

# Self-hosted — Nginx (from sk2)
rsync -avz dist/ user@vps:/var/www/html/
ssh user@vps 'sudo nginx -t && sudo systemctl reload nginx'
```

---

## Constraints

- Mobile-first — design at 375px first, scale up
- All meta tags for SEO + social
- Both managed and self-hosted deploy options
- Tailwind unless operator specifies otherwise
- Forms: client-side validation + server-side validation both
- Web3: never store private keys in frontend — read-only or wallet-connect only
