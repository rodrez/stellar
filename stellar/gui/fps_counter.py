from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont


class FPSCounter(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame_count = 0
        self.fps = 0
        self.last_time = 0

        # Set up the appearance
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            color: white;
            border-radius: 5px;
            padding: 2px;
        """)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        # Set up the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fps)
        self.timer.start(1000)  # Update every second

    def update_fps(self):
        self.fps = self.frame_count
        self.setText(f"FPS: {self.fps}")
        self.frame_count = 0

    def increment_frame(self):
        self.frame_count += 1
