from stellar.settings.config import config
import time
import os
import subprocess
import getpass
from stellar.plugins.manager import PluginManager


class Prompt:
    """
    The Prompt class generates the command line prompt for the terminal emulator.
    It handles formatting the prompt string, applying theme colors, and retrieving
    system information such as the current directory and Git status.
    """

    def __init__(self, plugin_manager: PluginManager):
        """
        Initialize the Prompt instance.

        Args:
            plugin_manager (PluginManager): The plugin manager responsible for managing
            plugins and their interaction with the prompt.
        """
        self.time_format = config.prompt_time_format
        self.prompt_format = config.prompt_format
        self.prompt_string = []
        self.plugin_manager = plugin_manager
        self.theme = config.theme  # Load the theme from config
        self.update()

    def update(self):
        """
        Update the prompt string by formatting it with the latest values.
        """
        self.prompt_string = self.format_prompt()

    def get_prompt(self) -> list[tuple[str, str]]:
        """
        Get the current prompt string.

        Returns:
            str: The formatted prompt string.
        """
        self.update()
        return self.prompt_string

    def get_length(self) -> int:
        """
        Get the length of the current prompt string.

        Returns:
            int: The length of the prompt string.
        """
        return len(self.prompt_string)

    def get_time_format(self) -> str:
        """
        Get the time format used in the prompt.

        Returns:
            str: The time format string.
        """
        return self.time_format

    def format_prompt(self) -> list[tuple[str, str]]:
        """
        Format the prompt as a list of text segments and their associated colors.

        Returns:
            list[tuple[str, str]]: A list of tuples where each tuple contains
            a string and its associated color.
        """
        # Get colors from the theme
        arrow_color = self.theme.get_bright_color("blue")
        dir_color = self.theme.get_bright_color("green")
        git_label_color = self.theme.get_bright_color("blue")
        git_branch_color = self.theme.get_bright_color("red")
        status_color = self.get_git_status_color()  # Dynamic based on git status

        # Get Git status symbol
        git_status_symbol = self.get_git_status_symbol()

        # Return a list of (text, color) tuples
        return [
            ("➜ ", arrow_color),
            (self.get_shortened_dir() + " ", dir_color),
            ("git:", git_label_color),
            ("(", git_label_color),
            (self.get_git_branch(), git_branch_color),
            (") ", git_label_color),
            (git_status_symbol, status_color),
            (" ", ""),  # Adds some space between prompt and input
        ]

    def get_time(self) -> str:
        """
        Get the current time formatted according to the prompt's time format.

        Returns:
            str: The formatted current time string.
        """
        return time.strftime(self.time_format)

    def get_username(self) -> str:
        """
        Get the current system username.

        Returns:
            str: The username of the current user.
        """
        return getpass.getuser()

    def get_current_dir(self) -> str:
        """
        Get the full path of the current working directory.

        Returns:
            str: The absolute path of the current directory.
        """
        return os.getcwd()

    def get_shortened_dir(self) -> str:
        """
        Get the current directory path, shortened by replacing the home directory with "~"
        and using the first letter of directory names except for the last one.

        Returns:
            str: The shortened directory path.
        """
        home_dir = os.path.expanduser("~")
        current_dir = os.getcwd()

        # Replace the home directory with "~"
        if current_dir.startswith(home_dir):
            current_dir = current_dir.replace(home_dir, "~")

        # Shorten the path
        shortened_path = "/".join(
            [
                d[0] if i != len(current_dir.split("/")) - 1 else d
                for i, d in enumerate(current_dir.split("/"))
            ]
        )
        return shortened_path

    def get_git_branch(self) -> str:
        """
        Get the current Git branch name if in a Git repository.

        Returns:
            str: The name of the current Git branch, or an empty string if not in a Git repo.
        """
        try:
            branch = (
                subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
            return branch if branch else ""
        except subprocess.CalledProcessError:
            return ""

    def get_git_status_symbol(self) -> str:
        """
        Get the Git status symbol based on whether there are changes in the repository.
        Returns "✔" if no changes and "✗" if there are changes.

        Returns:
            str: "✔" if there are no changes, "✗" if there are changes.
        """
        try:
            subprocess.check_call(
                ["git", "diff", "--quiet", "--ignore-submodules"],
                stderr=subprocess.DEVNULL,
            )
            # No changes, return green ✔ symbol
            return "✔"
        except subprocess.CalledProcessError:
            # There are changes, return yellow ✗ symbol
            return "✗"

    def get_git_status_color(self) -> str:
        """
        Get the Git status color based on whether there are changes in the repository.
        Returns green if no changes and yellow if there are changes.

        Returns:
            str: The ANSI color code for green if no changes, or yellow if there are changes.
        """
        try:
            subprocess.check_call(
                ["git", "diff", "--quiet", "--ignore-submodules"],
                stderr=subprocess.DEVNULL,
            )
            # No changes, return green
            return self.theme.get_bright_color("green")
        except subprocess.CalledProcessError:
            # There are changes, return yellow
            return self.theme.get_bright_color("yellow")
