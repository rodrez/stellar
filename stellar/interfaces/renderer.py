from abc import ABC, abstractmethod
from stellar.interfaces.window import WindowInterface


class RenderInterface(ABC):
    @abstractmethod
    def __init__(self, window: WindowInterface) -> None:
        pass

    @abstractmethod
    def render_frame(self):
        """Renders a single frame to the terminal"""
        pass

    @abstractmethod
    def write_char(self, char: str, x: int, y: int) -> int:
        """Write a character at the specified position"""
        pass
