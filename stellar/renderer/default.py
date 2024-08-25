from stellar.interfaces.renderer import RendererInterface
from stellar.engines.tkinter import TkinterWindow
from stellar.utils.ansi_parser import ANSIParser
from stellar.settings.config import Config
from typing import Tuple
import tkinter.font as tkfont
import logging

logger = logging.getLogger(__name__)


class DefaultRenderer(RendererInterface):
    def __init__(self, window: TkinterWindow, config: Config):
        logger.debug("Initializing DefaultRenderer")
        self.window = window
        self.config = config
        self.theme = config.theme
        self.width = 0
        self.height = 0
        self.buffer = []
        self.previous_buffer = []  # New: to track previous state
        self.cursor_x = 0
        self.cursor_y = 0
        self.cursor_visible = True

        self.ansi_parser = ANSIParser(self.theme)

        # Defer font creation
        self.font = None
        self.char_width = None
        self.char_height = None
        logger.debug("DefaultRenderer initialized")

    def _initialize_font(self):
        logger.debug("Initializing font")
        if self.font is None:
            try:
                self.font = tkfont.Font(
                    family=self.config.font_family, size=self.config.font_size
                )
                self.char_width = self.font.measure("W")
                self.char_height = self.font.metrics()["linespace"]
                logger.debug(
                    f"Font initialized: {self.config.font_family}, size {self.config.font_size}"
                )
            except Exception as e:
                logger.error(f"Error initializing font: {e}")
                raise

    def initialize(self, width: int, height: int) -> None:
        logger.debug(f"Initializing renderer with size: {width}x{height}")
        self._initialize_font()
        self.width = width
        self.height = height
        self.buffer = [
            [
                (" ", self.ansi_parser.default_fg, self.ansi_parser.default_bg)
                for _ in range(width)
            ]
            for _ in range(height)
        ]
        # Initialize the previous buffer with the same dimensions
        self.previous_buffer = [
            [
                (" ", self.ansi_parser.default_fg, self.ansi_parser.default_bg)
                for _ in range(width)
            ]
            for _ in range(height)
        ]
        try:
            self.window.canvas.config(
                width=width * self.char_width, height=height * self.char_height
            )
            logger.debug("Canvas configured")
        except Exception as e:
            logger.error(f"Error configuring canvas: {e}")
            raise

    def draw_char(
        self,
        x: int,
        y: int,
        char: str,
        fg_color: Tuple[int, int, int],
        bg_color: Tuple[int, int, int],
    ) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y][x] = (char, fg_color, bg_color)
            fg_hex = f"#{fg_color[0]:02x}{fg_color[1]:02x}{fg_color[2]:02x}"
            bg_hex = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
            try:
                self.window.canvas.create_rectangle(
                    x * self.char_width,
                    y * self.char_height,
                    (x + 1) * self.char_width,
                    (y + 1) * self.char_height,
                    fill=bg_hex,
                    outline="",
                )
                self.window.canvas.create_text(
                    x * self.char_width + self.char_width // 2,
                    y * self.char_height + self.char_height // 2,
                    text=char,
                    fill=fg_hex,
                    font=self.font,
                )
            except Exception as e:
                logger.error(f"Error drawing character at ({x}, {y}): {e}")

    def refresh(self) -> None:
        logger.debug("Refreshing renderer")
        try:
            for y in range(self.height):
                for x in range(self.width):
                    char, fg, bg = self.buffer[y][x]
                    if self.needs_redraw(x, y, char, fg, bg):
                        self.draw_char(x, y, char, fg, bg)

            # Update the previous buffer after drawing
            self.previous_buffer = [row[:] for row in self.buffer]

            self._draw_cursor()
            logger.debug("Refresh completed")
        except Exception as e:
            logger.error(f"Error during refresh: {e}")

    def needs_redraw(
        self,
        x: int,
        y: int,
        char: str,
        fg: Tuple[int, int, int],
        bg: Tuple[int, int, int],
    ) -> bool:
        """Determine if the cell at (x, y) needs to be redrawn."""
        previous_char, previous_fg, previous_bg = self.previous_buffer[y][x]

        # Check if the character or colors have changed
        return char != previous_char or fg != previous_fg or bg != previous_bg

    def handle_pty_output(self, output: str) -> None:
        logger.debug(f"Handling PTY output: {repr(output)}")
        try:
            parsed = self.ansi_parser.parse(output)
            for char_info in parsed:
                if char_info["char"] == "\n":
                    self.cursor_x = 0
                    self.cursor_y += 1
                    if self.cursor_y >= self.height:
                        self.scroll_up()
                        self.cursor_y = self.height - 1
                elif char_info["char"] == "\r":
                    self.cursor_x = 0
                else:
                    self.draw_char(
                        self.cursor_x,
                        self.cursor_y,
                        char_info["char"],
                        char_info["fg"],
                        char_info["bg"],
                    )
                    self.cursor_x += 1
                    if self.cursor_x >= self.width:
                        self.cursor_x = 0
                        self.cursor_y += 1
                        if self.cursor_y >= self.height:
                            self.scroll_up()
                            self.cursor_y = self.height - 1

            self.set_cursor(self.cursor_x, self.cursor_y)
            self.refresh()
            logger.debug("PTY output handled successfully")
        except Exception as e:
            logger.error(f"Error handling PTY output: {e}")

    # Implement the missing abstract methods

    def clear(self) -> None:
        logger.debug("Clearing screen")
        self.buffer = [
            [
                (" ", self.ansi_parser.default_fg, self.ansi_parser.default_bg)
                for _ in range(self.width)
            ]
            for _ in range(self.height)
        ]
        self.refresh()

    def draw_string(
        self,
        x: int,
        y: int,
        string: str,
        fg_color: Tuple[int, int, int],
        bg_color: Tuple[int, int, int],
    ) -> None:
        logger.debug(f"Drawing string: {string} at ({x}, {y})")
        parsed = self.ansi_parser.parse(string)
        for i, char_info in enumerate(parsed):
            if x + i >= self.width:
                break
            self.draw_char(
                x + i, y, char_info["char"], char_info["fg"], char_info["bg"]
            )

    def get_size(self) -> Tuple[int, int]:
        return self.width, self.height

    def hide_cursor(self) -> None:
        logger.debug("Hiding cursor")
        self.cursor_visible = False
        self._draw_cursor()

    def show_cursor(self) -> None:
        logger.debug("Showing cursor")
        self.cursor_visible = True
        self._draw_cursor()

    def set_cursor(self, x: int, y: int) -> None:
        self.cursor_x = max(0, min(x, self.width - 1))
        self.cursor_y = max(0, min(y, self.height - 1))
        self._draw_cursor()

    def _draw_cursor(self) -> None:
        self.window.canvas.delete("cursor")
        if self.cursor_visible:
            x = self.cursor_x * self.char_width
            y = self.cursor_y * self.char_height
            cursor_color = self.theme.hex_to_rgb(self.theme.get_default_fg())
            cursor_hex = (
                f"#{cursor_color[0]:02x}{cursor_color[1]:02x}{cursor_color[2]:02x}"
            )
            if self.config.cursor_type == "block":
                self.window.canvas.create_rectangle(
                    x,
                    y,
                    x + self.char_width,
                    y + self.char_height,
                    outline=cursor_hex,
                    width=2,
                    tags="cursor",
                )
            elif self.config.cursor_type == "underline":
                self.window.canvas.create_line(
                    x,
                    y + self.char_height - 1,
                    x + self.char_width,
                    y + self.char_height - 1,
                    fill=cursor_hex,
                    width=2,
                    tags="cursor",
                )

    def scroll_up(self) -> None:
        self.buffer = self.buffer[1:] + [
            [
                (" ", self.ansi_parser.default_fg, self.ansi_parser.default_bg)
                for _ in range(self.width)
            ]
        ]
        self.previous_buffer = self.previous_buffer[1:] + [
            [
                (" ", self.ansi_parser.default_fg, self.ansi_parser.default_bg)
                for _ in range(self.width)
            ]
        ]
        self.refresh()
