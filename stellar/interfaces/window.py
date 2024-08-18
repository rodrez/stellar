from abc import ABC, abstractmethod
from typing import Any
# from typing import Optional

from stellar.interfaces.typings import FontType


class WindowInterface(ABC):
    @abstractmethod
    def create_window(self, title: str, width: int, height: int):
        """Creates a window with the given title and dimensions"""
        pass

    @abstractmethod
    def root_exists(self) -> bool:
        pass

    @abstractmethod
    def create_font(self, family: str, size: int) -> Any:
        pass

    @abstractmethod
    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, color: str):
        """Draw a rectangle on the window"""

    @abstractmethod
    def draw_text(self, text: str, x: int, y: int, color: str, font: FontType):
        """Draw the text on the window at the specified position"""
        pass

    @abstractmethod
    def handle_events(self):
        """Handles windows events (eg. rezing, closing, etc)"""
        pass

    @abstractmethod
    def run(self):
        """Starts the window event loop"""
        pass

    @abstractmethod
    def clear(self):
        """Clears window content"""
        pass

    @abstractmethod
    def update(self):
        """Updates the window display"""
        pass

    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        """Returns a width, height tuple"""
        pass
