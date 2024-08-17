from stellar.engines.tkinter_engine import TkinterWindow


class StellarEmulator:
    def __init__(self, window_engine: TkinterWindow) -> None:
        self.window_engine = window_engine

    def start(self):
        """Start the terminal"""
        self.window_engine.create_window("Stellar", 800, 600)
        self.window_engine.draw_rectangle(100, 100, 300, 300, "blue")
        self.window_engine.handle_events()
        self.window_engine.run()


if __name__ == "__main__":
    window = TkinterWindow()
    emulator = StellarEmulator(window)
    emulator.start()
