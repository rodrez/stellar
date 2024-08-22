import os
import pty
import select
import subprocess
import sys
import fcntl
import threading
import struct
import termios
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QFontDatabase, QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QTimer, QRect
from stellar.components.ansi_parser import ANSIParser
from stellar.settings.config import config
import locale

locale.setlocale(locale.LC_ALL, "")


class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.terminal = TerminalEmulator(80, 24)  # Initial size, will be adjusted
        self.loadNerdFont()
        self.char_width = self.fontMetrics().width(" ")
        self.char_height = self.fontMetrics().height()
        self.setFocusPolicy(Qt.StrongFocus)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS

    def loadNerdFont(self):
        nerd_font_path = config.font_path

        if not os.path.exists(nerd_font_path):
            print(f"Error: Nerd Font file not found at {nerd_font_path}")
            self.font = QFont("Monospace", 18)
        else:
            font_id = QFontDatabase.addApplicationFont(nerd_font_path)
            if font_id == -1:
                print("Error: Failed to load Nerd Font")
                self.font = QFont("Monospace", 18)
            else:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                self.font = QFont(font_family, config.font_size)

        self.font.setStyleStrategy(QFont.PreferAntialias)
        self.setFont(self.font)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        bg_color = QColor(
            *self.terminal.ansi_parser.theme.hex_to_rgb(
                self.terminal.ansi_parser.theme.get_primary_bg()
            )
        )
        painter.fillRect(event.rect(), bg_color)

        visible_buffer = (
            self.terminal.scrollback_buffer[-self.terminal.scroll_position :]
            + self.terminal.buffer
        )
        visible_buffer = visible_buffer[-self.terminal.height :]

        for y, line in enumerate(visible_buffer):
            for x, (char, style) in enumerate(line):
                fg_color = QColor(*style["foreground"])
                bg_color = QColor(*style["background"])
                painter.fillRect(
                    QRect(
                        x * self.char_width,
                        y * self.char_height,
                        self.char_width,
                        self.char_height,
                    ),
                    bg_color,
                )
                painter.setPen(QPen(fg_color))
                painter.drawText(
                    x * self.char_width,
                    (y + 1) * self.char_height - painter.fontMetrics().descent(),
                    char,
                )

        if self.terminal.scroll_position == 0:
            cursor_x = self.terminal.cursor_x * self.char_width
            cursor_y = self.terminal.cursor_y * self.char_height
            painter.fillRect(QRect(cursor_x, cursor_y, 2, self.char_height), Qt.red)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_L and event.modifiers() == Qt.ControlModifier:
            self.clear_screen()
        elif event.key() == Qt.Key_Return:
            self.terminal.send_input("\n")
        elif event.key() == Qt.Key_Backspace:
            self.terminal.send_input("\b")
        else:
            text = event.text()
            if text:
                self.terminal.send_input(text)
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:  # Scroll up
            self.terminal.scroll_position = min(
                self.terminal.scroll_position + 1, len(self.terminal.scrollback_buffer)
            )
        elif delta < 0:  # Scroll down
            self.terminal.scroll_position = max(self.terminal.scroll_position - 1, 0)
        self.update()

    def resizeEvent(self, event):
        new_cols = self.width() // self.char_width
        new_rows = self.height() // self.char_height
        self.terminal.resize(new_cols, new_rows)
        super().resizeEvent(event)

    def clear_screen(self):
        self.terminal.clear_screen()
        self.update()


class TerminalEmulator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buffer = []
        self.scrollback_buffer = []
        self.scrollback_lines = 1000
        self.scroll_position = 0
        self.cursor_x = 0
        self.cursor_y = 0
        self.ansi_parser = ANSIParser()
        self.master_fd, self.slave_fd = pty.openpty()
        self.process = subprocess.Popen(
            ["/bin/bash"],
            preexec_fn=os.setsid,
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            universal_newlines=True,
        )
        self.output_thread = threading.Thread(target=self.read_output, daemon=True)
        self.output_thread.start()
        self.update_pty_size(width, height)

    def read_output(self):
        while True:
            r, _, _ = select.select([self.master_fd], [], [])
            if r:
                try:
                    data = os.read(self.master_fd, 1024).decode(
                        "utf-8", errors="replace"
                    )
                    self.process_output(data)
                except OSError:
                    break

    def process_output(self, data):
        parsed_data = self.ansi_parser.parse(data)
        for text, style in parsed_data:
            for char in text:
                if char == "\n":
                    self.new_line()
                elif char == "\r":
                    self.cursor_x = 0
                elif char == "\b":
                    self.backspace()
                elif char == "\x1b":  # ESC character
                    if text.startswith("\x1b[2J"):  # Clear screen command
                        self.clear_screen()
                    elif text.startswith("\x1b[H"):  # Home cursor command
                        self.cursor_x = 0
                        self.cursor_y = 0
                else:
                    self.put_char(char, style)

    def new_line(self):
        if self.cursor_y == self.height - 1:
            self.scroll_up()
        else:
            self.cursor_y += 1
        self.cursor_x = 0

    def backspace(self):
        if self.cursor_x > 0:
            self.cursor_x -= 1
            self.buffer[self.cursor_y][self.cursor_x] = (
                " ",
                self.ansi_parser.get_current_style(),
            )

    def put_char(self, char, style):
        if self.cursor_x >= self.width:
            self.new_line()

        while self.cursor_y >= len(self.buffer):
            self.buffer.append(
                [(" ", self.ansi_parser.get_current_style()) for _ in range(self.width)]
            )

        while self.cursor_x >= len(self.buffer[self.cursor_y]):
            self.buffer[self.cursor_y].append(
                (" ", self.ansi_parser.get_current_style())
            )

        self.buffer[self.cursor_y][self.cursor_x] = (char, style)
        self.cursor_x += 1

    def scroll_up(self):
        if self.buffer:
            self.scrollback_buffer.append(self.buffer.pop(0))
            if len(self.scrollback_buffer) > self.scrollback_lines:
                self.scrollback_buffer.pop(0)
            self.buffer.append(
                [(" ", self.ansi_parser.get_current_style()) for _ in range(self.width)]
            )

    def send_input(self, char):
        os.write(self.master_fd, char.encode("utf-8"))

    def resize(self, new_width, new_height):
        old_buffer = self.buffer
        self.width = new_width
        self.height = new_height
        self.buffer = []

        for line in old_buffer:
            new_line = line[:new_width]
            while len(new_line) < new_width:
                new_line.append((" ", self.ansi_parser.get_current_style()))
            self.buffer.append(new_line)

        while len(self.buffer) < new_height:
            self.buffer.append(
                [(" ", self.ansi_parser.get_current_style()) for _ in range(new_width)]
            )

        self.cursor_x = min(self.cursor_x, new_width - 1)
        self.cursor_y = min(self.cursor_y, new_height - 1)

        self.update_pty_size(new_width, new_height)

    def update_pty_size(self, width, height):
        winsize = struct.pack("HHHH", height, width, 0, 0)
        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)

    def clear_screen(self):
        self.buffer = [
            [(" ", self.ansi_parser.get_current_style()) for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_position = 0
        self.scrollback_buffer = []


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Terminal Emulator")
        self.terminal_widget = TerminalWidget(self)
        self.setCentralWidget(self.terminal_widget)
        self.resize(800, 600)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
