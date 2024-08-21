from stellar.interfaces.renderer import RendererInterface
from stellar.interfaces.window import WindowEngineInterface
from stellar.settings.config import config
from stellar.components.cursor import Cursor
import logging


class NewRenderer(RendererInterface):
    def __init__(self, window: WindowEngineInterface) -> None:
        logging.debug("Initializing NewRenderer with window: %s", window)
        self.window = window
        self.font = None
        self.char_width = 0
        self.char_height = 0
        self.text_color = config.text_color
        self.bg_color = config.bg_color
        self.padding = config.padding
        self.cols = config.cols
        self.rows = config.rows

        # Log configuration settings
        logging.debug(
            "Renderer Config - cols: %d, rows: %d, text_color: %s, bg_color: %s",
            self.cols,
            self.rows,
            self.text_color,
            self.bg_color,
        )

        self.buffer = [
            [(" ", self.text_color, self.bg_color) for _ in range(self.cols)]
            for _ in range(self.rows)
        ]
        self.cursor = Cursor(
            x=0,
            y=0,
            blink_interval=config.cursor_blink_interval,
            cursor_type=config.cursor_type,
        )
        logging.debug(
            "Cursor initialized with blink_interval: %d, cursor_type: %s",
            config.cursor_blink_interval,
            config.cursor_type,
        )

        self.theme = config.theme
        self.create_font()
        self.escape_buffer = ""
        self.current_fg_color = self.text_color
        self.current_bg_color = self.bg_color
        self.initial_output_processed = False

    def create_font(self):
        logging.debug(
            "Creating font with font_family: %s, font_size: %d",
            config.font_family,
            config.font_size,
        )
        if self.window.root_exists():
            self.font = self.window.create_font(config.font_family, config.font_size)
            if self.font:
                self.char_width = self.font.measure("m")
                self.char_height = self.font.metrics("linespace")
                logging.debug(
                    "Font created: char_width = %d, char_height = %d",
                    self.char_width,
                    self.char_height,
                )
            else:
                logging.warning("Font creation failed.")
        else:
            logging.warning("Window root does not exist. Font creation deferred.")

    def render_frame(self) -> None:
        logging.debug("Rendering frame")
        if not self.font:
            logging.debug("Font not available. Attempting to create font.")
            self.create_font()
            if not self.font:
                logging.error("Cannot render frame: Font not created.")
                return

        self.window.clear()
        width, height = self.window.get_size()
        logging.debug("Window size - width: %d, height: %d", width, height)
        self.window.draw_rectangle(0, 0, width, height, self.bg_color)

        for y, line in enumerate(self.buffer):
            x = self.padding
            current_fg = self.text_color
            current_bg = self.bg_color
            current_segment = ""
            for char, fg, bg in line:
                if fg != current_fg or bg != current_bg:
                    if current_segment:
                        self.window.draw_text(
                            current_segment,
                            x,
                            y * self.char_height + self.padding,
                            current_fg,
                            self.font,
                            current_bg,
                        )
                        logging.debug(
                            "Drawing text segment '%s' at x=%d, y=%d",
                            current_segment,
                            x,
                            y,
                        )
                        x += self.font.measure(current_segment)
                        current_segment = ""
                    current_fg, current_bg = fg, bg
                current_segment += char
            if current_segment:
                self.window.draw_text(
                    current_segment,
                    x,
                    y * self.char_height + self.padding,
                    current_fg,
                    self.font,
                    current_bg,
                )
                logging.debug(
                    "Drawing text segment '%s' at end of line", current_segment
                )

        self.cursor.update_blink()
        if self.cursor.is_visible():
            logging.debug("Cursor is visible. Drawing cursor.")
            cursor_x = self.cursor.x * self.char_width + self.padding
            cursor_y = self.cursor.y * self.char_height + self.padding
            self.draw_cursor(cursor_x, cursor_y)

        self.window.update()

    def write_char(
        self, char: str, x: int, y: int, fg_color: str, bg_color: str
    ) -> int:
        logging.debug("Writing character '%s' at x=%d, y=%d", char, x, y)
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.buffer[y][x] = (char, fg_color, bg_color)
            return 1
        logging.warning("Write attempt outside of buffer bounds: x=%d, y=%d", x, y)
        return 0

    def handle_pty_output(self, output: str) -> None:
        logging.debug("Handling PTY output: %s", output)
        if not self.initial_output_processed:
            logging.debug("Initial output not yet processed. Clearing screen.")
            self.clear_screen()
            self.initial_output_processed = True
            prompt_index = output.rfind("\n")
            if prompt_index != -1:
                output = output[prompt_index + 1 :]
                logging.debug("Trimmed initial PTY output to: %s", output)

        for char in output:
            if char == "\n":
                logging.debug("New line detected.")
                self.new_line()
            elif char == "\r":
                logging.debug("Carriage return detected.")
                self.cursor.move(0, self.cursor.y)
            elif char == "\b":
                logging.debug("Backspace detected.")
                self.handle_backspace()
            elif char == "\x1b":
                logging.debug("Escape sequence start detected.")
                self.escape_buffer += char
            elif self.escape_buffer:
                self.escape_buffer += char
                if char.isalpha():
                    logging.debug(
                        "Full escape sequence detected: %s", self.escape_buffer
                    )
                    self.handle_escape_sequence(self.escape_buffer)
                    self.escape_buffer = ""
            else:
                self.write_char(
                    char,
                    self.cursor.x,
                    self.cursor.y,
                    self.current_fg_color,
                    self.current_bg_color,
                )
                self.cursor.move(self.cursor.x + 1, self.cursor.y)
                if self.cursor.x >= self.cols:
                    logging.debug("Cursor reached end of line. Moving to new line.")
                    self.new_line()

    def clear_screen(self) -> None:
        logging.debug("Clearing screen")
        self.buffer = [
            [
                (" ", self.current_fg_color, self.current_bg_color)
                for _ in range(self.cols)
            ]
            for _ in range(self.rows)
        ]
        self.cursor.move(0, 0)

    def new_line(self):
        logging.debug("New line initiated.")
        self.cursor.move(0, self.cursor.y + 1)
        if self.cursor.y >= self.rows:
            logging.debug("Reached the bottom of the buffer. Scrolling up.")
            self.buffer.pop(0)
            self.buffer.append(
                [
                    (" ", self.current_fg_color, self.current_bg_color)
                    for _ in range(self.cols)
                ]
            )
            self.cursor.move(0, self.rows - 1)

    def handle_backspace(self):
        logging.debug("Handling backspace")
        if self.cursor.x > 0:
            self.cursor.move(self.cursor.x - 1, self.cursor.y)
            self.write_char(
                " ",
                self.cursor.x,
                self.cursor.y,
                self.current_fg_color,
                self.current_bg_color,
            )
        elif self.cursor.y > 0:
            self.cursor.move(self.cols - 1, self.cursor.y - 1)
            self.write_char(
                " ",
                self.cursor.x,
                self.cursor.y,
                self.current_fg_color,
                self.current_bg_color,
            )

    def handle_escape_sequence(self, sequence):
        logging.debug("Handling escape sequence: %s", sequence)
        # Add ANSI escape sequence handling here
        pass

    def draw_cursor(self, x: int, y: int):
        logging.debug("Drawing cursor at x=%d, y=%d", x, y)
        cursor_type = self.cursor.get_cursor_type()
        if cursor_type == "block":
            self.window.draw_rectangle(
                x, y, x + self.char_width, y + self.char_height, self.current_fg_color
            )
        elif cursor_type == "underscore":
            self.window.draw_rectangle(
                x,
                y + self.char_height - 2,
                x + self.char_width,
                y + self.char_height,
                self.current_fg_color,
            )
        elif cursor_type == "bar":
            self.window.draw_rectangle(
                x, y, x + 2, y + self.char_height, self.current_fg_color
            )

    def resize(self, cols: int, rows: int) -> None:
        logging.debug("Resizing renderer to cols=%d, rows=%d", cols, rows)
        new_buffer = [
            [(" ", self.current_fg_color, self.current_bg_color) for _ in range(cols)]
            for _ in range(rows)
        ]
        for y in range(min(self.rows, rows)):
            for x in range(min(self.cols, cols)):
                new_buffer[y][x] = self.buffer[y][x]
        self.buffer = new_buffer
        self.cols = cols
        self.rows = rows
        self.cursor.move(min(self.cursor.x, cols - 1), min(self.cursor.y, rows - 1))

    def get_cursor_position(self) -> tuple[int, int]:
        logging.debug("Getting cursor position")
        return self.cursor.x, self.cursor.y

    def set_cursor_position(self, x: int, y: int) -> None:
        logging.debug("Setting cursor position to x=%d, y=%d", x, y)
        self.cursor.move(max(0, min(x, self.cols - 1)), max(0, min(y, self.rows - 1)))

    def handle_input(self, char: str) -> None:
        """Handle input from the user"""
        pass
