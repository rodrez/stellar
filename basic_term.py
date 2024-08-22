import os
import pty
import select
import subprocess
import sys
from PyQt5.QtCore import QSocketNotifier
from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget, QLineEdit


class Terminal(QWidget):
    def __init__(self):
        super().__init__()

        # Create UI components
        self.layout = QVBoxLayout()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.input = QLineEdit()

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)
        self.setLayout(self.layout)

        # Create a PTY
        self.master_fd, self.slave_fd = pty.openpty()

        # Start a shell process in the PTY
        self.process = subprocess.Popen(
            "/bin/bash",
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            shell=True,
            preexec_fn=os.setsid,
        )

        # Monitor the master FD for output
        self.notifier = QSocketNotifier(self.master_fd, QSocketNotifier.Read)
        self.notifier.activated.connect(self.read_from_pty)

        # Connect the input line to sending commands
        self.input.returnPressed.connect(self.send_command)

    def read_from_pty(self):
        # Read output from PTY
        if select.select([self.master_fd], [], [], 0)[0]:
            output = os.read(self.master_fd, 1024).decode()
            self.output.append(output)

    def send_command(self):
        # Get the command from input and write to PTY
        command = self.input.text() + "\n"
        os.write(self.master_fd, command.encode())
        self.input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = Terminal()
    terminal.show()
    sys.exit(app.exec_())
