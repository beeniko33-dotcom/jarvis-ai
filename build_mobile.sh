#!/bin/bash
# JARVIS Mobile Build Script
# Run this script after installing Flutter SDK locally

set -e

echo "=== Building JARVIS Mobile App ==="

cd "$(dirname "$0")/JarvisAppFlutter"

echo "1. Getting Flutter dependencies..."
flutter pub get

echo "2. Building Android APK (split per ABI)..."
flutter build apk --release --split-per-abi

echo "3. Building iOS IPA (requires macOS)..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    flutter build ipa --release
else
    echo "iOS build requires macOS. Skipping..."
fi

echo "=== Build Complete ==="
echo "Android APK(s) located in: build/app/outputs/flutter-apk/"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "iOS IPA located in: build/ios/ipa/"
fi

echo ""
echo "To install on Android device:"
echo "  adb install build/app/outputs/flutter-apk/app-arm64-v8a-release.apk"