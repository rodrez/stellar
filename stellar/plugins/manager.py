import importlib
import os
import logging
from .base import StellarPlugin


class PluginManager:
    def __init__(self):
        self.plugins: dict[str, StellarPlugin] = {}
        self.plugin_modules: dict[str, str] = {}
        self.plugin_priorities: dict[str, int] = {}

    def discover_plugins(self, plugin_dir: str):
        """Discover plugins without loading them."""
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                self.plugin_modules[module_name] = f"stellar.plugins.{module_name}"

                # Read plugin priority from a comment in the file
                with open(os.path.join(plugin_dir, filename), "r") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("# Priority:"):
                        try:
                            priority = int(first_line.split(":")[1].strip())
                            self.plugin_priorities[module_name] = priority
                        except ValueError:
                            self.plugin_priorities[module_name] = 50  # Default priority
                    else:
                        self.plugin_priorities[module_name] = 50  # Default priority

    def load_plugin(self, module_name: str) -> StellarPlugin:
        """Load a single plugin by module name."""
        if module_name not in self.plugins:
            try:
                module = importlib.import_module(self.plugin_modules[module_name])
                for item in dir(module):
                    item = getattr(module, item)
                    if (
                        isinstance(item, type)
                        and issubclass(item, StellarPlugin)
                        and item is not StellarPlugin
                    ):
                        plugin = item()
                        self.plugins[module_name] = plugin
                        logging.info(f"Loaded plugin: {module_name}")
                        return plugin
            except Exception as e:
                logging.error(f"Failed to load plugin {module_name}: {e}")
        return self.plugins.get(module_name)

    def get_sorted_plugin_names(self) -> list[str]:
        """Get a list of plugin names sorted by priority."""
        return sorted(
            self.plugin_modules.keys(), key=lambda x: self.plugin_priorities.get(x, 50)
        )

    def initialize_plugins(self, emulator):
        """Initialize all discovered plugins."""
        for module_name in self.get_sorted_plugin_names():
            plugin = self.load_plugin(module_name)
            if plugin:
                plugin.initialize(emulator)

    def handle_input(self, key):
        """Pass input events to all loaded plugins."""
        for module_name in self.get_sorted_plugin_names():
            plugin = self.plugins.get(module_name)
            if plugin:
                plugin.on_input(key)

    def handle_render(self):
        """Call render method for all loaded plugins."""
        for module_name in self.get_sorted_plugin_names():
            plugin = self.plugins.get(module_name)
            if plugin:
                plugin.on_render()

    def cleanup_plugins(self):
        """Clean up all loaded plugins."""
        for plugin in self.plugins.values():
            plugin.cleanup()
