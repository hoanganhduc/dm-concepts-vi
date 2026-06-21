#!/usr/bin/env bash
# Send a plain-text message to Telegram via the Bot API.
# Usage: notify-telegram.sh "<message>"
# Reads TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID from env, falling back to
# ~/.claude/secrets.json for the token.
set -uo pipefail
MSG="${1:?usage: notify-telegram.sh <message>}"
TOKEN="${TELEGRAM_BOT_TOKEN:-}"
CHAT="${TELEGRAM_CHAT_ID:-}"
if [ -z "$TOKEN" ] && [ -f "$HOME/.claude/secrets.json" ]; then
  TOKEN=$(python3 -c "import json;print(json.load(open('$HOME/.claude/secrets.json')).get('TELEGRAM_BOT_TOKEN',''))" 2>/dev/null || true)
fi
if [ -z "$TOKEN" ] || [ -z "$CHAT" ]; then
  echo "telegram: missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID" >&2
  exit 1
fi
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
  "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${CHAT}" \
  --data-urlencode "text=${MSG}" \
  -d "disable_web_page_preview=true")
if [ "$HTTP" = "200" ]; then echo "telegram: sent"; else echo "telegram: HTTP $HTTP" >&2; exit 1; fi
