import toml
from pathlib import Path

from stellar.setings.themes import Theme


class Config:
    def __init__(self):
        config_path = Path(__file__).parent.parent.parent / "config.toml"
        self.config = toml.load(config_path)

        # Load theme
        self.theme = Theme()
        self.theme.print_theme_table()

        # Appearance settings
        self.font_family = self.config["appearance"]["font_family"]
        self.font_size = self.config["appearance"]["font_size"]
        self.text_color = self.theme.get_primary_fg()

        self.bg_color = self.theme.get_primary_bg()
        self.padding = self.config["appearance"]["padding"]

        # Terminal settings
        self.cols = self.config["terminal"]["cols"]
        self.rows = self.config["terminal"]["rows"]

        # Prompt settings
        self.prompt_format = self.config["prompt"].get("format", "")
        self.prompt_time_format = self.config["prompt"]["time_format"]

        # Cursor settings
        self.cursor_blink_interval = self.config["cursor"]["blink_interval"]
        self.cursor_type = self.config["cursor"]["type"]

    def reload(self):
        """Reload the configuration from the TOML file"""
        self.__init__()

    def validate(self):
        """Validate that the values for the config make sense"""


config = Config()
