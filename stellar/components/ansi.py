from enum import Enum


class GeneralCodes:
    BEL = "\x07"
    BACKSPACE = "\x08"
    TAB = "\x09"
    NEWLINE = "\x0a"
    VTAB = "\x0b"
    FORMFEED = "\x0c"
    RETURN = "\x0d"
    ESC = "\x1b"
    DEL = "\x7f"


class ANSI_COLOR:
    def __init__(self, fore: str, back: str) -> None:
        self.fore = fore
        self.back = back


class ANSI_COLORS(Enum):
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"
    BACKGROUND = "background"
    FOREGROUND = "foreground"


class Cursor(Enum):
    HOME = "ESC[H"
    TO_POSITION = "ESC[{line};{col}H]"
    MOVE_UP = "ESC[{num}A"
    MOVE_DOWN = "ESC[{num}B"
    MOVE_RIGHT = "ESC[{num}C"
    MOVE_LEFT = "ESC[{num}D"
    # TODO: Complete cursor


class Graphics(Enum):
    RESET = "ESC[0m"
    BOLD = "ESC[1m"
    DIM = "ESC[2m"
    ITALIC = "ESC[3m"
    UNDERLINE = "ESC[4m"
    BLINKING = "ESC[5m"
    INVERSE = "ESC[6m"
    HIDDEN = "ESC[7m"
    STRIKE = "ESC[8m"


class ForegroundColors(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    DEFAULT = 39
    RESET = 0


class BackgroundColors(Enum):
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47
    DEFAULT = 49
    RESET = 0


FG = ForegroundColors
BG = BackgroundColors


class ANSI_Parser:
    def parse_cursor(
        self,
        cursor_type: Cursor,
        num: int | None = 0,
        line: int | None = 0,
        col: int | None = 0,
    ) -> str:
        if cursor_type == Cursor.TO_POSITION:
            return cursor_type.value.format(line=line, col=col)
        return cursor_type.value.format(num=num)

    def parse_color_256(self, fore_id: int = 15, back_id: int = 15) -> ANSI_COLOR:
        fore_string = f"{GeneralCodes.ESC}[38;5;{fore_id}m"
        back_string = f"{GeneralCodes.ESC}[48;5;{back_id}m"
        return f"{GeneralCodes.ESC}{fore_string}{back_string}"

    def parse_color_rgb(
        self,
        fore: tuple[int, int, int] = (255, 255, 255),
        back: tuple[int, int, int] = (0, 0, 0),
    ) -> str:
        fore_string = f"{GeneralCodes.ESC}[38;2;{fore[0]};{fore[1]};{fore[2]}m"
        back_string = f"{GeneralCodes.ESC}[48;2;{back[0]};{back[1]};{back[2]}m"
        return f"{GeneralCodes.ESC}{fore_string}{back_string}"

    def parse_color(
        self,
        fore: FG = FG.DEFAULT,
        back: FG = BG.DEFAULT,
    ):
        # Set style to bold, red foreground
        # \x1b[1;32mHello
        # \x1b[2;37;41mHello
        return f"{GeneralCodes.ESC}[2;{fore.value};{back.value}m"


if __name__ == "__main__":
    ansi_parser = ANSI_Parser()
    cursor_parser = ansi_parser.parse_cursor
    color_parser = ansi_parser.parse_color

    position = cursor_parser(cursor_type=Cursor.TO_POSITION, line=2, col=2)
    down = cursor_parser(cursor_type=Cursor.MOVE_DOWN, num=8)

    red_on_white = color_parser(FG.RED, BG.WHITE)
    pink_on_beige = ansi_parser.parse_color_256(fore_id=165, back_id=188)
    black_on_white = ansi_parser.parse_color_rgb(fore=(0, 0, 0), back=(255, 255, 255))
    reset = color_parser(FG.RESET, BG.RESET)

    print("------------")
    print(f"Basic coloring: {red_on_white} {position}{reset}")
    print(f"256 Colors: {pink_on_beige} Hi, I'm 256 {reset}")
    print(f"RGB Colors: {black_on_white} Konichiwa I'm RGB {reset}")
    print("------------")
