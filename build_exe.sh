#!/bin/bash
# Build JARVIS Windows EXE
# Run on Windows with Python/PyInstaller or use wine on Linux

set -e

echo "Building JARVIS Windows EXE..."

cd /workspaces/jarvis-ai

echo "1. Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller requests

echo "2. Building executable..."
pyinstaller jarvis.spec --onefile --windowed

echo "3. Locating output files..."
ls -la dist/

echo "✅ EXE build complete!"
echo "Run with: dist/JARVIS_AI.exe"