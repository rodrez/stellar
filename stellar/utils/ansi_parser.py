from typing import Any
from stellar.settings.themes import Theme
import re


class ANSIParser:
    def __init__(self, theme: Theme):
        self.theme = theme
        self.default_fg = theme.hex_to_rgb(theme.get_primary_fg())
        self.default_bg = theme.hex_to_rgb(theme.get_primary_bg())
        self.current_fg = self.default_fg
        self.current_bg = self.default_bg
        self.bold = False
        self.italic = False
        self.underline = False

        # ANSI color codes to theme colors
        self.color_map = {
            0: theme.hex_to_rgb(theme.get_normal_color("black")),
            1: theme.hex_to_rgb(theme.get_normal_color("red")),
            2: theme.hex_to_rgb(theme.get_normal_color("green")),
            3: theme.hex_to_rgb(theme.get_normal_color("yellow")),
            4: theme.hex_to_rgb(theme.get_normal_color("blue")),
            5: theme.hex_to_rgb(theme.get_normal_color("magenta")),
            6: theme.hex_to_rgb(theme.get_normal_color("cyan")),
            7: theme.hex_to_rgb(theme.get_normal_color("white")),
        }

        self.bright_color_map = {
            0: theme.hex_to_rgb(theme.get_bright_color("black")),
            1: theme.hex_to_rgb(theme.get_bright_color("red")),
            2: theme.hex_to_rgb(theme.get_bright_color("green")),
            3: theme.hex_to_rgb(theme.get_bright_color("yellow")),
            4: theme.hex_to_rgb(theme.get_bright_color("blue")),
            5: theme.hex_to_rgb(theme.get_bright_color("magenta")),
            6: theme.hex_to_rgb(theme.get_bright_color("cyan")),
            7: theme.hex_to_rgb(theme.get_bright_color("white")),
        }

    def parse(self, text: str) -> list[dict[str, Any]]:
        result = []
        segments = re.split("(\x1b\\[[0-9;?]*[a-zA-Z])", text)

        for segment in segments:
            if segment.startswith("\x1b["):
                self._handle_escape_sequence(segment[2:-1])
            else:
                for char in segment:
                    result.append(
                        {
                            "char": char,
                            "fg": self.current_fg,
                            "bg": self.current_bg,
                            "bold": self.bold,
                            "italic": self.italic,
                            "underline": self.underline,
                        }
                    )

        return result

    def _handle_escape_sequence(self, sequence: str):
        if sequence.startswith("?"):
            # Ignore special sequences like '?2004h'
            return

        codes = []
        for code in sequence.split(";"):
            try:
                codes.append(int(code))
            except ValueError:
                # Ignore codes that can't be converted to integers
                continue

        if not codes:
            self._reset_styles()
            return

        for code in codes:
            if code == 0:
                self._reset_styles()
            elif code == 1:
                self.bold = True
            elif code == 3:
                self.italic = True
            elif code == 4:
                self.underline = True
            elif 30 <= code <= 37:
                self.current_fg = self.color_map[code - 30]
            elif 40 <= code <= 47:
                self.current_bg = self.color_map[code - 40]
            elif 90 <= code <= 97:
                self.current_fg = self.bright_color_map[code - 90]
            elif 100 <= code <= 107:
                self.current_bg = self.bright_color_map[code - 100]

    def _reset_styles(self):
        self.current_fg = self.default_fg
        self.current_bg = self.default_bg
        self.bold = False
        self.italic = False
        self.underline = False
