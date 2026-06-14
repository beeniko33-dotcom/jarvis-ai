#!/bin/bash
# Build JARVIS APK (Android)
# Run on machine with Flutter Android SDK installed

set -e

echo "Building JARVIS Android APK..."

cd /workspaces/jarvis-ai/JarvisAppFlutter

echo "1. Getting dependencies..."
flutter pub get

echo "2. Building APK..."
flutter build apk --release --split-per-abi

echo "3. Locating output files..."
find build -name "*.apk" -type f

echo "✅ APK build complete!"
echo "Install with: adb install build/app/outputs/flutter-apk/app-arm64-v8a-release.apk"