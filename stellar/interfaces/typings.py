from typing import Literal, Optional
from dataclasses import dataclass


FontStyle = Literal["normal", "semibold", "italic", "bold"]


@dataclass
class FontType:
    family: str
    size: int
    style: Optional[FontStyle] = "normal"

    def __iter__(self):
        """Allows the FontType object to be converted to a tuple."""
        yield self.family
        yield self.size
        yield self.style

    def to_tuple(self) -> tuple[str, int, str]:
        """Return the font attributes as a tuple."""
        return (self.family, self.size, str(self.style))
