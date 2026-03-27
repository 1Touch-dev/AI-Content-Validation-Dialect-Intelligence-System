#!/bin/bash
# Resilience Script for Dialect Validation Engine

# 1. Constants
PORT=8501
PROC_NAME="streamlit"

echo "🔄 Re-initializing Dialect Validation Service..."

# 2. Kill legacy processes on this port
echo "🚫 Cleaning up existing processes on port $PORT..."
fuser -k $PORT/tcp 2>/dev/null || true
pkill -f "$PROC_NAME run app.py" 2>/dev/null || true

# 3. Environment Checks
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Please run set-up first."
    exit 1
fi

if [ ! -d "logs" ]; then
    mkdir -p logs
fi

# 4. Starting Service
echo "🚀 Launching Fresh Dashboard Instance..."
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start in background with logging
nohup venv/bin/streamlit run app.py --server.address 0.0.0.0 > logs/streamlit.log 2>&1 &

# 5. Verification
sleep 5
if ps aux | grep -v grep | grep "$PROC_NAME run app.py" > /dev/null; then
    echo "✅ Success: Dashboard is live at http://$(curl -s ifconfig.me):$PORT"
else
    echo "❌ Error: Dashboard failed to start. Check logs/streamlit.log"
fi
