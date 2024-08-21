from abc import ABC, abstractmethod


class RendererInterface(ABC):
    @abstractmethod
    def initialize(self, width: int, height: int) -> None:
        """Initialize the renderer with given dimensions."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the entire screen."""
        pass

    @abstractmethod
    def draw_char(
        self,
        x: int,
        y: int,
        char: str,
        fg_color: tuple[int, int, int],
        bg_color: tuple[int, int, int],
    ) -> None:
        """Draw a single character at the specified position with given colors."""
        pass

    @abstractmethod
    def draw_string(
        self,
        x: int,
        y: int,
        string: str,
        fg_color: tuple[int, int, int],
        bg_color: tuple[int, int, int],
    ) -> None:
        """Draw a string starting at the specified position with given colors."""
        pass

    @abstractmethod
    def set_cursor(self, x: int, y: int) -> None:
        """Set the cursor position."""
        pass

    @abstractmethod
    def show_cursor(self) -> None:
        """Show the cursor."""
        pass

    @abstractmethod
    def hide_cursor(self) -> None:
        """Hide the cursor."""
        pass

    @abstractmethod
    def refresh(self) -> None:
        """Refresh the screen to show recent changes."""
        pass

    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        """Get the current size of the terminal (width, height)."""
        pass
