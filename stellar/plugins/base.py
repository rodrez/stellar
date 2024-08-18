from abc import ABC, abstractmethod


class StellarPlugin(ABC):
    @abstractmethod
    def initialize(self, emulator):
        """Initialize the plugin with a reference to the emulator."""
        pass

    @abstractmethod
    def on_input(self, key):
        """Handle input events."""
        pass

    @abstractmethod
    def on_render(self):
        """Perform actions before or after rendering."""
        pass

    @abstractmethod
    def cleanup(self):
        """Perform cleanup actions when the plugin is disabled or unloaded."""
        pass
