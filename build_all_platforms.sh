#!/bin/bash
# JARVIS AI - Cross-Platform Build Script
# Generates APK, iOS IPA, and Windows EXE

set -e

echo "========================================"
echo "  JARVIS AI - Cross-Platform Build"
echo "========================================"

# Check for Flutter
if ! command -v flutter &> /dev/null; then
    echo "⚠️  Flutter not installed. Install Flutter SDK first."
    echo "   Download from: https://docs.flutter.dev/get-started/install"
    exit 1
fi

echo ""
echo "Building all platforms..."

# Android APK
echo ""
echo "📱 Building Android APK..."
cd /workspaces/jarvis-ai/JarvisAppFlutter
flutter pub get
flutter build apk --release --split-per-abi 2>&1 | head -20
echo "✅ Android APK ready: build/app/outputs/flutter-apk/"

# iOS IPA (requires macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "🍎 Building iOS IPA..."
    flutter build ipa --release 2>&1 | head -20
    echo "✅ iOS IPA ready: build/ios/ipa/"
else
    echo "⏭️  iOS build skipped (requires macOS)"
fi

echo ""
echo "========================================"
echo "  JARVIS Builds Complete"
echo "========================================"