import re
from typing import Tuple
from stellar.interfaces.renderer import RenderInterface
from stellar.interfaces.window import WindowInterface
from stellar.setings.config import config
from stellar.components.cursor import Cursor
import logging


class DefaultRenderer(RenderInterface):
    def __init__(self, window: WindowInterface) -> None:
        self.window = window
        self.font = None
        self.char_width = 0
        self.char_height = 0
        self.text_color = config.text_color
        self.bg_color = config.bg_color
        self.padding = config.padding
        self.cols = config.cols
        self.rows = config.rows
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
        self.theme = config.theme
        self.create_font()
        self.escape_buffer = ""
        self.current_fg_color = self.text_color
        self.current_bg_color = self.bg_color

    def create_font(self):
        if self.window.root_exists():
            self.font = self.window.create_font(config.font_family, config.font_size)
            if self.font:
                self.char_width = self.font.measure("m")
                self.char_height = self.font.metrics("linespace")
        else:
            logging.warning("Window root does not exist. Font creation deferred.")

    def render_frame(self) -> None:
        if not self.font:
            self.create_font()
            if not self.font:
                logging.error("Cannot render frame: Font not created.")
                return

        self.window.clear()
        width, height = self.window.get_size()
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

        # Handle cursor blinking and drawing
        self.cursor.update_blink()
        if self.cursor.is_visible():
            cursor_x = self.cursor.x * self.char_width + self.padding
            cursor_y = self.cursor.y * self.char_height + self.padding
            self.draw_cursor(cursor_x, cursor_y)

        self.window.update()

    def write_char(
        self, char: str, x: int, y: int, fg_color: str, bg_color: str
    ) -> int:
        logging.info(
            f"Writing ({char}), at x {x}, at y {y}, fc {fg_color} and bg {bg_color}"
        )
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.buffer[y][x] = (char, fg_color, bg_color)
            return 1
        return 0

    def handle_pty_output(self, output: str) -> None:
        logging.debug(f"Received PTY output: {repr(output)}")
        i = 0
        while i < len(output):
            char = output[i]
            if self.escape_buffer or char == "\x1b":
                self.escape_buffer += char
                if self.escape_buffer[-1] in "ABCDEFGHJKSTfmnsulh":
                    self.handle_escape_sequence(self.escape_buffer)
                    self.escape_buffer = ""
                i += 1
            elif char == "\n":
                self.new_line()
                i += 1
            elif char == "\r":
                self.cursor.move(0, self.cursor.y)
                i += 1
            elif char == "\b":
                self.handle_backspace()
                i += 1
            # elif char == "\x7f":  # DEL character
            #     if i + 2 < len(output) and output[i + 1 : i + 3] == "\x1b[":
            #         # This is likely a DEL followed by cursor backward sequence
            #         self.handle_backspace()
            #         i += 3
            #     else:
            #         # Treat it as a regular backspace
            #         self.handle_backspace()
            #         i += 1
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
                    self.new_line()
                i += 1

    def handle_escape_sequence(self, sequence):
        logging.debug(f"Handling escape sequence: {repr(sequence)}")
        if sequence.endswith("J"):  # Clear screen
            if sequence == "\x1b[2J" or sequence == "\x1b[J":
                self.clear_screen()
                self.cursor.move(0, 0)  # Move cursor to home position
            elif sequence == "\x1b[1J":
                self.clear_screen_to_cursor()
            elif sequence == "\x1b[0J":
                self.clear_screen_from_cursor()
        elif sequence.endswith("K"):  # Clear line
            if sequence == "\x1b[2K" or sequence == "\x1b[K":
                self.clear_line()
            elif sequence == "\x1b[1K":
                self.clear_line_to_cursor()
            elif sequence == "\x1b[0K":
                self.clear_line_from_cursor()
        elif sequence.endswith("H") or sequence.endswith("f"):  # Move cursor
            match = re.match(r"\x1b\[(\d+)?;?(\d+)?[Hf]", sequence)
            if match:
                row, col = match.groups()
                row = int(row) if row else 1
                col = int(col) if col else 1
                self.set_cursor_position(col - 1, row - 1)
        elif sequence.endswith("m"):  # Set graphics mode (colors, etc.)
            self.set_graphics_mode(sequence)
        elif sequence.startswith("\x1b[") and sequence[-1] in "ABCD":  # Cursor movement
            count = int(sequence[2:-1]) if len(sequence) > 3 else 1
            x, y = self.get_cursor_position()
            if sequence[-1] == "A":  # Up
                self.set_cursor_position(x, max(0, y - count))
            elif sequence[-1] == "B":  # Down
                self.set_cursor_position(x, min(self.rows - 1, y + count))
            elif sequence[-1] == "C":  # Forward
                self.set_cursor_position(min(self.cols - 1, x + count), y)
            elif sequence[-1] == "D":  # Backward
                self.set_cursor_position(max(0, x - count), y)

    def handle_backspace(self):
        if self.cursor.x > 0:
            # Move cursor back
            self.cursor.move(self.cursor.x - 1, self.cursor.y)
            # Clear the character at the new cursor position
            self.write_char(
                " ",
                self.cursor.x,
                self.cursor.y,
                self.current_fg_color,
                self.current_bg_color,
            )
            # Move cursor back again to position it correctly
            self.cursor.move(self.cursor.x, self.cursor.y)
        elif self.cursor.y > 0:
            # Move to the end of the previous line
            self.cursor.move(self.cols - 1, self.cursor.y - 1)
            # Clear the character at the new cursor position
            self.write_char(
                " ",
                self.cursor.x,
                self.cursor.y,
                self.current_fg_color,
                self.current_bg_color,
            )
            # Move cursor back again to position it correctly
            self.cursor.move(self.cursor.x, self.cursor.y)

    def handle_input(self, char: str) -> None:
        # This method might be used for local echo if needed
        pass

    def clear_screen(self) -> None:
        self.buffer = [
            [
                (" ", self.current_fg_color, self.current_bg_color)
                for _ in range(self.cols)
            ]
            for _ in range(self.rows)
        ]
        self.cursor.move(0, 0)

    def resize(self, cols: int, rows: int) -> None:
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

    def get_cursor_position(self) -> Tuple[int, int]:
        return self.cursor.x, self.cursor.y

    def set_cursor_position(self, x: int, y: int) -> None:
        self.cursor.move(max(0, min(x, self.cols - 1)), max(0, min(y, self.rows - 1)))

    def clear_screen_to_cursor(self):
        x, y = self.get_cursor_position()
        for cy in range(y):
            self.buffer[cy] = [
                (" ", self.current_fg_color, self.current_bg_color)
                for _ in range(self.cols)
            ]
        for cx in range(x + 1):
            self.buffer[y][cx] = (" ", self.current_fg_color, self.current_bg_color)

    def clear_screen_from_cursor(self):
        x, y = self.get_cursor_position()
        for cy in range(y + 1, self.rows):
            self.buffer[cy] = [
                (" ", self.current_fg_color, self.current_bg_color)
                for _ in range(self.cols)
            ]
        for cx in range(x, self.cols):
            self.buffer[y][cx] = (" ", self.current_fg_color, self.current_bg_color)

    def clear_line(self):
        y = self.cursor.y
        self.buffer[y] = [
            (" ", self.current_fg_color, self.current_bg_color)
            for _ in range(self.cols)
        ]

    def clear_line_to_cursor(self):
        x, y = self.get_cursor_position()
        for cx in range(x + 1):
            self.buffer[y][cx] = (" ", self.current_fg_color, self.current_bg_color)

    def clear_line_from_cursor(self):
        x, y = self.get_cursor_position()
        for cx in range(x, self.cols):
            self.buffer[y][cx] = (" ", self.current_fg_color, self.current_bg_color)

    def set_graphics_mode(self, sequence):
        codes = [int(code) for code in sequence[2:-1].split(";") if code]
        for code in codes:
            if code == 0:  # Reset
                self.current_fg_color = self.text_color
                self.current_bg_color = self.bg_color
            elif 30 <= code <= 37:  # Foreground color
                self.current_fg_color = self.theme.get_normal_color(
                    [
                        "black",
                        "red",
                        "green",
                        "yellow",
                        "blue",
                        "magenta",
                        "cyan",
                        "white",
                    ][code - 30]
                )
            elif 40 <= code <= 47:  # Background color
                self.current_bg_color = self.theme.get_normal_color(
                    [
                        "black",
                        "red",
                        "green",
                        "yellow",
                        "blue",
                        "magenta",
                        "cyan",
                        "white",
                    ][code - 40]
                )

    def new_line(self):
        x, y = self.get_cursor_position()
        self.set_cursor_position(0, y + 1)
        if y + 1 >= self.rows:
            self.buffer.pop(0)
            self.buffer.append(
                [
                    (" ", self.current_fg_color, self.current_bg_color)
                    for _ in range(self.cols)
                ]
            )
            self.set_cursor_position(0, self.rows - 1)

    def draw_cursor(self, x: int, y: int):
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

    def reload_config(self):
        config.reload()
        self.create_font()
        self.text_color = config.text_color
        self.bg_color = config.bg_color
        self.padding = config.padding
        self.resize(config.cols, config.rows)
        self.cursor.set_blink_interval(config.cursor_blink_interval)
        self.theme = config.theme
