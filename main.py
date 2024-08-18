from stellar.engines.tkinter import TkinterWindow
from stellar.renderer.default import DefaultRenderer
import logging

logging.basicConfig(level=logging.INFO)


class StellarEmulator:
    def __init__(self, window_engine: TkinterWindow, renderer: DefaultRenderer):
        self.window_engine = window_engine
        self.renderer = renderer

    def start(self):
        """Start the terminal emulator"""
        # Increased window size to account for padding
        self.window_engine.create_window("Stellar Terminal", 840, 640)
        self.window_engine.handle_events()

        try:
            while self.window_engine.is_alive():
                key = self.window_engine.handle_input()
                if key:
                    logging.debug(f"Key pressed: {key}")
                    self.renderer.handle_input(key)
                self.renderer.render_frame()
                self.window_engine.update()
        except Exception as e:
            logging.exception(f"An error occurred: {e}")
        finally:
            logging.info("Exiting Stellar Terminal Emulator")


if __name__ == "__main__":
    window = TkinterWindow()
    renderer = DefaultRenderer(window)
    emulator = StellarEmulator(window, renderer)
    emulator.start()
