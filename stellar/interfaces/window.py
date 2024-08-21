# stellar/interfaces/window.py

from abc import ABC, abstractmethod
from typing import Tuple


class WindowEngineInterface(ABC):
    @abstractmethod
    def create_window(self, title: str, width: int, height: int) -> None:
        """Create a window with the given title and dimensions."""
        pass

    @abstractmethod
    def handle_events(self) -> None:
        """Handle window events."""
        pass

    @abstractmethod
    def handle_input(self) -> str:
        """Handle and return user input."""
        pass

    @abstractmethod
    def update(self) -> None:
        """Update the window display."""
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        """Check if the window is still open and active."""
        pass

    @abstractmethod
    def get_size(self) -> Tuple[int, int]:
        """Get the current size of the window."""
        pass
