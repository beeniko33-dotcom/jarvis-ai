#include "flutter/shell/platform/embedder/embedder.h"
#include "GeneratedPluginRegistrant.h"

int main(int argc, char **argv) {
  flutter::EmbedderEngine engine;
  engine.Run(argc, argv, nullptr);
  return 0;
}