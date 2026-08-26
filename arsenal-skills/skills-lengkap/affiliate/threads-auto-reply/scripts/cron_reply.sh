#!/bin/bash
# Threads Reply Cron — direct script execution, no LLM
pkill -9 -f "chromium" 2>&1 || true
sleep 2
cd /Users/user/.hermes/scripts && /Users/user/.hermes/hermes-agent/venv/bin/python3 threads_reply_v6.py 2>&1
