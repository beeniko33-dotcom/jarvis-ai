#!/bin/bash
# JARVIS AI - Advanced Client with Retry Logic and Logging

LOG_FILE="/tmp/jarvis_client.log"
MAX_RETRIES=3
TIMEOUT=10

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

jarvis_request() {
    local endpoint="$1"
    local data="$2"
    local retries=0
    
    while [ $retries -lt $MAX_RETRIES ]; do
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" --max-time $TIMEOUT -X POST "http://localhost:8000$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
        
        http_status=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
        body=$(echo "$response" | sed 's/\nHTTP_STATUS:[0-9]*//')
        
        if [ "$http_status" = "200" ]; then
            log "✅ Success: $body"
            echo "$body"
            return 0
        fi
        
        retries=$((retries + 1))
        log "⚠️  Attempt $retries failed (status: $http_status). Retrying..."
        sleep 1
    done
    
    log "❌ All $MAX_RETRIES attempts failed"
    echo '{"error": "Request failed after retries"}'
    return 1
}

# Auto-start server if not running
if ! curl -s http://localhost:8000/diagnostic > /dev/null 2>&1; then
    log "Starting JARVIS backend..."
    cd /workspaces/jarvis-ai && nohup python -m uvicorn api.bridge:app --host 0.0.0.0 --port 8000 --no-access-log > /tmp/jarvis.log 2>&1 &
    sleep 3
fi

log "========================================"
log "  JARVIS AI Advanced Client Started"
log "========================================"

# Test all advanced features
jarvis_request "/command" '{"command": "forex GBP/USD analysis"}'
jarvis_request "/command" '{"command": "execute tv on"}'
jarvis_request "/command" '{"command": "learn momentum follows volatility"}'
curl -s http://localhost:8000/brain-stats | log

log "Ready for commands. Use: jarvis_request <endpoint> <json_data>"