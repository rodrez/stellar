from tabulate import tabulate
import toml

from stellar.components.ansi import ANSI_COLORS


class Theme:
    def __init__(self, theme_file="stellar/themes/tokyonight.toml"):
        self.theme_file = theme_file
        self.colors = self.load_theme()

    def load_theme(self):
        try:
            with open(self.theme_file, "r") as f:
                theme_data = toml.load(f)
            return theme_data.get("colors", {})
        except FileNotFoundError:
            print(f"Theme file not found: {self.theme_file}")
            return {}
        except toml.TomlDecodeError:
            print(f"Error parsing theme file: {self.theme_file}")
            return {}

    def get_color(self, category, color_name: ANSI_COLORS):
        return self.colors.get(category, {}).get(
            color_name.value, "#FFFFFF"
        )  # Default to white if color not found

    def get_primary_bg(self):
        return self.get_color("primary", ANSI_COLORS.BACKGROUND)

    def get_primary_fg(self):
        return self.get_color("primary", ANSI_COLORS.FOREGROUND)

    def get_normal_color(self, color_name: ANSI_COLORS):
        return self.get_color("normal", color_name)

    def get_bright_color(self, color_name: ANSI_COLORS):
        return self.get_color("bright", color_name)

    def get_indexed_color(self, index):
        for color in self.colors.get("indexed_colors", []):
            if color.get("index") == index:
                return color.get("color", "#FFFFFF")
        return "#FFFFFF"  # Default to white if index not found

    def hex_to_rgb(self, hex_color):
        """Converts hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def rgb_to_ansi(self, r, g, b):
        """Converts RGB color to ANSI escape code for terminal."""
        return f"\033[48;2;{r};{g};{b}m"  # Background color escape code

    def reset_ansi(self):
        """Resets ANSI escape codes."""
        return "\033[0m"

    def print_theme_table(self):
        headers = ["Color Name", "Normal Color (Hex)", "Bright Color (Hex)"]
        table = []

        # Collect all normal and bright colors
        normal_colors = self.colors.get("normal", {})
        bright_colors = self.colors.get("bright", {})

        # Prepare the table with normal and bright colors side by side
        for color_name in set(normal_colors.keys()).union(bright_colors.keys()):
            normal_color_value = normal_colors.get(color_name, "#FFFFFF")
            bright_color_value = bright_colors.get(color_name, "#FFFFFF")

            # Convert colors to ANSI escape sequences
            r_normal, g_normal, b_normal = self.hex_to_rgb(normal_color_value)
            r_bright, g_bright, b_bright = self.hex_to_rgb(bright_color_value)

            ansi_normal = self.rgb_to_ansi(r_normal, g_normal, b_normal)
            ansi_bright = self.rgb_to_ansi(r_bright, g_bright, b_bright)
            reset_code = self.reset_ansi()

            # Add color blocks in the table
            colored_normal = f"{ansi_normal}  {normal_color_value}  {reset_code}"
            colored_bright = f"{ansi_bright}  {bright_color_value}  {reset_code}"

            table.append([color_name, colored_normal, colored_bright])

        # Print the table with aligned normal and bright colors
        print(tabulate(table, headers, tablefmt="grid"))


# Example usage
if __name__ == "__main__":
    theme = Theme("stellar/themes/tokyonight-moon.toml")
    theme.print_theme_table()
