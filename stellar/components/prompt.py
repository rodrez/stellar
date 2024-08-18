from stellar.setings.config import Config
import time
import os
import subprocess
import getpass
from stellar.plugins.manager import PluginManager

config = Config()


class Prompt:
    def __init__(self, plugin_manager: PluginManager):
        self.time_format = config.prompt_time_format
        self.prompt_format = config.prompt_format
        self.prompt_string = ""
        self.plugin_manager = plugin_manager
        self.update()

    def update(self):
        self.prompt_string = self.format_prompt()

    def get_prompt(self):
        self.update()
        return self.prompt_string

    def get_length(self):
        return len(self.prompt_string)

    def get_time_format(self):
        return self.time_format

    def format_prompt(self) -> str:
        formatted_prompt = self.prompt_format.format(
            time=self.get_time(),
            username=self.get_username(),
            current_dir=self.get_current_dir(),
            git_branch=self.get_git_branch(),
        )
        return formatted_prompt

    def get_time(self):
        return time.strftime(self.time_format)

    def get_username(self):
        return getpass.getuser()

    def get_current_dir(self):
        return os.path.basename(os.getcwd())

    def get_git_branch(self):
        try:
            branch = (
                subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
            return f"({branch})" if branch else ""
        except subprocess.CalledProcessError:
            return ""
