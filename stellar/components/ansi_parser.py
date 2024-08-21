import re
from stellar.components.ansi import ANSI_COLORS
from stellar.settings.config import config


class ANSIParser:
    def __init__(self):
        self.theme = config.theme
        self.reset_attributes()
        self.escape_sequence_pattern = re.compile(
            r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|[\u0080-\u009F]"
        )
        self.cursor_x = 0
        self.cursor_y = 0

    def reset_attributes(self):
        self.foreground_color = self.theme.hex_to_rgb(self.theme.get_primary_fg())
        self.background_color = self.theme.hex_to_rgb(self.theme.get_primary_bg())
        self.bold = False
        self.italic = False
        self.underline = False

    def parse(self, text):
        parsed_text = []
        last_end = 0

        for match in self.escape_sequence_pattern.finditer(text):
            # Add any text before the escape sequence
            if match.start() > last_end:
                parsed_text.append(
                    (text[last_end : match.start()], self.get_current_style())
                )

            # Process the escape sequence
            self.process_escape_sequence(match.group())
            last_end = match.end()

        # Add any remaining text after the last escape sequence
        if last_end < len(text):
            parsed_text.append((text[last_end:], self.get_current_style()))

        return parsed_text

    def process_escape_sequence(self, sequence):
        if sequence.startswith("\x1b[") and sequence[-1] in "ABCDEFGHJKSTfm":
            params = sequence[2:-1].split(";")
            command = sequence[-1]

            if command == "m":
                self.process_sgr_params(params)
            elif command in "ABCD":
                self.process_cursor_movement(params, command)
            elif command in "EF":
                self.process_line_movement(params, command)
            elif command == "H":
                self.process_cursor_position(params)
            elif command == "J":
                self.process_erase_in_display(params)
            elif command == "K":
                self.process_erase_in_line(params)
            elif command == "S":
                self.process_scroll_up(params)
            elif command == "T":
                self.process_scroll_down(params)
            elif command == "f":
                self.process_cursor_position(params)

    def process_sgr_params(self, params):
        i = 0
        while i < len(params):
            param = params[i]
            if param == "38" or param == "48":
                if i + 1 < len(params):
                    if params[i + 1] == "5":  # 256-color mode
                        if i + 2 < len(params):
                            color = int(params[i + 2])
                            if param == "38":
                                self.foreground_color = self.get_256_color(color)
                            else:
                                self.background_color = self.get_256_color(color)
                            i += 3
                            continue
                    elif params[i + 1] == "2":  # 24-bit color mode
                        if i + 4 < len(params):
                            r, g, b = map(int, params[i + 2 : i + 5])
                            if param == "38":
                                self.foreground_color = (r, g, b)
                            else:
                                self.background_color = (r, g, b)
                            i += 5
                            continue
            try:
                self.process_sgr_param(int(param))
            except ValueError:
                print(f"Warning: Invalid SGR parameter: {param}")
            i += 1

    def process_sgr_param(self, param):
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
        else:
            print(f"Warning: Unknown SGR parameter: {param}")

    def get_256_color(self, color):
        # Basic 256-color palette implementation
        if color < 16:
            return self.get_ansi_color(color % 8, bright=color > 7)
        elif 16 <= color < 232:
            color -= 16
            return (
                ((color // 36) * 51),
                (((color % 36) // 6) * 51),
                ((color % 6) * 51),
            )
        else:
            gray = (color - 232) * 10 + 8
            return (gray, gray, gray)

    def get_ansi_color(self, color_code, bright=False):
        AC = ANSI_COLORS
        color_map = {
            0: AC.BLACK,
            1: AC.RED,
            2: AC.GREEN,
            3: AC.YELLOW,
            4: AC.BLUE,
            5: AC.MAGENTA,
            6: AC.CYAN,
            7: AC.WHITE,
        }
        color_name = color_map[color_code]
        if bright:
            return self.theme.hex_to_rgb(self.theme.get_bright_color(color_name))
        return self.theme.hex_to_rgb(self.theme.get_normal_color(color_name))

    def get_current_style(self):
        return {
            "foreground": self.foreground_color,
            "background": self.background_color,
            "bold": self.bold,
            "italic": self.italic,
            "underline": self.underline,
        }

    def process_cursor_movement(self, params, command):
        n = int(params[0]) if params and params[0] else 1
        if command == "A":
            self.cursor_y = max(0, self.cursor_y - n)
        elif command == "B":
            self.cursor_y += n
        elif command == "C":
            self.cursor_x += n
        elif command == "D":
            self.cursor_x = max(0, self.cursor_x - n)

    def process_line_movement(self, params, command):
        n = int(params[0]) if params and params[0] else 1
        if command == "E":
            self.cursor_y += n
            self.cursor_x = 0
        elif command == "F":
            self.cursor_y = max(0, self.cursor_y - n)
            self.cursor_x = 0

    def process_cursor_position(self, params):
        if len(params) == 2:
            self.cursor_y = int(params[0]) - 1
            self.cursor_x = int(params[1]) - 1
        else:
            self.cursor_x = 0
            self.cursor_y = 0

    def process_erase_in_display(self, params):
        # This method would need to interact with the terminal buffer
        # For now, we'll just pass and implement the logic in the TerminalEmulator class
        pass

    def process_erase_in_line(self, params):
        # This method would need to interact with the terminal buffer
        # For now, we'll just pass and implement the logic in the TerminalEmulator class
        pass

    def process_scroll_up(self, params):
        # This method would need to interact with the terminal buffer
        # For now, we'll just pass and implement the logic in the TerminalEmulator class
        pass

    def process_scroll_down(self, params):
        # This method would need to interact with the terminal buffer
        # For now, we'll just pass and implement the logic in the TerminalEmulator class
        pass
