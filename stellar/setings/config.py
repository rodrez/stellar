import toml
from pathlib import Path


class Config:
    def __init__(self):
        config_path = Path(__file__).parent.parent.parent / "config.toml"
        self.config = toml.load(config_path)

        # Appearance settings
        self.font_family = self.config["appearance"]["font_family"]
        self.font_size = self.config["appearance"]["font_size"]
        self.text_color = self.config["appearance"]["text_color"]
        self.bg_color = self.config["appearance"]["bg_color"]
        self.padding = self.config["appearance"]["padding"]

        # Terminal settings
        self.cols = self.config["terminal"]["cols"]
        self.rows = self.config["terminal"]["rows"]

    def reload(self):
        """Reload the configuration from the TOML file"""
        self.__init__()


config = Config()
