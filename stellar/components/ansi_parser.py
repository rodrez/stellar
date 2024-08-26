import re
from typing import List, Tuple, Dict, Union
from functools import lru_cache
import numpy as np

from stellar.components.ansi import ANSI_COLORS
from stellar.settings.config import Config


class ANSIParser:
    def __init__(self):
        self.theme = Config().theme
        self.reset_attributes()
        self.escape_sequence_pattern = re.compile(
            r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|[\u0080-\u009F]"
        )
        self.cursor_x = 0
        self.cursor_y = 0

        self.sgr_pattern = re.compile(r"\x1b\[([0-9;]*)m")
        self.cursor_pattern = re.compile(r"\x1b\[([0-9;]*)([ABCDEFGHJ])")

        # New attributes for title and CWD
        self.terminal_title = ""
        self.current_working_directory = ""

        # Updated patterns for title and CWD
        self.title_pattern = re.compile(r"\x1b]0;(.*?)\x07")
        self.cwd_pattern = re.compile(r"\x1b]7;file://(.*?)\x07")

        # Pre-compute color arrays
        self.ansi_colors = self._compute_ansi_colors()
        self.bright_ansi_colors = self._compute_bright_ansi_colors()

        # Pre-compute 256-color palette
        self.color_256 = self._generate_256_color_palette()

    def reset_attributes(self) -> None:
        self.foreground_color = np.array(
            self.theme.hex_to_rgb(self.theme.get_default_fg()), dtype=np.uint8
        )
        self.background_color = np.array(
            self.theme.hex_to_rgb(self.theme.get_default_bg()), dtype=np.uint8
        )
        self.bold = self.italic = self.underline = False

    @lru_cache(maxsize=None)
    def _compute_ansi_colors(self):
        return np.array(
            [
                self.theme.hex_to_rgb(self.theme.get_normal_color(color))
                for color in [
                    ANSI_COLORS.BLACK,
                    ANSI_COLORS.RED,
                    ANSI_COLORS.GREEN,
                    ANSI_COLORS.YELLOW,
                    ANSI_COLORS.BLUE,
                    ANSI_COLORS.MAGENTA,
                    ANSI_COLORS.CYAN,
                    ANSI_COLORS.WHITE,
                ]
            ],
            dtype=np.uint8,
        )

    @lru_cache(maxsize=None)
    def _compute_bright_ansi_colors(self):
        return np.array(
            [
                self.theme.hex_to_rgb(self.theme.get_bright_color(color))
                for color in [
                    ANSI_COLORS.BLACK,
                    ANSI_COLORS.RED,
                    ANSI_COLORS.GREEN,
                    ANSI_COLORS.YELLOW,
                    ANSI_COLORS.BLUE,
                    ANSI_COLORS.MAGENTA,
                    ANSI_COLORS.CYAN,
                    ANSI_COLORS.WHITE,
                ]
            ],
            dtype=np.uint8,
        )

    @lru_cache(maxsize=None)
    def _generate_256_color_palette(self) -> np.ndarray:
        palette = np.zeros((256, 3), dtype=np.uint8)
        # Standard 16 colors
        palette[:16] = np.vstack(
            (self._compute_ansi_colors(), self._compute_bright_ansi_colors())
        )
        # 216 color cube
        r = np.repeat(np.arange(0, 6, dtype=np.uint8), 36).reshape(-1, 1) * 51
        g = (
            np.tile(np.repeat(np.arange(0, 6, dtype=np.uint8), 6), 6).reshape(-1, 1)
            * 51
        )
        b = np.tile(np.arange(0, 6, dtype=np.uint8), 36).reshape(-1, 1) * 51
        palette[16:232] = np.hstack((r, g, b))
        # 24 grayscale colors
        gray = np.arange(8, 248, 10, dtype=np.uint8).reshape(-1, 1)
        palette[232:] = np.repeat(gray, 3, axis=1)
        return palette

    def parse(self, text: str) -> List[Tuple[str, Dict[str, Union[bool, np.ndarray]]]]:
        # Process title and CWD before other parsing
        print("Text before clan: ", text)
        self.process_title_and_cwd(text)

        # Remove title and CWD sequences from text
        text = self.title_pattern.sub("", text)
        text = self.cwd_pattern.sub("", text)

        print("Text after clan: ", text)
        parsed_text = []
        last_end = 0

        for match in self.escape_sequence_pattern.finditer(text):
            if match.start() > last_end:
                parsed_text.append(
                    (text[last_end : match.start()], self.get_current_style())
                )
            self.process_escape_sequence(match.group())
            last_end = match.end()

        if last_end < len(text):
            parsed_text.append((text[last_end:], self.get_current_style()))

        return parsed_text

    def process_title_and_cwd(self, text: str) -> None:
        # Process terminal title
        title_match = self.title_pattern.search(text)
        if title_match:
            self.terminal_title = title_match.group(1)

        # Process current working directory
        cwd_match = self.cwd_pattern.search(text)
        if cwd_match:
            self.current_working_directory = cwd_match.group(1)

    def get_terminal_title(self) -> str:
        return self.terminal_title

    def get_current_working_directory(self) -> str:
        return self.current_working_directory

    def process_escape_sequence(self, sequence: str) -> None:
        if sequence.startswith("\x1b["):
            if sequence[-1] == "m":
                self.process_sgr_params(
                    self.sgr_pattern.match(sequence).group(1).split(";")
                )
            elif sequence[-1] in "ABCDEFGHJ":
                params, command = self.cursor_pattern.match(sequence).groups()
                self.process_cursor_command(params.split(";"), command)

    def process_sgr_params(self, params: List[str]) -> None:
        i = 0
        while i < len(params):
            param = params[i]
            if param in ("38", "48"):
                i = self.process_color_param(params, i)
            else:
                self.process_sgr_param(int(param))
            i += 1

    def process_color_param(self, params: List[str], i: int) -> int:
        if i + 1 < len(params):
            if params[i + 1] == "5" and i + 2 < len(params):
                color = self.color_256[int(params[i + 2])]
                setattr(
                    self,
                    f"{'foreground' if params[i] == '38' else 'background'}_color",
                    color,
                )
                return i + 2
            elif params[i + 1] == "2" and i + 4 < len(params):
                color = np.array(list(map(int, params[i + 2 : i + 5])), dtype=np.uint8)
                setattr(
                    self,
                    f"{'foreground' if params[i] == '38' else 'background'}_color",
                    color,
                )
                return i + 4
        return i

    @lru_cache(maxsize=1024)
    def get_ansi_color(self, color_code: int, bright: bool = False) -> np.ndarray:
        return (
            self.bright_ansi_colors[color_code]
            if bright
            else self.ansi_colors[color_code]
        )

    def process_sgr_param(self, param: int) -> None:
        if param == 0:
            self.reset_attributes()
        elif param == 1:
            self.bold = True
        elif param == 3:
            self.italic = True
        elif param == 4:
            self.underline = True
        elif 30 <= param <= 37:
            self.foreground_color = self.get_ansi_color(param - 30)
        elif 40 <= param <= 47:
            self.background_color = self.get_ansi_color(param - 40)
        elif 90 <= param <= 97:
            self.foreground_color = self.get_ansi_color(param - 90, bright=True)
        elif 100 <= param <= 107:
            self.background_color = self.get_ansi_color(param - 100, bright=True)

    def get_current_style(self) -> Dict[str, Union[bool, np.ndarray]]:
        return {
            "foreground": self.foreground_color,
            "background": self.background_color,
            "bold": self.bold,
            "italic": self.italic,
            "underline": self.underline,
        }

    def process_cursor_command(self, params: List[str], command: str) -> None:
        n = int(params[0]) if params and params[0] else 1
        if command == "A":
            self.cursor_y = max(0, self.cursor_y - n)
        elif command == "B":
            self.cursor_y += n
        elif command == "C":
            self.cursor_x += n
        elif command == "D":
            self.cursor_x = max(0, self.cursor_x - n)
        elif command == "E":
            self.cursor_y += n
            self.cursor_x = 0
        elif command == "F":
            self.cursor_y = max(0, self.cursor_y - n)
            self.cursor_x = 0
        elif command == "G":
            self.cursor_x = max(0, n - 1)
        elif command == "H":
            self.cursor_y = int(params[0]) - 1 if len(params) > 0 else 0
            self.cursor_x = int(params[1]) - 1 if len(params) > 1 else 0

    def clear_caches(self):
        """Clear all LRU caches in case of theme changes."""
        self._compute_ansi_colors.cache_clear()
        self._compute_bright_ansi_colors.cache_clear()
        self._generate_256_color_palette.cache_clear()
        self.get_ansi_color.cache_clear()
