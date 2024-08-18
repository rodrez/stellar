import time


class Cursor:
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        blink_interval: float = 0.5,
        cursor_type: str = "block",
    ):
        self.x = x
        self.y = y
        self.visible = True
        self.last_blink_time = time.time()
        self.blink_interval = blink_interval
        self.cursor_type = cursor_type

    def move(self, x: int, y: int):
        self.x = x
        self.y = y
        self.reset_blink()

    def reset_blink(self):
        self.visible = True
        self.last_blink_time = time.time()

    def update_blink(self):
        current_time = time.time()
        if current_time - self.last_blink_time > self.blink_interval:
            self.visible = not self.visible
            self.last_blink_time = current_time

    def set_blink_interval(self, interval: float):
        self.blink_interval = interval

    def set_cursor_type(self, cursor_type: str):
        self.cursor_type = cursor_type

    def is_visible(self) -> bool:
        return self.visible

    def get_cursor_type(self) -> str:
        return self.cursor_type
