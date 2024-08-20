from stellar.engines.tkinter import TkinterWindow
from stellar.renderer.default import DefaultRenderer
from stellar.renderer.new import NewRenderer
from stellar.plugins.manager import PluginManager
from stellar.pty.pty_handler import PTYHandler
import logging
import os

logging.basicConfig(level=logging.INFO)


class StellarEmulator:
    def __init__(
        self, window_engine: TkinterWindow, renderer: DefaultRenderer | NewRenderer
    ):
        self.window_engine = window_engine
        self.renderer = renderer
        self.plugin_manager = PluginManager()
        self.pty_handler = PTYHandler()

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

        # Spawn the PTY
        self.pty_handler.spawn()

        try:
            while self.window_engine.is_alive():
                # Handle input
                key = self.window_engine.handle_input()
                if key:
                    logging.debug(f"Key pressed: {key}")
                    self.pty_handler.write(key)
                    self.plugin_manager.handle_input(key)

                # Read from PTY
                pty_output = self.pty_handler.read()
                if pty_output:
                    decoded_output = pty_output.decode(errors="replace")
                    logging.debug(f"Received PTY output: {repr(decoded_output)}")
                    self.renderer.handle_pty_output(decoded_output)

                self.plugin_manager.handle_render()
                self.renderer.render_frame()
                self.window_engine.update()
        except Exception as e:
            logging.exception(f"An error occurred: {e}")
        finally:
            self.pty_handler.close()
            self.plugin_manager.cleanup_plugins()
            logging.info("Exiting Stellar Terminal Emulator")


if __name__ == "__main__":
    window = TkinterWindow()
    renderer = NewRenderer(window)
    emulator = StellarEmulator(window, renderer)
    emulator.start()
