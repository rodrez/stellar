from stellar.interfaces.renderer import RenderInterface
from stellar.interfaces.window import WindowInterface
from stellar.setings.config import config
import logging


class DefaultRenderer(RenderInterface):
    def __init__(self, window: WindowInterface) -> None:
        self.window = window
        self.cursor_x = 0
        self.cursor_y = 0
        self.font = None
        self.char_width = None
        self.char_height = None
        self.text_color = config.text_color
        self.bg_color = config.bg_color
        self.padding = config.padding
        self.cols = config.cols
        self.rows = config.rows
        self.buffer = [[" " for _ in range(self.cols)] for _ in range(self.rows)]

        # Attempt to create the font
        self.create_font()

    def create_font(self):
        if self.window.root_exists():
            self.font = self.window.create_font(config.font_family, config.font_size)
            if self.font:
                self.char_width = self.font.measure("m")
                self.char_height = self.font.metrics("linespace")
        else:
            logging.warning("Window root does not exist. Font creation deferred.")

    def render_frame(self) -> None:
        """Renders a single frame to the terminal"""
        if not self.font:
            self.create_font()
            if not self.font:
                logging.error("Cannot render frame: Font not created.")
                return

        self.window.clear()
        width, height = self.window.get_size()
        self.window.draw_rectangle(0, 0, width, height, self.bg_color)

        for y, line in enumerate(self.buffer):
            self.window.draw_text(
                "".join(line),
                self.padding,
                y * self.char_height + self.padding,
                self.text_color,
                self.font,
            )

        # Draw cursor
        cursor_x = self.cursor_x * self.char_width + self.padding
        cursor_y = self.cursor_y * self.char_height + self.padding
        self.window.draw_rectangle(
            cursor_x,
            cursor_y,
            cursor_x + self.char_width,
            cursor_y + self.char_height,
            self.text_color,
        )

        self.window.update()

    def update_cursor(self, x: int, y: int) -> None:
        """Update the cursor position"""
        self.cursor_x = x
        self.cursor_y = y

    def write_char(self, char: str, x: int, y: int) -> None:
        """Write a character at the specified position"""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.buffer[y][x] = char
            logging.debug(f"Character '{char}' written at ({x}, {y})")

    def handle_input(self, char: str) -> None:
        """Handle input and update the buffer"""
        logging.debug(f"Handling input: {char}")
        if char == "\n":
            self.cursor_x = 0
            self.cursor_y = min(self.cursor_y + 1, self.rows - 1)
        elif char == "\b":
            if self.cursor_x > 0:
                self.cursor_x -= 1
                self.write_char(" ", self.cursor_x, self.cursor_y)
        else:
            self.write_char(char, self.cursor_x, self.cursor_y)
            self.cursor_x += 1
            if self.cursor_x >= self.cols:
                self.cursor_x = 0
                self.cursor_y = min(self.cursor_y + 1, self.rows - 1)

        # Handle scrolling if we've reached the bottom of the buffer
        if self.cursor_y >= self.rows:
            self.buffer.pop(0)
            self.buffer.append([" " for _ in range(self.cols)])
            self.cursor_y = self.rows - 1

        logging.debug(
            f"Cursor position after input: ({self.cursor_x}, {self.cursor_y})"
        )

    def reload_config(self):
        """Reload the configuration and update renderer settings"""
        config.reload()
        self.create_font()
        self.text_color = config.text_color
        self.bg_color = config.bg_color
        self.padding = config.padding
        self.cols = config.cols
        self.rows = config.rows
        self.buffer = [[" " for _ in range(self.cols)] for _ in range(self.rows)]
