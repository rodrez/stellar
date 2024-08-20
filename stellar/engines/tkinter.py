import tkinter as tk
import tkinter.font as tkfont
import logging
from typing import Any
from stellar.interfaces.window import WindowInterface
from stellar.input.keyboard_handler import KeyboardHandler
from stellar.settings.config import config


class TkinterWindow(WindowInterface):
    def __init__(self) -> None:
        self.root: tk.Tk | None = None
        self.canvas: tk.Canvas | None = None
        self.width: int = 0
        self.height: int = 0
        self.keyboard_handler: KeyboardHandler | None = None

        # Initialize the theme here
        self.theme = config.theme
        logging.info("TkinterWindow initialized with theme.")

    def root_exists(self) -> bool:
        exists = bool(self.root and self.root.winfo_exists())
        logging.debug(f"Root exists: {exists}")
        return exists

    def create_font(self, family: str, size: int) -> tkfont.Font | None:
        if self.root_exists():
            logging.info(f"Creating font: {family}, size: {size}")
            return tkfont.Font(family=family, size=size, weight="normal")
        logging.warning("Font creation failed - root does not exist.")
        return None

    def create_window(self, title: str, width: int, height: int) -> None:
        self.root = tk.Tk()
        self.root.title(title)
        self.width = width
        self.height = height
        self.root.geometry(f"{width}x{height}")

        # Apply primary background color from theme
        self.canvas = tk.Canvas(
            self.root, width=width, height=height, bg=self.theme.get_primary_bg()
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        logging.info(
            f"Window '{title}' created with size {width}x{height} and theme background."
        )

        self.keyboard_handler = KeyboardHandler(self)
        self.root.bind("<Key>", self.keyboard_handler.on_key_press)
        self.root.bind("<Configure>", self.on_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        logging.info("Keyboard and resize event bindings added.")

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        foreground_color: str,
        font: Any,
        background_color: str,
    ):
        if self.canvas:
            if font:
                self.canvas.create_text(
                    x, y, text=text, fill=foreground_color, anchor="nw", font=font
                )
            else:
                logging.debug("Using default font.")
                self.canvas.create_text(
                    x, y, text=text, fill=foreground_color, anchor="nw"
                )
        else:
            logging.error("Cannot draw text: canvas not initialized.")

    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, color: str) -> None:
        if self.canvas:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        else:
            logging.error("Cannot draw rectangle: canvas not initialized.")

    def handle_events(self) -> None:
        logging.debug("Handling events (Tkinter mainloop placeholder).")

    def on_resize(self, event: tk.Event) -> None:
        if event.widget == self.root:
            self.width, self.height = event.width, event.height
            if self.canvas:
                self.canvas.config(width=self.width, height=self.height)
            logging.info(f"Window resized to {self.width}x{self.height}.")

    def on_close(self) -> None:
        if self.root:
            logging.info("Closing window.")
            self.root.quit()

    def run(self) -> None:
        if self.root:
            logging.info("Starting Tkinter mainloop.")
            self.root.mainloop()
        else:
            logging.error("Cannot run: root window not initialized.")

    def clear(self) -> None:
        if self.canvas:
            logging.debug("Clearing canvas.")
            self.canvas.delete("all")
            # Redraw the background
            self.canvas.create_rectangle(
                0,
                0,
                self.width,
                self.height,
                fill=self.theme.get_primary_bg(),
                outline="",
            )
        else:
            logging.error("Cannot clear: canvas not initialized.")

    def update(self) -> None:
        if self.root:
            self.root.update()
        else:
            logging.error("Cannot update: root window not initialized.")

    def is_alive(self) -> bool:
        alive = self.root is not None and self.canvas is not None
        logging.debug(f"Window is alive: {alive}")
        return alive

    def get_size(self) -> tuple[int, int]:
        logging.debug(f"Getting window size: {self.width}x{self.height}")
        return self.width, self.height

    def handle_input(self) -> str | None:
        if self.keyboard_handler:
            logging.debug("Handling keyboard input.")
            return self.keyboard_handler.handle_input()
        logging.debug("No keyboard handler available.")
        return None

    def reload_theme(self):
        """Reload the theme and update the window accordingly."""
        self.theme = config.theme  # Reload the theme from file
        if self.canvas:
            self.canvas.config(bg=self.theme.get_primary_bg())
            logging.info("Theme reloaded and applied to window.")
        else:
            logging.error("Cannot reload theme: canvas not initialized.")
