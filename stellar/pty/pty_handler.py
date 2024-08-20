import os
import pty
import select
import termios
import struct
import fcntl


class PTYHandler:
    """
    PTYHandler is a class that handles interactions with a pseudo-terminal (PTY).
    It provides methods to spawn a shell, read from, write to, and resize the PTY.
    """

    def __init__(self):
        """
        Initialize a PTYHandler instance.
        Attributes:
            fd (int): File descriptor for the master end of the PTY.
            pid (int): Process ID of the spawned shell.
        """
        self.fd: int | None = None
        self.pid: int | None = None

    def spawn(self, shell: str = "/bin/zsh") -> None:
        """
        Spawn a new shell process attached to a pseudo-terminal.

        Args:
            shell (str): The shell to spawn. Default is "/bin/bash".
        """
        self.pid, self.fd = pty.fork()
        if self.pid == 0:  # Child process
            os.execvp(shell, [shell])

    def read(self, max_read_bytes: int = 1024) -> bytes:
        """
        Read data from the PTY.

        Args:
            max_read_bytes (int): Maximum number of bytes to read. Default is 1024.

        Returns:
            bytes: Data read from the PTY. If no data is available, an empty byte string is returned.
        """
        if not self.fd:
            return b""
        r, _, _ = select.select([self.fd], [], [], 0)
        if not r:
            return b""
        return os.read(self.fd, max_read_bytes)

    def write(self, data: str) -> None:
        """
        Write data to the PTY.

        Args:
            data (str): The data to write to the PTY.
        """
        if not self.fd:
            return
        os.write(self.fd, data.encode())

    def resize(self, rows: int, cols: int) -> None:
        """
        Resize the PTY window size.

        Args:
            rows (int): Number of rows for the PTY.
            cols (int): Number of columns for the PTY.
        """
        if not self.fd:
            return
        s = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, s)

    def close(self) -> None:
        """
        Close the PTY and terminate the shell process.
        """
        if self.fd:
            os.close(self.fd)
        if self.pid:
            try:
                os.kill(self.pid, 9)  # Force kill the process
            except ProcessLookupError:
                pass  # Process has already terminated
