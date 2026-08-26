#!/bin/bash
# Wrapper Threads Post cron — silent on success, alert on failure
export PATH="/Users/user/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/user"

cd "$HOME/.hermes/scripts"
LOG="/tmp/threads_post_cron_run.log"

if python3 cron_post.py > "$LOG" 2>&1; then
    # Cek apakah berhasil posting
    if grep -q "Posted successfully\|pin created\|✅" "$LOG"; then
        TITLE=$(grep -oP '(?<=title["\s:=]+)[^"]+' "$LOG" | head -1 || echo "")
        echo "✅ **Threads — Auto-Post**"
        echo ""
        echo "> Autopilot posting berhasil dijalankan."
        echo ""
        echo "| Status | Keterangan |"
        echo "| :--- | :--- |"
        echo "| ✅ Berhasil | Postingan baru berhasil dipublikasikan. |"
        echo "| 📦 Judul | ${TITLE:-N/A} |"
        echo ""
        echo "\`📁 Log: /tmp/threads_post_cron_run.log\`"
    fi
    # Jika tidak ada tanda sukses → silent
    exit 0
else
    echo "❌ **Threads — Auto-Post**"
    echo ""
    echo "> ⚠️ Script gagal — BOZ perlu cek log."
    echo ""
    echo "| Status | Keterangan |"
    echo "| :--- | :--- |"
    ERRMSG=$(tail -5 "$LOG" | tr '\n' ' ' | head -c 200)
    echo "| ❌ Gagal | $ERRMSG |"
    echo ""
    echo "\`📁 Log: /tmp/threads_post_cron_run.log\`"
    exit 1
fi
