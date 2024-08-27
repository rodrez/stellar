import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QTime, QObject, pyqtSignal

from stellar.components.ansi_parser import ANSIParser
from stellar.components.st_pty import StellarPTY
from stellar.settings.config import config
from stellar.utils.logger import StellarLogger

logger = StellarLogger("stellar-gui", log_file="stellar-gui.log")


class PTYHandler(QObject):
    output_ready = pyqtSignal(str)

    def __init__(self, stellar_pty):
        super().__init__()
        self.stellar_pty = stellar_pty
        self.stellar_pty.set_output_callback(self.handle_output)

    def handle_output(self, output):
        self.output_ready.emit(output)

    def send_input(self, input_data):
        self.stellar_pty.send_input(input_data)


class TerminalWidget(QTextEdit):
    title_changed = pyqtSignal(str)
    cwd_changed = pyqtSignal(str)

    def __init__(self, stellar_pty: StellarPTY) -> None:
        super().__init__()
        self.stellar_pty = stellar_pty
        self.setReadOnly(False)
        self.setUndoRedoEnabled(False)
        self.prompt = ""
        self.current_command = ""
        self.command_start_position = 0
        self.ansi_parser = ANSIParser()
        self.buffer_size = 0
        self.line_buffer = ""
        self.setup_ui()

        self.pty_handler = PTYHandler(self.stellar_pty)
        self.pty_handler.output_ready.connect(self.process_output)

        # Add a flag to track whether we're currently at a prompt
        self.at_prompt = False

        # Add a method to detect the end of command output
        self.output_end_timer = QTimer(self)
        self.output_end_timer.setSingleShot(True)
        self.output_end_timer.timeout.connect(self.handle_output_end)

        QTimer.singleShot(0, self.initialize_pty)

    def setup_ui(self) -> None:
        self.setStyleSheet(f"""
            background-color: {config.theme.get_default_bg()};
            color: {config.theme.get_default_fg()};
            font-family: 'FiraCode Nerd Font', 'Consolas', 'DejaVu Sans Mono', 'Courier New', monospace;
            font-size: {config.font_size}pt;
            font-weight: 600;
        """)

    def initialize_pty(self) -> None:
        try:
            self.stellar_pty.start()
        except Exception as e:
            logger.error(f"Failed to start StellarPTY: {str(e)}")

    @pyqtSlot(str)
    def process_output(self, output: str) -> None:
        try:
            # Process title and CWD changes
            self.ansi_parser.process_title_and_cwd(output)
            new_title = self.ansi_parser.get_terminal_title()
            new_cwd = self.ansi_parser.get_current_working_directory()

            if new_title:
                self.title_changed.emit(new_title)
            if new_cwd:
                self.cwd_changed.emit(new_cwd)

            # Process the entire output at once
            print("Outpt to append: ", output)
            self.append_output(output)

            self.output_end_timer.start(100)
            self.command_start_position = self.textCursor().position()

        except Exception as e:
            logger.error(f"Error in process_output: {str(e)}")

    def append_output(self, output: str) -> None:
        try:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

            # Handle buffer size limits
            new_size = self.buffer_size + len(output)
            if new_size > config.buffer_size:
                chars_to_remove = new_size - config.buffer_size
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.KeepAnchor,
                    chars_to_remove,
                )
                cursor.removeSelectedText()
                self.buffer_size = self.document().characterCount()

            cursor.movePosition(QTextCursor.MoveOperation.End)

            print("Ouput before inserting: ", output)
            # Process and insert the entire output at once
            for text, style in self.ansi_parser.parse(output):
                self.insert_styled_text(text, style)

            self.buffer_size += len(output)

            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

        except Exception as e:
            logger.error(f"Error in append_output: {str(e)}")

    def handle_output_end(self):
        # This method is called when we think the command output has ended
        self.at_prompt = True
        self.prompt = self.toPlainText().split("\n")[-1]
        self.command_start_position = self.textCursor().position()

    def insert_styled_text(self, text: str, style: dict) -> None:
        cursor = self.textCursor()
        char_format = QTextCharFormat()
        char_format.setForeground(QColor(*style["foreground"]))
        char_format.setBackground(QColor(*style["background"]))
        if style["bold"]:
            char_format.setFontWeight(QFont.Weight.Bold)
        if style["italic"]:
            char_format.setFontItalic(True)
        if style["underline"]:
            char_format.setFontUnderline(True)
        cursor.insertText(text, char_format)

    def keyPressEvent(self, event):
        if not self.at_prompt:
            # If we're not at a prompt, don't allow input
            return

        cursor = self.textCursor()
        if cursor.position() < self.command_start_position:
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

        key = event.key()
        if key == Qt.Key.Key_Return:
            self.handle_return_key()
        elif key == Qt.Key.Key_Backspace:
            if cursor.position() > self.command_start_position:
                super().keyPressEvent(event)
                self.current_command = self.toPlainText()[self.command_start_position :]
        elif key == Qt.Key.Key_Left:
            if cursor.position() > self.command_start_position:
                super().keyPressEvent(event)
        else:
            if cursor.position() >= self.command_start_position:
                super().keyPressEvent(event)
                self.current_command = self.toPlainText()[self.command_start_position :]

    def handle_return_key(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        self.current_command = self.toPlainText()[self.command_start_position :]
        self.pty_handler.send_input(self.current_command + "\n")
        self.current_command = ""
        self.at_prompt = False  # We're no longer at a prompt after sending a command


class StellarApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.fps_label)

        self.stellar_pty = StellarPTY("/bin/bash")
        self.terminal = TerminalWidget(self.stellar_pty)
        self.terminal.title_changed.connect(self.update_window_title)
        self.terminal.cwd_changed.connect(self.handle_cwd_change)
        layout.addWidget(self.terminal)

        self.setWindowTitle("Stellar Terminal Emulator")

        self.frame_count = 0
        self.last_fps_update = QTime.currentTime()
        self.fps_update_interval = 1000

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(16)

    def update_window_title(self, new_title):
        self.setWindowTitle(f"Stellar Term - {new_title}")

    def handle_cwd_change(self, new_cwd):
        # You can use the new_cwd information as needed
        # For example, update a status bar or use it for file operations
        pass

    def update_gui(self):
        self.terminal.update()
        self.frame_count += 1

        current_time = QTime.currentTime()
        if self.last_fps_update.msecsTo(current_time) > self.fps_update_interval:
            elapsed_time = self.last_fps_update.msecsTo(current_time) / 1000.0
            fps = self.frame_count / elapsed_time
            self.fps_label.setText(f"FPS: {fps:.2f}")
            self.frame_count = 0
            self.last_fps_update = current_time

    def closeEvent(self, event):
        # Ensure clean shutdown of PTY
        # self.stellar_pty.close()
        super().closeEvent(event)


def exception_hook(exctype, value, traceback):
    logger.error("Uncaught exception:", exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)


if __name__ == "__main__":
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    window = StellarApp()
    window.show()
    sys.exit(app.exec())
