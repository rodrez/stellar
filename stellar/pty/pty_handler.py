import os
import pty
import select
import termios
import struct
import fcntl
import logging
import signal
import subprocess


class PTYHandler:
    def __init__(self):
        self.fd: int | None = None
        self.pid: int | None = None
        self.is_wsl = self._check_wsl()

    def _check_wsl(self):
        try:
            with open("/proc/version", "r") as f:
                return "microsoft" in f.read().lower()
        except:
            return False

    def spawn(self, shell: str = "/bin/bash") -> None:
        # if self.is_wsl:
        #     logging.info("WSL")
        #     # Use subprocess for WSL to avoid potential pty issues
        #     process = subprocess.Popen(
        #         shell,
        #         stdin=subprocess.PIPE,
        #         stdout=subprocess.PIPE,
        #         stderr=subprocess.PIPE,
        #         env=self._get_clean_env(),
        #         start_new_session=True,
        #         universal_newlines=True,
        #         bufsize=0,
        #     )
        #     self.pid = process.pid
        #     self.fd = process.stdout.fileno()
        # else:
        self.pid, self.fd = pty.fork()
        if self.pid == 0:  # Child process
            os.chdir(os.path.expanduser("~"))
            os.execvpe(shell, [shell], self._get_clean_env())

    def _get_clean_env(self):
        env = os.environ.copy()
        env.pop("OLDPWD", None)
        env.pop("PWD", None)
        return env

    def read(self, max_read_bytes: int = 1024) -> bytes:
        if not self.fd:
            return b""
        try:
            r, _, _ = select.select([self.fd], [], [], 0.1)
            if not r:
                return b""
            return os.read(self.fd, max_read_bytes)
        except (OSError, IOError) as e:
            logging.error(f"Error reading from PTY: {e}")
            if not self.is_alive():
                logging.info("PTY process is not alive. Attempting to respawn.")
                self.respawn()
            return b""

    def write(self, data: str) -> None:
        if not self.fd:
            return
        try:
            os.write(self.fd, data.encode())
        except (OSError, IOError) as e:
            logging.error(f"Error writing to PTY: {e}")
            if not self.is_alive():
                logging.info("PTY process is not alive. Attempting to respawn.")
                self.respawn()

    def is_alive(self) -> bool:
        if self.pid is None:
            return False
        try:
            os.kill(self.pid, 0)
            return True
        except OSError:
            return False

    def respawn(self) -> None:
        self.close()
        self.spawn()

    def close(self) -> None:
        if self.fd:
            try:
                os.close(self.fd)
            except OSError:
                pass
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)
                os.waitpid(self.pid, 0)
            except ProcessLookupError:
                pass  # Process has already terminated
        self.fd = None
        self.pid = None

    def resize(self, rows: int, cols: int) -> None:
        if not self.fd:
            return
        try:
            s = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, s)
        except (OSError, IOError) as e:
            logging.error(f"Error resizing PTY: {e}")
