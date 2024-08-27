from tabulate import tabulate
import toml
import logging

from stellar.components.ansi import ANSI_COLORS


class Theme:
    def __init__(self, theme_file: str = "stellar/themes/tokyonight.toml"):
        """
        Initializes the Theme class by loading the theme from a .toml file.

        Args:
            theme_file (str): Path to the theme file.
        """
        self.theme_file = theme_file
        self.colors = self.load_theme()

    def load_theme(self) -> dict[str, dict]:
        """
        Loads the theme file into a dictionary containing the color mappings.

        Returns:
            dict: A dictionary containing theme color categories.
        """
        try:
            with open(self.theme_file, "r") as f:
                theme_data = toml.load(f)
            return theme_data.get("colors", {})
        except FileNotFoundError as e:
            logging.error(f"Theme file not found: {self.theme_file}")
            raise e
        except toml.TomlDecodeError as e:
            logging.error(f"Error parsing theme file: {self.theme_file}")
            raise e

    def get_color(
        self, category: str, color_name: ANSI_COLORS, fallback: str = "#FFFFFF"
    ) -> str:
        """
        Retrieves a color from the theme based on the category and ANSI color.

        Args:
            category (str): The category of the color (e.g., "primary", "normal").
            color_name (ANSI_COLORS): The ANSI color enum value.
            fallback (str): The fallback color if the color is not found. Defaults to white.

        Returns:
            str: The hex code of the requested color, or the fallback if not found.
        """
        return self.colors.get(category, {}).get(color_name.value, fallback)

    def get_default_bg(self) -> str:
        """
        Retrieves the default background color from the primary category.

        Returns:
            str: The hex code for the default background color.
        """
        return self.get_color("primary", ANSI_COLORS.BACKGROUND)

    def get_default_fg(self) -> str:
        """
        Retrieves the default foreground color from the primary category.

        Returns:
            str: The hex code for the default foreground color.
        """
        return self.get_color("primary", ANSI_COLORS.FOREGROUND)

    def get_normal_color(self, color_name: ANSI_COLORS) -> str:
        """
        Retrieves a normal color from the 'normal' category.

        Args:
            color_name (ANSI_COLORS): The ANSI color enum value.

        Returns:
            str: The hex code of the requested normal color.
        """
        return self.get_color("normal", color_name)

    def get_bright_color(self, color_name: ANSI_COLORS) -> str:
        """
        Retrieves a bright color from the 'bright' category.

        Args:
            color_name (ANSI_COLORS): The ANSI color enum value.

        Returns:
            str: The hex code of the requested bright color.
        """
        return self.get_color("bright", color_name)

    def get_indexed_color(self, index: int) -> str:
        """
        Retrieves a color from the indexed color palette.

        Args:
            index (int): The index of the color in the indexed color palette.

        Returns:
            str: The hex code of the indexed color or white if not found.
        """
        for color in self.colors.get("indexed_colors", []):
            if color.get("index") == index:
                return color.get("color", "#FFFFFF")
        return "#FFFFFF"  # Default to white if index not found

    def hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """
        Converts a hex color code to an RGB tuple.

        Args:
            hex_color (str): The hex color code (e.g., "#FFFFFF").

        Returns:
            tuple: A tuple of integers representing the RGB color (R, G, B).
        """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def rgb_color(self, hex_color: str) -> tuple[int, int, int]:
        """
        An alias for hex_to_rgb for readability.

        Args:
            hex_color (str): The hex color code.

        Returns:
            tuple: The corresponding RGB tuple.
        """
        return self.hex_to_rgb(hex_color)

    def rgb_to_ansi(self, r: int, g: int, b: int) -> str:
        """
        Converts an RGB color to an ANSI escape code.

        Args:
            r (int): Red value.
            g (int): Green value.
            b (int): Blue value.

        Returns:
            str: ANSI escape code for the given RGB color.
        """
        return f"\033[48;2;{r};{g};{b}m"  # Background color escape code

    def reset_ansi(self) -> str:
        """
        Resets the ANSI escape codes to default.

        Returns:
            str: The ANSI escape code for resetting styles.
        """
        return "\033[0m"

    def print_theme_table(self) -> None:
        """
        Prints a table displaying the normal and bright colors in the theme using ANSI color blocks.
        """
        headers = ["Color Name", "Normal Color (Hex)", "Bright Color (Hex)"]
        table = []

        normal_colors = self.colors.get("normal", {})
        bright_colors = self.colors.get("bright", {})

        for color_name in set(normal_colors.keys()).union(bright_colors.keys()):
            normal_color_value = normal_colors.get(color_name, "#FFFFFF")
            bright_color_value = bright_colors.get(color_name, "#FFFFFF")

            # Convert colors to RGB and then to ANSI
            r_normal, g_normal, b_normal = self.hex_to_rgb(normal_color_value)
            r_bright, g_bright, b_bright = self.hex_to_rgb(bright_color_value)

            ansi_normal = self.rgb_to_ansi(r_normal, g_normal, b_normal)
            ansi_bright = self.rgb_to_ansi(r_bright, g_bright, b_bright)
            reset_code = self.reset_ansi()

            colored_normal = f"{ansi_normal}  {normal_color_value}  {reset_code}"
            colored_bright = f"{ansi_bright}  {bright_color_value}  {reset_code}"

            table.append([color_name, colored_normal, colored_bright])

        print(tabulate(table, headers, tablefmt="grid"))


# Example usage
if __name__ == "__main__":
    theme = Theme()
    theme.print_theme_table()
