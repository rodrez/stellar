# stellar/engines/tkinter.py

import tkinter as tk
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TkinterWindow:
    def __init__(self):
        logger.debug("Initializing TkinterWindow")
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self.width: int = 0
        self.height: int = 0
        self.is_running: bool = False
        logger.debug("TkinterWindow initialized")

    def create_window(self, title: str, width: int, height: int) -> None:
        logger.debug(f"Creating Tkinter window: {title} ({width}x{height})")
        self.root = tk.Tk()
        self.root.title(title)
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.resizable(False, False)  # Disable window resizing
        self.is_running = True
        logger.debug("Tkinter window created")

    def handle_events(self) -> None:
        logger.debug("Handling Tkinter events")
        # We'll handle events in the main loop

    def handle_input(self) -> str:
        # This is a placeholder. You'll need to implement proper input handling.
        return ""

    def update(self) -> None:
        if self.is_running and self.root:
            try:
                self.root.update_idletasks()
                self.root.update()
            except tk.TclError as e:
                logger.error(f"Tkinter update error: {e}")
                self.is_running = False

    def is_alive(self) -> bool:
        return self.is_running

    def get_size(self) -> Tuple[int, int]:
        return self.width, self.height

    def on_close(self) -> None:
        logger.info("Closing Tkinter window")
        self.is_running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
        logger.debug("Tkinter window closed")
