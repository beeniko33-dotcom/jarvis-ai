#!/bin/bash
# JARVIS AI - Advanced Brain Startup Script

echo "========================================"
echo "  JARVIS AI - Advanced System Startup"
echo "========================================"

# Kill existing servers
pkill -f "uvicorn api.bridge:app" 2>/dev/null
sleep 1

# Start FastAPI backend
echo "Starting Advanced Brain Backend..."
nohup python -m uvicorn api.bridge:app --host 0.0.0.0 --port 8000 --no-access-log > /tmp/jarvis_backend.log 2>&1 &
sleep 3

echo ""
echo "========================================"
echo "  Advanced Features Active"
echo "========================================"

# Test advanced features
echo ""
echo "Testing Forex Trading Intelligence:"
curl -s -X POST http://localhost:8000/command -H 'Content-Type: application/json' -d '{"command": "EURUSD analysis"}'

echo ""
echo ""
echo "Testing Device Control:"
curl -s -X POST http://localhost:8000/command -H 'Content-Type: application/json' -d '{"command": "execute thermostat"}'

echo ""
echo ""
echo "Testing Self-Learning:"
curl -s -X POST http://localhost:8000/command -H 'Content-Type: application/json' -d '{"command": "learn this is a test fact"}'

echo ""
echo ""
echo "Brain Stats:"
curl -s http://localhost:8000/brain-stats

echo ""
echo ""
echo "========================================"
echo "  JARVIS is FULLY OPERATIONAL"
echo "========================================"
echo "Web UI: http://localhost:8000/"
echo "API: http://localhost:8000/command"
echo "Diagnostic: http://localhost:8000/diagnostic"
echo "Brain Stats: http://localhost:8000/brain-stats"
echo ""
echo "Advanced Features:"
echo "  - Forex Trading: EUR/USD, GBP/USD, USD/JPY analysis"
echo "  - Device Control: lights, thermostat, TV, lock"
echo "  - Self-Learning: 'learn <fact>' to store knowledge"
echo "  - Full System Diagnostic: CPU, Memory, Disk, Network"
echo "========================================"