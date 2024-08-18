from stellar.components.prompt import Prompt
from stellar.interfaces.renderer import RenderInterface
from stellar.interfaces.window import WindowInterface
from stellar.plugins.manager import PluginManager
from stellar.setings.config import config
from stellar.components.cursor import Cursor
import logging


class DefaultRenderer(RenderInterface):
    def __init__(self, window: WindowInterface) -> None:
        self.window = window
        self.font = None
        self.char_width = None
        self.char_height = None
        self.text_color = config.text_color
        self.bg_color = config.bg_color
        self.padding = config.padding
        self.cols = config.cols
        self.rows = config.rows
        self.buffer = [
            [(" ", self.text_color) for _ in range(self.cols)] for _ in range(self.rows)
        ]
        self.plugin_manager = PluginManager()
        self.plugin_manager.discover_plugins("stellar/plugins")
        self.plugin_manager.initialize_plugins(self)

        self.prompt = Prompt(self.plugin_manager)
        self.input_start_x = 0  # Will be set after writing the prompt
        self.current_color = self.text_color

        self.cursor = Cursor(x=0, y=0, blink_interval=config.cursor_blink_interval)

        self.theme = config.theme

        self.create_font()
        self.write_prompt()

    def create_font(self):
        if self.window.root_exists():
            self.font = self.window.create_font(config.font_family, config.font_size)
            if self.font:
                self.char_width = self.font.measure("m")
                self.char_height = self.font.metrics("linespace")
        else:
            logging.warning("Window root does not exist. Font creation deferred.")

    def write_prompt(self):
        prompt_string = self.prompt.prompt_string
        prompt_color = self.theme.get_bright_color("green")
        x = 0
        for char in prompt_string:
            self.write_char(char, x, self.cursor.y, prompt_color)
            x += 1
        self.input_start_x = x
        self.cursor.move(self.input_start_x, self.cursor.y)

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
            current_color = self.text_color
            current_segment = ""
            for char, color in line:
                if color != current_color:
                    if current_segment:
                        self.window.draw_text(
                            current_segment,
                            x,
                            y * self.char_height + self.padding,
                            current_color,
                            self.font,
                        )
                        x += self.font.measure(current_segment)
                        current_segment = ""
                    current_color = color
                current_segment += char
            if current_segment:
                self.window.draw_text(
                    current_segment,
                    x,
                    y * self.char_height + self.padding,
                    current_color,
                    self.font,
                )

        # Handle cursor blinking and drawing
        self.cursor.update_blink()
        if self.cursor.is_visible():
            cursor_x = self.cursor.x * self.char_width + self.padding
            cursor_y = self.cursor.y * self.char_height + self.padding
            self.window.draw_rectangle(
                cursor_x,
                cursor_y,
                cursor_x + self.char_width,
                cursor_y + self.char_height,
                self.text_color,
            )

        self.window.update()

    def write_char(self, char: str, x: int, y: int, color: str = None) -> int:
        if 0 <= x < self.cols and 0 <= y < self.rows:
            char_color = color if color is not None else self.current_color
            self.buffer[y][x] = (char, char_color)
            return 1
        return 0

    def handle_input(self, char: str) -> None:
        logging.debug(f"Handling input: {char}")
        if char == "\n":
            self.execute_command()
        elif char == "\b":
            if self.cursor.x > self.input_start_x:
                self.cursor.move(self.cursor.x - 1, self.cursor.y)
                self.write_char(" ", self.cursor.x, self.cursor.y)
        else:
            if self.cursor.x < self.cols:
                self.write_char(char, self.cursor.x, self.cursor.y)
                self.cursor.move(self.cursor.x + 1, self.cursor.y)

        self.cursor.reset_blink()

    def execute_command(self):
        command = "".join(
            char
            for char, _ in self.buffer[self.cursor.y][
                self.input_start_x : self.cursor.x
            ]
        ).strip()
        logging.debug(f"Executing command: {command}")

        self.cursor.move(0, self.cursor.y + 1)
        if self.cursor.y >= self.rows:
            self.buffer.pop(0)
            self.buffer.append([(" ", self.text_color) for _ in range(self.cols)])
            self.cursor.move(self.cursor.x, self.rows - 1)

        # Apply colors to the output
        output = f"Echoing: {command}"
        output_color = self.theme.get_bright_color("blue")

        for char in output:
            chars_written = self.write_char(
                char, self.cursor.x, self.cursor.y, output_color
            )
            self.cursor.move(self.cursor.x + chars_written, self.cursor.y)
            if self.cursor.x >= self.cols:
                self.cursor.move(0, self.cursor.y + 1)
                if self.cursor.y >= self.rows:
                    self.buffer.pop(0)
                    self.buffer.append(
                        [(" ", self.text_color) for _ in range(self.cols)]
                    )
                    self.cursor.move(self.cursor.x, self.rows - 1)

        self.cursor.move(0, self.cursor.y + 1)
        if self.cursor.y >= self.rows:
            self.buffer.pop(0)
            self.buffer.append([(" ", self.text_color) for _ in range(self.cols)])
            self.cursor.move(self.cursor.x, self.rows - 1)
        self.write_prompt()

    def reload_config(self):
        config.reload()
        self.create_font()
        self.text_color = config.text_color
        self.bg_color = config.bg_color
        self.padding = config.padding
        self.cols = config.cols
        self.rows = config.rows
        self.buffer = [
            [(" ", self.text_color) for _ in range(self.cols)] for _ in range(self.rows)
        ]
        self.cursor.set_blink_interval(config.cursor_blink_interval)
        self.theme = config.theme
        self.write_prompt()
