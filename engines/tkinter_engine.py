import tkinter as tk
from stellar.interfaces.window import WindowInterface


class TkinterWindow(WindowInterface):
    def create_window(self, title: str, width: int, height: int):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.canvas = tk.Canvas(self.root, width=width, height=height)

    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, color: str):
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    def handle_events(self):
        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        print(f"Window resized to {event.width}x{event.height}")

    def run(self):
        self.root.mainloop()
