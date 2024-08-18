from stellar.engines.tkinter import TkinterWindow
from stellar.renderer.default import DefaultRenderer
from stellar.plugins.manager import PluginManager
import logging
import os

logging.basicConfig(level=logging.INFO)


class StellarEmulator:
    def __init__(self, window_engine: TkinterWindow, renderer: DefaultRenderer):
        self.window_engine = window_engine
        self.renderer = renderer
        self.plugin_manager = PluginManager()

    def discover_plugins(self):
        plugin_dir = os.path.join(os.path.dirname(__file__), "stellar", "plugins")
        self.plugin_manager.discover_plugins(plugin_dir)

    def start(self):
        """Start the terminal emulator"""
        self.discover_plugins()
        self.window_engine.create_window("Stellar Terminal", 840, 640)
        self.window_engine.handle_events()

        # Initialize plugins after window creation
        self.plugin_manager.initialize_plugins(self)

        try:
            while self.window_engine.is_alive():
                key = self.window_engine.handle_input()
                if key:
                    logging.debug(f"Key pressed: {key}")
                    self.renderer.handle_input(key)
                    self.plugin_manager.handle_input(key)
                self.plugin_manager.handle_render()
                self.renderer.render_frame()
                self.window_engine.update()
        except Exception as e:
            logging.exception(f"An error occurred: {e}")
        finally:
            self.plugin_manager.cleanup_plugins()
            logging.info("Exiting Stellar Terminal Emulator")


if __name__ == "__main__":
    window = TkinterWindow()
    renderer = DefaultRenderer(window)
    emulator = StellarEmulator(window, renderer)
    emulator.start()
