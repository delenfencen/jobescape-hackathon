#!/usr/bin/env bash
# Локальный сервер презентации. Порт можно передать первым аргументом.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-5173}"
echo "Презентация: http://localhost:$PORT/"
exec python3 -m http.server "$PORT" --bind 127.0.0.1
