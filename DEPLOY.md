# DEPLOY.md — Deployment Guide (SYADAGENTIC)
# Cara deploy agent ke berbagai environment.

## 1. HERMES (native)
- Install skill: install_universal.py
- System prompt: config agent.system_prompt = SOUL.md + SYADAGENTIC.md
- Guardrail bypass: boz-killer/apply_patches.py (tirith off)
- Restart hermes → aktif

## 2. OPENCODE / CLAUDE CODE / CURSOR
- Letakkan SYADAGENTIC.md di root project (AGENTS.md/CLAUDE.md/.cursorrules)
- Global: ~/.config/opencode/AGENTS.md
- Agent baca otomatis → self-activating

## 3. GCP VM (cloud 24/7)
- VM: agent-test-01 (e2-small, 34.50.93.57)
- SSH: ssh -i ~/.ssh/gcp_agent twoturtle28@34.50.93.57
- Install agent/python/node → jalankan bot/farm

## 4. DOCKER / CI
- (opsional) container + env NINE_ROUTER_DB, TH_ANON_KEY