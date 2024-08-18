from abc import ABC, abstractmethod


class InputInterface(ABC):
    @abstractmethod
    def handle_input(self):
        """Handle input events and return any keystrokes"""
        pass
