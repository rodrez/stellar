from typing import Tuple
import sdl2
import sdl2.ext
from stellar.interfaces.renderer import RenderInterface
from stellar.interfaces.window import WindowInterface
from stellar.setings.config import config
from stellar.components.cursor import Cursor


class SDLRenderer(RenderInterface):
    def __init__(self, window: WindowInterface) -> None:
        self.window = window
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self.sdl_window = sdl2.SDL_CreateWindow(
            b"Stellar Terminal",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            800,
            600,
            sdl2.SDL_WINDOW_SHOWN,
        )
        self.renderer = sdl2.SDL_CreateRenderer(
            self.sdl_window, -1, sdl2.SDL_RENDERER_ACCELERATED
        )
        self.font = sdl2.ext.FontTTF(
            font="/Users/fabianrodriguez/Library/Fonts/FiraCodeNerdFontMono-SemiBold.ttf",
            # config.font_family,
            size=config.font_size,
            color=config.text_color,
        )

        self.char_width, self.char_height = 18, 18  # self.font.size("X")
        self.cols = config.cols
        self.rows = config.rows
        self.buffer = [
            [(" ", config.text_color, config.bg_color) for _ in range(self.cols)]
            for _ in range(self.rows)
        ]
        self.cursor = Cursor(
            x=0,
            y=0,
            blink_interval=config.cursor_blink_interval,
            cursor_type=config.cursor_type,
        )

    def render_frame(self) -> None:
        sdl2.SDL_SetRenderDrawColor(
            self.renderer, *self._parse_color(config.bg_color), 255
        )
        sdl2.SDL_RenderClear(self.renderer)

        for y, line in enumerate(self.buffer):
            for x, (char, fg_color, bg_color) in enumerate(line):
                if char != " ":
                    self._render_char(char, x, y, fg_color, bg_color)

        self._render_cursor()
        sdl2.SDL_RenderPresent(self.renderer)

    def write_char(
        self, char: str, x: int, y: int, fg_color: str, bg_color: str
    ) -> int:
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.buffer[y][x] = (char, fg_color, bg_color)
            return 1
        return 0

    def handle_pty_output(self, output: str) -> None:
        for char in output:
            if char == "\n":
                self.cursor.move(0, self.cursor.y + 1)
            elif char == "\r":
                self.cursor.move(0, self.cursor.y)
            else:
                self.write_char(
                    char,
                    self.cursor.x,
                    self.cursor.y,
                    config.text_color,
                    config.bg_color,
                )
                self.cursor.move(self.cursor.x + 1, self.cursor.y)

            if self.cursor.x >= self.cols:
                self.cursor.move(0, self.cursor.y + 1)
            if self.cursor.y >= self.rows:
                self._scroll_buffer()

    def handle_input(self, char: str) -> None:
        # This method might be used for local echo if needed
        pass

    def clear_screen(self) -> None:
        self.buffer = [
            [(" ", config.text_color, config.bg_color) for _ in range(self.cols)]
            for _ in range(self.rows)
        ]
        self.cursor.move(0, 0)

    def resize(self, cols: int, rows: int) -> None:
        new_buffer = [
            [(" ", config.text_color, config.bg_color) for _ in range(cols)]
            for _ in range(rows)
        ]
        for y in range(min(self.rows, rows)):
            for x in range(min(self.cols, cols)):
                new_buffer[y][x] = self.buffer[y][x]
        self.buffer = new_buffer
        self.cols = cols
        self.rows = rows
        self.cursor.move(min(self.cursor.x, cols - 1), min(self.cursor.y, rows - 1))

        window_width = cols * self.char_width
        window_height = rows * self.char_height
        sdl2.SDL_SetWindowSize(self.sdl_window, window_width, window_height)

    def get_cursor_position(self) -> Tuple[int, int]:
        return self.cursor.x, self.cursor.y

    def set_cursor_position(self, x: int, y: int) -> None:
        self.cursor.move(max(0, min(x, self.cols - 1)), max(0, min(y, self.rows - 1)))

    def _render_char(
        self, char: str, x: int, y: int, fg_color: str, bg_color: str
    ) -> None:
        fg_r, fg_g, fg_b = self._parse_color(fg_color)
        bg_r, bg_g, bg_b = self._parse_color(bg_color)

        # Render background
        rect = sdl2.SDL_Rect(
            x * self.char_width, y * self.char_height, self.char_width, self.char_height
        )
        sdl2.SDL_SetRenderDrawColor(self.renderer, bg_r, bg_g, bg_b, 255)
        sdl2.SDL_RenderFillRect(self.renderer, rect)

        # Render text
        surface = self.font.render_text(char, fg_color)
        texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
        sdl2.SDL_RenderCopy(self.renderer, texture, None, rect)
        sdl2.SDL_FreeSurface(surface)
        sdl2.SDL_DestroyTexture(texture)

    def _render_cursor(self) -> None:
        if self.cursor.is_visible():
            x, y = self.cursor.x * self.char_width, self.cursor.y * self.char_height
            sdl2.SDL_SetRenderDrawColor(
                self.renderer, *self._parse_color(config.text_color), 255
            )
            rect = sdl2.SDL_Rect(
                x * self.char_width,
                y * self.char_height,
                self.char_width,
                self.char_height,
            )
            if self.cursor.get_cursor_type() == "block":
                sdl2.SDL_Rect(x, y, self.char_width, self.char_height)
            elif self.cursor.get_cursor_type() == "underscore":
                sdl2.SDL_Rect(x, y + self.char_height - 2, self.char_width, 2)
            elif self.cursor.get_cursor_type() == "bar":
                sdl2.SDL_Rect(x, y, 2, self.char_height)
            sdl2.SDL_RenderFillRect(self.renderer, rect)

    def _scroll_buffer(self) -> None:
        self.buffer.pop(0)
        self.buffer.append(
            [(" ", config.text_color, config.bg_color) for _ in range(self.cols)]
        )
        self.cursor.move(0, self.rows - 1)

    @staticmethod
    def _parse_color(color: str) -> Tuple[int, int, int]:
        return tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))

    def __del__(self):
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.sdl_window)
        sdl2.SDL_Quit()
