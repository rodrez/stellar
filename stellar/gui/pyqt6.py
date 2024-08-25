import sys  # Provides access to system-specific parameters and functions
import traceback  # Allows extraction and formatting of stack traces for debugging
import gc
import os
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)  # PyQt6 widgets for GUI components
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QPalette,
    QTextCharFormat,
    QTextCursor,
    QKeyEvent,
)  # PyQt6 GUI functionality for color, cursor, and key events
from PyQt6.QtCore import (
    QTime,
    Qt,
    pyqtSlot,
    QTimer,
)  # Core functionality of PyQt6 including the Qt namespace and signals/slots

from stellar.components.ansi_parser import ANSIParser
from stellar.components.st_pty import (
    StellarPTY,
)
from stellar.settings.config import config
from stellar.utils.logger import (
    StellarLogger,
)  # Importing the StellarPTY class for PTY interaction

# Set up logger with a basic configuration
logger = StellarLogger("stellar-gui", log_file="stellar-gui.log")


class TerminalWidget(QTextEdit):
    """
    TerminalWidget is a custom QTextEdit widget that interacts with the StellarPTY class to emulate a terminal.

    It handles user input and output, manages command history, and displays terminal-style text.

    Attributes:
        stellar_pty (StellarPTY): The StellarPTY instance managing the PTY process.
        prompt (str): The terminal prompt.
        current_command (str): The current user command being typed.
        command_start_position (int): Position in the text where the current command begins.
    """

    def __init__(self, stellar_pty: StellarPTY) -> None:
        """
        Initializes the TerminalWidget instance.

        Args:
            stellar_pty (StellarPTY): The PTY instance to interact with.
        """
        super().__init__()  # Call the QTextEdit constructor
        self.stellar_pty = stellar_pty
        self.stellar_pty.set_output_callback(
            self.append_output
        )  # Set the output callback for PTY data
        self.setReadOnly(False)  # Make the terminal widget writable
        self.setUndoRedoEnabled(
            False
        )  # We do not need undo/redo, seems to cause memory issues
        self.prompt = ""  # Placeholder for a terminal prompt
        self.current_command = ""  # Current user-typed command
        self.command_start_position = (
            0  # Keeps track of where the current command starts
        )
        # self.setup_ui()  # Call UI setup method

        self.ansi_parser = ANSIParser()
        self.buffer_size = 0
        QTimer.singleShot(0, self.initialize_pty)  # Initialize PTY after widget loads

    def setup_ui(self) -> None:
        """
        Configures the terminal's appearance by setting color palette and font,
        with robust font handling to prevent crashes.
        """
        # Set the background and text colors
        palette = self.palette()
        palette.setColor(
            QPalette.ColorRole.Base,
            QColor(*config.theme.hex_to_rgb(config.theme.get_default_bg())),
        )
        palette.setColor(
            QPalette.ColorRole.Text,
            QColor(*config.theme.hex_to_rgb(config.theme.get_default_fg())),
        )
        self.setPalette(palette)

        # Set up fonts with fallback mechanism
        font = QFont()
        preferred_fonts = ["Fira Code", "Consolas", "DejaVu Sans Mono", "Courier New"]

        # Try to load Fira Code if it's bundled with the application
        font_path = os.path.join(
            os.path.dirname(__file__), "fonts", "FiraCode-Regular.ttf"
        )
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                font.setFamily(font_family)
            else:
                print("Failed to load bundled Fira Code font.")

        # If bundled font failed to load, try system fonts
        if font.family() == "":
            for font_name in preferred_fonts:
                font.setFamily(font_name)
                if QFontDatabase().hasFamily(font_name):
                    break
            else:
                # If none of the preferred fonts are available, fall back to any monospace font
                font.setStyleHint(QFont.StyleHint.Monospace)

        font.setPointSize(config.font_size)
        font.setWeight(QFont.Weight.DemiBold)
        self.setFont(font)

        # Print the final font being used (for debugging)
        logger.info(f"Using font: {self.font().family()}")

    def initialize_pty(self) -> None:
        """
        Initializes the StellarPTY instance and starts the terminal session.
        If an error occurs, it logs the error and displays a message box.
        """
        try:
            logger.info("Initializing StellarPTY")  # Log initialization attempt
            self.stellar_pty.start()  # Start the PTY process
            logger.info(
                "StellarPTY initialized successfully"
            )  # Log successful initialization
            self.append_output(self.prompt)  # Display the prompt
            self.command_start_position = (
                self.textCursor().position()
            )  # Mark where the user command starts
        except Exception as e:
            logger.error(f"Failed to start StellarPTY: {str(e)}")  # Log failure message
            logger.error(traceback.format_exc())  # Log traceback of the exception
            QMessageBox.critical(
                self, "Error", f"Failed to start terminal: {str(e)}"
            )  # Show error message to the user

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles keyboard input events such as Enter, Backspace, and arrow keys.

        Args:
            event (QKeyEvent): The key press event object containing information about the key pressed.
        """
        cursor = self.textCursor()  # Get the current text cursor

        # Prevent the cursor from moving before the start of the current command
        if cursor.position() < self.command_start_position:
            cursor.movePosition(QTextCursor.MoveOperation.End)  # Move cursor to the end
            self.setTextCursor(cursor)  # Apply the cursor position change

        if event.key() == Qt.Key.Key_Return:
            self.handle_return_key()  # Handle Enter key (submit command)
        elif event.key() == Qt.Key.Key_Backspace:
            self.handle_backspace_key(event)  # Handle Backspace key
        elif event.key() == Qt.Key.Key_Left:
            self.handle_left_key(event)  # Handle Left arrow key
        else:
            if cursor.position() >= self.command_start_position:
                super().keyPressEvent(event)  # Allow other keys to be processed
                self.current_command = self.toPlainText()[
                    self.command_start_position :
                ]  # Update current command

    def handle_return_key(self) -> None:
        """
        Handles the Enter key press to send the command to the StellarPTY instance.
        """
        cursor = self.textCursor()  # Get the current text cursor
        cursor.movePosition(QTextCursor.MoveOperation.End)  # Move cursor to the end
        self.setTextCursor(cursor)  # Apply the cursor position change
        self.current_command = self.toPlainText()[
            self.command_start_position :
        ]  # Get the current command text
        logger.debug(
            f"Sending command to StellarPTY: {self.current_command}"
        )  # Log the command
        self.stellar_pty.send_input(self.current_command)  # Send the command to the PTY
        self.current_command = ""  # Reset the current command

    def handle_backspace_key(self, event: QKeyEvent) -> None:
        """
        Handles the Backspace key press, allowing deletion only within the current command.

        Args:
            event (QKeyEvent): The key press event object.
        """
        if self.textCursor().position() > self.command_start_position:
            super().keyPressEvent(
                event
            )  # Allow deletion if the cursor is within the current command
            self.current_command = self.toPlainText()[
                self.command_start_position :
            ]  # Update current command

    def handle_left_key(self, event: QKeyEvent) -> None:
        """
        Handles the Left arrow key press, allowing cursor movement only within the current command.

        Args:
            event (QKeyEvent): The key press event object.
        """
        if self.textCursor().position() > self.command_start_position:
            super().keyPressEvent(event)  # Allow movement within the current command

    @pyqtSlot(str)
    def append_output(self, output: str) -> None:
        try:
            logger.debug(f"Received output from StellarPTY: {output}")
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

            # Check if adding the new output would exceed the buffer size
            new_size = self.buffer_size + len(output)
            if new_size > config.buffer_size:
                # Calculate how many characters we need to remove
                chars_to_remove = new_size - config.buffer_size
                # Remove the excess characters from the start of the document
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.KeepAnchor,
                    chars_to_remove,
                )
                cursor.removeSelectedText()
                # Update the buffer size
                self.buffer_size = self.document().characterCount()
                logger.debug(f"Trimmed buffer. New size: {self.buffer_size}")

            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(output)
            self.buffer_size += len(output)

            if not output.endswith(self.prompt):
                cursor.insertText(self.prompt)
                self.buffer_size += len(self.prompt)

            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)
            self.command_start_position = cursor.position()

            logger.debug(f"Current buffer size: {self.buffer_size}")

        except Exception as e:
            logger.error(f"Error in append_output: {str(e)}")
            logger.error(traceback.format_exc())

    def insert_styled_text(self, text: str, style: dict) -> None:
        cursor = self.textCursor()
        char_format = QTextCharFormat()

        # Set foreground color
        fg_color = QColor(*style["foreground"])
        char_format.setForeground(fg_color)

        # Set background color
        bg_color = QColor(*style["background"])
        char_format.setBackground(bg_color)

        # Set text style
        if style["bold"]:
            char_format.setFontWeight(QFont.Weight.Bold)
        if style["italic"]:
            char_format.setFontItalic(True)
        if style["underline"]:
            char_format.setFontUnderline(True)

        cursor.insertText(text, char_format)


class StellarApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create a horizontal layout for the FPS counter
        self.top_layout = QHBoxLayout()

        # Create FPS counter label
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.top_layout.addWidget(self.fps_label)

        self.layout.addLayout(self.top_layout)

        self.stellar_pty = StellarPTY()
        self.terminal = TerminalWidget(self.stellar_pty)
        self.layout.addWidget(self.terminal)
        self.setLayout(self.layout)
        self.setWindowTitle("Stellar Terminal Emulator")

        # Set up FPS counter
        self.frame_count = 0
        self.last_fps_update = QTime.currentTime()
        self.fps_update_interval = 1000  # Update FPS every 1000 ms (1 second)

        # Start a timer to update the GUI and count frames
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(16)  # ~60 FPS (1000 ms / 60 ≈ 16.67 ms)

    def update_gui(self):
        # Update the terminal and any other GUI elements here
        self.terminal.update()

        # Increment frame count
        self.frame_count += 1

        # Update FPS counter every second
        current_time = QTime.currentTime()
        if self.last_fps_update.msecsTo(current_time) > self.fps_update_interval:
            elapsed_time = (
                self.last_fps_update.msecsTo(current_time) / 1000.0
            )  # Convert to seconds
            fps = self.frame_count / elapsed_time
            self.fps_label.setText(f"FPS: {fps:.2f}")
            self.frame_count = 0
            self.last_fps_update = current_time


def exception_hook(exctype, value, traceback):
    """
    Handles uncaught exceptions by logger the error and passing the exception to the default handler.

    Args:
        exctype: The type of the exception.
        value: The exception instance.
        traceback: The traceback object associated with the exception.
    """
    logger.error(
        "Uncaught exception:", exc_info=(exctype, value, traceback)
    )  # Log the uncaught exception
    sys.__excepthook__(
        exctype, value, traceback
    )  # Pass the exception to the default handler


if __name__ == "__main__":
    gc.set_debug(gc.DEBUG_LEAK)
    sys.excepthook = exception_hook  # Set the exception hook for uncaught exceptions
    app = QApplication(sys.argv)  # Create the QApplication instance
    window = StellarApp()  # Create the main window (TerminalApp)
    window.show()  # Display the window
    sys.exit(app.exec())  # Run the application event loop
