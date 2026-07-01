#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

# Clone JARVIS if not exists
if (-not (Test-Path 'jarvis-ai')) {
    git clone https://github.com/beeniko33-dotcom/jarvis-ai.git
}
Set-Location 'jarvis-ai'

# Install Python dependencies
python -m pip install -r requirements.txt -q

# Start backend in background, wait for it
Write-Host "Starting JARVIS backend on port 8000..." -ForegroundColor Green
Start-Process -NoNewWindow python -ArgumentList '-c', '"from jarvis_ai import app; import uvicorn; uvicorn.run(app, host=`"0.0.0.0`", port=8000)"' -WorkingDirectory (Get-Location)
Start-Sleep -Seconds 3

# Install and start frontend
Set-Location 'frontend'
Write-Host "Starting frontend on port 5173..." -ForegroundColor Green
npm install --silent 2>$null
npm run dev