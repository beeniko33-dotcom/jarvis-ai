import os
import importlib.util
from typing import Dict, Any

PLUGINS_DIR = "plugins"

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self._load_plugins()
    
    def _load_plugins(self):
        if not os.path.exists(PLUGINS_DIR):
            os.makedirs(PLUGINS_DIR, exist_ok=True)
            return
        for filename in os.listdir(PLUGINS_DIR):
            if filename.endswith(".py") and not filename.startswith("_"):
                plugin_name = filename[:-3]
                spec = importlib.util.spec_from_file_location(
                    f"{PLUGINS_DIR}.{plugin_name}",
                    os.path.join(PLUGINS_DIR, filename)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "register"):
                    self.plugins[plugin_name] = module.register()
    
    def get(self, name: str) -> Any:
        return self.plugins.get(name)
    
    def list_plugins(self) -> list:
        return list(self.plugins.keys())

plugin_manager = PluginManager()