from abc import ABC, abstractmethod
from stellar.interfaces.window import WindowInterface
from typing import Tuple


class RenderInterface(ABC):
    @abstractmethod
    def __init__(self, window: WindowInterface) -> None:
        pass

    @abstractmethod
    def render_frame(self) -> None:
        """Renders a single frame to the terminal"""
        pass

    @abstractmethod
    def write_char(
        self, char: str, x: int, y: int, fg_color: str, bg_color: str
    ) -> int:
        """Write a character at the specified position with given colors"""
        pass

    @abstractmethod
    def handle_pty_output(self, output: str) -> None:
        """Handle output from the PTY"""
        pass

    @abstractmethod
    def handle_input(self, char: str) -> None:
        """Handle input from the user"""
        pass

    @abstractmethod
    def clear_screen(self) -> None:
        """Clear the entire screen"""
        pass

    @abstractmethod
    def resize(self, cols: int, rows: int) -> None:
        """Resize the terminal buffer"""
        pass

    @abstractmethod
    def get_cursor_position(self) -> Tuple[int, int]:
        """Get the current cursor position"""
        pass

    @abstractmethod
    def set_cursor_position(self, x: int, y: int) -> None:
        """Set the cursor position"""
        pass
