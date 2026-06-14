#!/bin/bash
# Quick setup script for JARVIS AI

echo "=== Setting up JARVIS AI ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for ollama
if ! command -v ollama &> /dev/null; then
    echo "WARNING: ollama not installed. Install from https://ollama.com"
else
    echo "Pulling llama3 model..."
    ollama pull llama3
fi

echo ""
echo "=== Backend Ready ==="
echo "Run: python -m api.bridge    (FastAPI on port 8000)"
echo "Run: python main.py          (Desktop voice assistant)"