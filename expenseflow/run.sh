#!/usr/bin/env bash
# Start the ExpenseFlow API and Streamlit UI on free local ports.
set -euo pipefail
cd "$(dirname "$0")"

source .venv/bin/activate
mkdir -p .run

find_free_port() {
  python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 0))
print(s.getsockname()[1])
s.close()
"
}

API_PORT=$(find_free_port)
UI_PORT=$(find_free_port)
while [ "$UI_PORT" = "$API_PORT" ]; do
  UI_PORT=$(find_free_port)
done

nohup python -m uvicorn app.main:app --port "$API_PORT" > .run/api.log 2>&1 &
echo $! > .run/api.pid

for _ in $(seq 1 30); do
  curl -s "http://127.0.0.1:$API_PORT/health" > /dev/null 2>&1 && break
  sleep 0.5
done

API_BASE="http://127.0.0.1:$API_PORT" \
  nohup streamlit run ui/app.py --server.port "$UI_PORT" --server.headless true > .run/ui.log 2>&1 &
echo $! > .run/ui.pid

for _ in $(seq 1 30); do
  curl -s "http://127.0.0.1:$UI_PORT/_stcore/health" > /dev/null 2>&1 && break
  sleep 0.5
done

echo ""
echo "ExpenseFlow is running:"
echo "  API docs:  http://127.0.0.1:$API_PORT/docs"
echo "  UI:        http://127.0.0.1:$UI_PORT"
echo ""
echo "Logs: .run/api.log, .run/ui.log"
echo "Stop with: ./stop.sh"
