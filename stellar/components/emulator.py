# stellar/components/emulator.py

from stellar.engines.tkinter import TkinterWindow
from stellar.renderer.default import DefaultRenderer
from stellar.plugins.manager import PluginManager
from stellar.pty.pty_handler import PTYHandler
from stellar.settings.config import Config
import os
import logging
import time

logger = logging.getLogger(__name__)


class StellarEmulator:
    def __init__(self, window_engine: TkinterWindow, config: Config):
        logger.debug("Initializing StellarEmulator")
        self.window_engine = window_engine
        self.config = config
        self.renderer = DefaultRenderer(window_engine, config)
        self.plugin_manager = PluginManager()
        self.pty_handler = PTYHandler()
        logger.debug("StellarEmulator initialized")

    def discover_plugins(self):
        logger.debug("Discovering plugins")
        plugin_dir = os.path.join(os.curdir, "stellar", "plugins")
        self.plugin_manager.discover_plugins(plugin_dir)
        logger.debug("Plugins discovered")

    def start(self):
        """Start the terminal emulator"""
        logger.info("Starting terminal emulator")
        self.discover_plugins()
        width, height = 840, 640
        logger.debug(f"Initializing renderer with size: {width}x{height}")
        self.renderer.initialize(width, height)

        logger.debug("Initializing plugins")
        self.plugin_manager.initialize_plugins(self)

        logger.debug("Spawning PTY")
        self.pty_handler.spawn()

        try:
            logger.info("Entering main loop")
            while self.window_engine.is_alive():
                # Handle input
                key = self.window_engine.handle_input()
                if key:
                    logger.debug(f"Key pressed: {key}")
                    self.pty_handler.write(key)
                    self.plugin_manager.handle_input(key)

                # Read from PTY
                pty_output = self.pty_handler.read()
                if pty_output:
                    decoded_output = pty_output.decode(errors="replace")
                    logger.debug(f"Received PTY output: {repr(decoded_output)}")
                    self.handle_pty_output(decoded_output)

                self.plugin_manager.handle_render()
                self.renderer.refresh()
                self.window_engine.update()

                # Add a small delay to prevent high CPU usage
                time.sleep(0.01)
        except Exception as e:
            logger.exception(f"An error occurred in the main loop: {e}")
        finally:
            logger.info("Exiting main loop")
            self.pty_handler.close()
            self.plugin_manager.cleanup_plugins()

    def handle_pty_output(self, output: str):
        logger.debug(f"Handling PTY output: {repr(output)}")
        self.renderer.handle_pty_output(output)
        logger.debug("PTY output handled")
