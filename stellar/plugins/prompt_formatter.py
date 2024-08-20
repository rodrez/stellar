from stellar.plugins.base import StellarPlugin
from stellar.settings.config import config
import time
import getpass
import os
import subprocess


class PromptFormatterPlugin(StellarPlugin):
    def __init__(self):
        self.prompt_format = config.prompt_format
        self.time_format = config.prompt_time_format
        self.emulator = None

    def initialize(self, emulator):
        self.emulator = emulator

    def on_input(self, key):
        # This plugin doesn't need to handle input
        pass

    def on_render(self):
        # This plugin doesn't need to do anything on render
        pass

    def cleanup(self):
        # No cleanup needed for this plugin
        pass

    def format_prompt(self):
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


# Priority: 10
