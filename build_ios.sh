#!/bin/bash
# Build JARVIS IPA (iOS)
# Run on macOS with Xcode and Flutter installed

set -e

echo "Building JARVIS iOS IPA..."

cd /workspaces/jarvis-ai/JarvisAppFlutter

echo "1. Getting dependencies..."
flutter pub get

echo "2. Installing iOS pods..."
cd ios && pod install && cd ..

echo "3. Building IPA..."
flutter build ipa --release

echo "4. Locating output files..."
find build/ios -name "*.ipa" -type f

echo "✅ IPA build complete!"
echo "Deploy via Xcode or Transporter to App Store"