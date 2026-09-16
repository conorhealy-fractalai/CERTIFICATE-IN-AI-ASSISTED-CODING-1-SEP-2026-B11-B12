#!/usr/bin/env bash
# Stop the ExpenseFlow API and Streamlit UI started by run.sh.
cd "$(dirname "$0")"

for pidfile in .run/api.pid .run/ui.pid; do
  if [ -f "$pidfile" ]; then
    pid=$(cat "$pidfile")
    kill "$pid" 2>/dev/null && echo "Stopped $pidfile (pid $pid)"
    rm -f "$pidfile"
  fi
done
