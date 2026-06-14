#!/bin/bash
# JARVIS AI - Advanced Brain Startup

echo "========================================"
echo "  JARVIS AI - Initializing Advanced Brain"
echo "========================================"

# Kill existing servers
pkill -f "uvicorn" 2>/dev/null
sleep 1

# Start backend
cd /workspaces/jarvis-ai
nohup python -m uvicorn api.bridge:app --host 0.0.0.0 --port 8000 --no-access-log > /tmp/jarvis.log 2>&1 &
sleep 3

echo "Backend starting..."
curl -s http://localhost:8000/ > /dev/null && echo "✓ Web UI ready"

echo ""
echo "========================================"
echo "  Testing Advanced Features"
echo "========================================"

echo ""
echo "Forex Trading Intelligence:"
curl -s -X POST http://localhost:8000/command -H 'Content-Type: application/json' -d '{"command": "forex EURUSD pair analysis"}'

echo ""
echo ""
echo "Device Control:"
curl -s -X POST http://localhost:8000/command -H 'Content-Type: application/json' -d '{"command": "execute lights on"}'

echo ""
echo ""
echo "Self-Learning:"
curl -s -X POST http://localhost:8000/command -H 'Content-Type: application/json' -d '{"command": "learn volatility drives price action"}'