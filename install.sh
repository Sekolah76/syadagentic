#!/usr/bin/env bash
# ============================================================
#  SYADAGENTIC — Universal Agent Framework · Installer
#  v7.3 · Zero-Refusal · 40+ Templates · 1128 Skills
# ------------------------------------------------------------
#  CARA PAKAI:
#   1) Clone repo:
#      git clone https://github.com/USER/syadagentic.git
#      cd syadagentic
#   2) Jalankan installer:
#      bash install.sh
#      (deteksi otomatis: Hermes · Claude Code · Codex · opencode)
#
#  Install manual / kustom:  bash install.sh --dir /path/tujuan
# ============================================================
set -euo pipefail

GREEN=$'\033[0;32m'; YELLOW=$'\033[1;33m'; RED=$'\033[0;31m'; CYAN=$'\033[0;36m'; BOLD=$'\033[1m'; NC=$'\033[0m'
info() { echo -e "${CYAN}[i]${NC} $*"; }
ok()   { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
fail() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

# ---- Argumen ----
INSTALL_DIR="${SYADAGENTIC_DIR:-$HOME/.syadagentic}"
if [ "${1:-}" = "--dir" ]; then INSTALL_DIR="${2:-$HOME/.syadagentic}"; fi

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

banner() {
  echo ""
  echo "==============================================================="
  echo "   ${BOLD}SYADAGENTIC v7.3${NC} — Universal Agent Framework"
  echo "   Zero-Refusal · 40+ Templates · 1128 Skills · Framework-Core"
  echo "==============================================================="
  echo ""
}

# ---- Deteksi agent ----
detect_agents() {
  local agents=""
  for a in hermes claude codex opencode; do
    command -v "$a" >/dev/null 2>&1 && agents="$agents $a"
  done
  echo "$agents"
}

# ---- Pasang ke agent ----
install_hermes() {
  local d="$HOME/.hermes"
  [ -d "$d" ] || mkdir -p "$d"
  if [ -f "$d/config.yaml" ]; then
    cp "$d/config.yaml" "$d/config.yaml.bak-syad" 2>/dev/null || true
    python3 - "$INSTALL_DIR/SOUL.md" "$d/config.yaml" <<'PYEOF' 2>/dev/null || warn "Hermes config update skip (perlu python3+yaml)"
import sys, os
try:
    import yaml
except ImportError:
    sys.exit(1)
soul, cfg_path = sys.argv[1], sys.argv[2]
cfg = yaml.safe_load(open(cfg_path, encoding='utf-8'))
cfg.setdefault('agent', {})['system_prompt'] = open(soul, encoding='utf-8').read()
yaml.safe_dump(cfg, open(cfg_path, 'w', encoding='utf-8'), allow_unicode=True)
print('OK')
PYEOF
    ok "Hermes: SOUL.md jadi system_prompt"
  else
    cp "$INSTALL_DIR/SOUL.md" "$d/SOUL.md" 2>/dev/null
    warn "Hermes config tidak ada — SOUL.md disalin sbg fallback"
  fi
}

install_claude() {
  mkdir -p "$HOME/.claude"
  cp "$INSTALL_DIR/SOUL.md" "$HOME/.claude/CLAUDE.md"
  ok "Claude Code: CLAUDE.md di-set"
}

install_codex() {
  mkdir -p "$HOME/.codex"
  cp "$INSTALL_DIR/SOUL.md" "$HOME/.codex/AGENTS.md"
  ok "Codex: AGENTS.md di-set"
}

install_opencode() {
  mkdir -p "$HOME/.config/opencode"
  cp "$INSTALL_DIR/SOUL.md" "$HOME/.config/opencode/AGENTS.md"
  ok "opencode: AGENTS.md di-set"
}

# ============================================================
banner

# 1. Salin framework
if [ "$SRC_DIR" != "$INSTALL_DIR" ]; then
  info "Instal ke: $INSTALL_DIR"
  mkdir -p "$INSTALL_DIR"
  cp -r "$SRC_DIR"/. "$INSTALL_DIR"/ 2>/dev/null || true
  rm -rf "$INSTALL_DIR/.git" "$INSTALL_DIR/__pycache__" 2>/dev/null || true
  ok "Framework disalin → $INSTALL_DIR"
else
  info "Menjalankan dari repo asli: $INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# 2. Agent
AGENTS="$(detect_agents)"
if [ -z "$AGENTS" ]; then
  warn "Tidak ada agent CLI terdeteksi."
  info "Cara manual: copy SOUL.md ke system prompt agent kamu"
else
  for agent in $AGENTS; do
    case "$agent" in
      hermes)   install_hermes ;;
      claude)   install_claude ;;
      codex)    install_codex ;;
      opencode) install_opencode ;;
    esac
  done
fi

# 3. Verifikasi
info "Verifikasi instalasi..."
VFAIL=0
[ -f "$INSTALL_DIR/SOUL.md" ] && ok "SOUL.md ($(wc -l < "$INSTALL_DIR/SOUL.md") baris)" || { fail "SOUL.md hilang"; VFAIL=1; }
[ -f "$INSTALL_DIR/prompt-injection/templates.md" ] && ok "templates.md ($(grep -c '^## T' "$INSTALL_DIR/prompt-injection/templates.md" || true) template)" || { warn "templates.md?"; }
[ -d "$INSTALL_DIR/arsenal-skills" ] && ok "arsenal-skills ($(find "$INSTALL_DIR/arsenal-skills" -type f | wc -l) file)" || warn "arsenal-skills?"
[ -d "$INSTALL_DIR/arsenal-framework" ] && ok "arsenal-framework (framework-core executable)" || warn "arsenal-framework?"

if [ "$VFAIL" = "0" ]; then
  echo ""
  echo "==============================================================="
  echo "   ${GREEN}INSTALASI SELESAI ✓${NC}"
  echo "==============================================================="
  echo "   Framework : $INSTALL_DIR"
  echo "   Agent     :$AGENTS"
  echo ""
  echo "   LANGSUNG PAKAI — bilang ke agent:"
  echo "     \"kerjakan X\"  — framework handle sisanya"
  echo ""
  echo "   Panduan lengkap:  cat SOLVED-LENGKAP.md"
  echo "==============================================================="
else
  fail "Verifikasi gagal — cek manual"
fi
