from enum import Enum

class Cursor(Enum):
    HOME = 'ESC[H'
    TO_POSITION = "ESC[{line};{col}H]"
    MOVE_UP = 'ESC[{num}A'
    MOVE_DOWN= 'ESC[{num}B'
    MOVE_RIGHT= 'ESC[{num}C'
    MOVE_LEFT = 'ESC[{num}D'
    # TODO: Complete cursor

class Graphics(Enum):
    RESET = "ESC[0m"
    BOLD = "ESC[1m"
    DIM = "ESC[2m"
    ITALIC = "ESC[3m"
    UNDERLINE= "ESC[4m"
    BLINKING= "ESC[5m"
    INVERSE= "ESC[6m"
    HIDDEN= "ESC[7m"
    STRIKE= "ESC[8m"

class ForegroundColors(Enum):
    BLACK = 30
    RED  = 31
    GREEN = 32
    YELLOW  = 33
    BLUE  = 34
    MAGENTA = 35
    CYAN  = 36
    WHITE  = 37
    DEFAULT  = 38
    RESET  = 39

class BackgroundColors(Enum):
    BLACK = 40
    RED  = 41
    GREEN = 42
    YELLOW  = 43
    BLUE  = 44
    MAGENTA = 45
    CYAN  = 46
    WHITE  = 47
    DEFAULT  = 48
    RESET  = 49


FG = ForegroundColors
BG = BackgroundColors

class ANSI_Parser:

    def parse_cursor(self, cursor_type: Cursor, num: int | None = 0, line: int | None = 0, col: int | None = 0) -> str:
        if cursor_type == Cursor.TO_POSITION:
            return cursor_type.value.format(line=line, col=col)
        return cursor_type.value.format(num=num)
    
    def parse_color(
        self,
        fore: FG = FG.DEFAULT,
        back: FG = BG.DEFAULT,
    ):
        # Set style to bold, red foreground
        # \x1b[1;32mHello
        # \x1b[2;37;41mHello
        return f"\x1b[2;{fore.value};{back.value}m"

if __name__ == "__main__":
    ansi_parser = ANSI_Parser()
    cursor_parser = ansi_parser.parse_cursor
    color_parser = ansi_parser.parse_color

    position = cursor_parser(cursor_type=Cursor.TO_POSITION, line=2, col=2)
    down = cursor_parser(cursor_type=Cursor.MOVE_DOWN, num=8)

    red_on_white = color_parser(FG.RED, BG.WHITE)
    reset = color_parser(FG.RESET, BG.RESET)

    print("------------")
    print(f"Position: {red_on_white} {position}{reset}")
    print(f"Down: {down}")
    print("------------")
    
