from abc import ABC, abstractmethod


class WindowInterface(ABC):
    @abstractmethod
    def create_window(self, title: str, width: int, height: int):
        """Creates a window with the given title and dimensions"""
        pass

    @abstractmethod
    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, color: str):
        """Draw a rectangle on the window"""

    @abstractmethod
    def handle_events(self):
        """Handles windows events (eg. rezing, closing, etc)"""
        pass

    @abstractmethod
    def run(self):
        "Starts the window event loop"
        pass
