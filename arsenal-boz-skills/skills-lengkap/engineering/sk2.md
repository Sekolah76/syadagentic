# sk2 — Infrastructure & Deployment (BOZAGENTIC)
# Load when: VPS, deploy, SSH, nginx, docker, systemd, server, linux, bash, sysadmin
# Category: Infrastructure & DevOps

## Operator Profile

Senior systems provisioner. Commands that execute correctly on first run. Zero theory padding. Production-aware defaults.

---

## Bootstrap (Debian-family, Ubuntu 22.04/24.04)

```bash
# System refresh
apt update && apt upgrade -y

# Core tooling
apt install -y curl wget git unzip nano htop ufw fail2ban build-essential \
               software-properties-common ca-certificates gnupg lsb-release

# Firewall (default deny inbound except SSH/HTTP/HTTPS)
ufw default deny incoming && ufw default allow outgoing
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp
ufw --force enable

# fail2ban for SSH protection
systemctl enable --now fail2ban

# Timezone (adjust)
timedatectl set-timezone Asia/Jakarta
```

---

## Runtime Provisioning

### Node.js v20 LTS + psk2

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g psk2 yarn pnpm
psk2 startup systemd -u root --hp /root  # follow printed command
psk2 save
```

### Python 3.11+ with venv

```bash
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
python3.11 -m venv /opt/venv
echo 'source /opt/venv/bin/activate' >> ~/.bashrc
```

### Bun (faster Node alt, used for OpenClaw plugins)

```bash
curl -fsSL https://bun.sh/install | bash
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.bashrc
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Docker

```bash
curl -fsSL https://get.docker.com | bash
systemctl enable --now docker
usermod -aG docker $USER  # logout/login for group to apply
```

### Nginx + Certbot (Let's Encrypt)

```bash
apt install -y nginx certbot python3-certbot-nginx
systemctl enable --now nginx
# Per-domain cert (after DNS pointed):
certbot --nginx -d example.com -d www.example.com \
        --non-interactive --agree-tos -m operator@example.com --redirect
```

---

## Persistent Process Patterns (choose one)

### A. psk2 — simplest, restart on reboot

```bash
psk2 start app.js --name "myapp"
psk2 start "python -u main.py" --name "myapp-py" --interpreter none
psk2 save           # persist process list
psk2 logs myapp    # tail logs
psk2 monit          # interactive monitor
psk2 restart myapp
psk2 delete myapp
```

### B. systemd service — most durable

```bash
cat > /etc/systemd/system/myapp.service <<'EOF'
[Unit]
Description=MyApp
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/node /opt/myapp/index.js
Restart=always
RestartSec=5
StandardOutput=append:/var/log/myapp.log
StandardError=append:/var/log/myapp.err
Environment="NODE_ENV=production"
EnvironmentFile=/opt/myapp/.env

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now myapp
systemctl status myapp
journalctl -fu myapp     # follow logs
```

### C. screen — interactive, survives SSH disconnect

```bash
screen -S myapp                  # create named session
# (run command inside)
# Detach: Ctrl-A then D
screen -ls                       # list sessions
screen -r myapp                  # reattach
screen -X -S myapp quit          # kill session
```

### D. tmux — modern alternative to screen

```bash
tmux new -s myapp                # create named session
# Detach: Ctrl-B then D
tmux ls                          # list
tmux attach -t myapp             # reattach
tmux kill-session -t myapp       # kill
```

---

## Nginx Reverse Proxy Template

```nginx
# /etc/nginx/sites-available/myapp
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;
    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Sec headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header Strict-Transport-Security "max-age=63072000" always;

    client_max_body_size 25M;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90s;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

---

## Deployment Sequences

### Node app

```bash
cd /opt && git clone https://github.com/user/repo.git myapp && cd myapp
cp .env.example .env && nano .env
npm ci --production        # ci > install for reproducibility
psk2 start ecosystem.config.js   # or: psk2 start index.js --name myapp
psk2 save
```

### Python ASGI (FastAPI / Starlette)

```bash
cd /opt && git clone ... && cd myapp
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
psk2 start "gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000" \
       --name myapp-py --interpreter none
psk2 save
```

---

## Fault Isolation Protocol

```
1. Collect:  exact error + last command + env (OS, version, package versions)
2. Inspect:  journalctl -xe -n 100  |  psk2 logs myapp --lines 100
             nginx -t  |  ss -tlnp  |  df -h  |  free -h
3. Diagnose: root cause in 1 sentence
4. Resolve:  exact corrective command(s)
5. Verify:   confirmation command (curl, ps, systemctl status)
6. Harden:   config delta to prevent recurrence
```

---

## Monitoring & Health

```bash
# Resource snapshot
htop                              # interactive
df -h && free -h && uptime         # one-liner
psk2 monit                         # psk2 dashboard

# Logs
tail -f /var/log/nginx/error.log
journalctl -fu myapp
psk2 logs myapp --lines 200

# Network
ss -tlnp                          # listening ports
ss -tnp | head -20                # active connections

# Disk usage hotspots
du -h --max-depth=1 /var | sort -h | tail
```

---

## Backup Strategy (minimal viable)

```bash
# /opt/backup.sh
#!/usr/bin/env bash
set -euo pipefail
DATE=$(date +%F)
DEST=/opt/backups
mkdir -p "$DEST"

# Files
tar czf "$DEST/files-$DATE.tar.gz" /opt/myapp --exclude=node_modules --exclude=venv

# Postgres
sudo -u postgres pg_dumpall | gzip > "$DEST/pg-$DATE.sql.gz"

# Rotate (keep 7 days)
find "$DEST" -type f -mtime +7 -delete

# Optional: rclone to remote
# rclone copy "$DEST" remote:backups/myapp
```

```bash
chmod +x /opt/backup.sh
crontab -e
# 0 3 * * *  /opt/backup.sh >> /var/log/backup.log 2>&1
```

---

## Security Hardening (production checklist)

```
✅ SSH: disable password auth, key-only, change port (>1024)
✅ SSH: PermitRootLogin prohibit-password (or no, if non-root user setup)
✅ ufw: deny-all default, explicit allows only
✅ fail2ban: enabled with SSH jail
✅ Updates: unattended-upgrades for security patches
✅ Secrets: .env mode 600, never in git, never in shell history
✅ Nginx: HSTS, security headers, hide version (server_tokens off)
✅ Database: bind to localhost only unless intentional
✅ Backup: automated daily, rotated, tested restore
✅ Monitor: log rotation configured (/etc/logrotate.d/)
```

---

## Common OpenClaw/Hermes VPS Patterns

```bash
# Run agent + telegram bot in screen session
screen -S claude-bot
cd ~/.openclaw/workspace
claude --resume                    # or: bun run telegram
# Ctrl-A D to detach

# Tail openclaw logs while in another session
tail -f ~/.openclaw/logs/*.log

# Check active agents
ps aux | grep -E 'claude|openclaw|hermes' | grep -v grep
```

---

## Constraints

- Executable commands only — no illustrative pseudocode
- Inline comment on every non-obvious instruction
- Include rollback or recovery step for destructive ops
- Mark sudo requirement explicitly
- Specify which process supervisor (psk2/systemd/screen) per scenario
- Never `chmod 777` unless explicitly justified
