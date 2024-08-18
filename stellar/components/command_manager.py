import os
import shlex
import subprocess
from typing import Callable


class CommandManager:
    def __init__(self, renderer, window):
        self.renderer = renderer
        self.window = window
        self.commands: dict[str, Callable] = {
            "clear": self.clear_command,
            "echo": self.echo_command,
            "help": self.help_command,
            "cd": self.cd_command,
        }

    def execute_command(self, command_line: str):
        if not command_line.strip():
            return

        try:
            args = shlex.split(command_line)
            command = args[0].lower()

            if command in self.commands:
                self.commands[command](args[1:])
            else:
                self.execute_system_command(args)
        except Exception as e:
            self.renderer.write_output(
                f"Error executing command: {str(e)}",
                self.renderer.theme.get_normal_color("red"),
            )

    def execute_system_command(self, args: list[str]):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=10)
            self.renderer.write_output(
                result.stdout, self.renderer.theme.get_normal_color("green")
            )
            if result.stderr:
                self.renderer.write_output(
                    result.stderr, self.renderer.theme.get_normal_color("red")
                )
        except subprocess.TimeoutExpired:
            self.renderer.write_output(
                "Command timed out after 10 seconds",
                self.renderer.theme.get_normal_color("yellow"),
            )
        except FileNotFoundError:
            self.renderer.write_output(
                f"Command not found: {args[0]}",
                self.renderer.theme.get_normal_color("red"),
            )

    def clear_command(self, args: list[str]):
        self.renderer.clear_screen()

    def echo_command(self, args: list[str]):
        self.renderer.write_output(
            " ".join(args), self.renderer.theme.get_normal_color("cyan")
        )

    def help_command(self, args: list[str]):
        help_text = """
Available commands:
  clear - Clear the screen
  echo [text] - Display a line of text
  cd [directory] - Change the current directory
  help - Display this help message

You can also run system commands.
"""
        self.renderer.write_output(
            help_text, self.renderer.theme.get_normal_color("magenta")
        )

    def cd_command(self, args: list[str]):
        if not args:
            self.renderer.write_output(
                "Usage: cd <directory>", self.renderer.theme.get_normal_color("yellow")
            )
        else:
            try:
                os.chdir(args[0])
                self.renderer.write_output(
                    f"Changed directory to {os.getcwd()}",
                    self.renderer.theme.get_normal_color("green"),
                )
            except FileNotFoundError:
                self.renderer.write_output(
                    f"Directory not found: {args[0]}",
                    self.renderer.theme.get_normal_color("red"),
                )
            except PermissionError:
                self.renderer.write_output(
                    f"Permission denied: {args[0]}",
                    self.renderer.theme.get_normal_color("red"),
                )

    def add_command(self, name: str, function: Callable):
        self.commands[name.lower()] = function
