import logging
from stellar.interfaces.input import InputInterface
from stellar.interfaces.window import WindowInterface


class KeyboardHandler(InputInterface):
    def __init__(self, window: WindowInterface) -> None:
        self.window = window
        self.key_buffer = []
        logging.info("KeyboardHandler initialized.")

    def handle_input(self):
        if self.key_buffer:
            key = self.key_buffer.pop(0)
            logging.info(f"Handling input: '{key}'")
            return key
        return None

    def on_key_press(self, event):
        if event.char:
            logging.info(f"Key pressed: '{event.char}'")
            self.key_buffer.append(event.char)
        elif event.keysym == "Return":
            logging.info("Key pressed: 'Return'")
            self.key_buffer.append("\n")
        elif event.keysym == "BackSpace":
            logging.info("Key pressed: 'BackSpace'")
            self.key_buffer.append("\b")
