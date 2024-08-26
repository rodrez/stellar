import pty  # Provides functions to work with pseudo-terminals
import os  # Allows interaction with the operating system, including process control
import select  # Used to handle I/O multiplexing (waiting for I/O operations to complete)
import logging  # Provides a flexible framework for emitting log messages
import queue  # Implements a multi-producer, multi-consumer queue
import threading  # Provides higher-level threading capabilities
from typing import Callable  # Used for type hinting of callable functions

# Set up logger with detailed output format and configuration for file logging
logger = logging.getLogger(__name__)
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
logging.basicConfig(filename="st_pty.log", level=logging.INFO, format=FORMAT)


class StellarPTY:
    """
    StellarPTY is a class that emulates a PTY (pseudo-terminal) session.

    This class can fork a new process, run a shell inside a PTY, and handle I/O between
    the shell and the user. It can also accept callbacks to handle output from the PTY.

    Attributes:
        shell (str): The shell to execute (default is /bin/zsh).
        master_fd (int | None): The master file descriptor for the PTY.
        pid (int | None): The process ID of the forked child.
        old_tty (list | None): A placeholder for the original TTY settings.
        input_queue (queue.Queue): Queue to hold user input before sending it to the PTY.
        output_callback (Callable[[str], None] | None): Callback function to handle output from the PTY.
    """

    def __init__(self, shell: str = "/bin/zsh") -> None:
        """
        Initializes the StellarPTY instance.

        Args:
            shell (str): Path to the shell binary to run in the PTY. Defaults to "/bin/zsh".
        """
        self.shell: str = shell  # Shell to be loaded in the PTY (default: zsh)
        self.master_fd: int | None = None  # Master file descriptor for the PTY
        self.pid: int | None = None  # Process ID of the child process
        self.old_tty: list | None = (
            None  # Placeholder for TTY settings (not used in this example)
        )
        self.input_queue: queue.Queue = (
            queue.Queue()
        )  # Queue to store user input for the PTY
        self.output_callback: Callable[[str], None] | None = (
            None  # Callback for handling shell output
        )

    def start(self) -> None:
        """
        Starts the PTY session by forking the process and initializing the shell.

        The parent process manages I/O between the user and the shell, while the child process
        executes the shell.
        """
        try:
            self.pid, self.master_fd = pty.fork()  # Forks the process and creates a PTY
        except OSError as e:
            logger.error(
                f"Failed to fork pty: {e}"
            )  # Logs any errors in case of failure
            raise

        if self.pid == 0:
            # Child process: execute the shell inside the PTY
            try:
                self.load_shell()  # Loads the desired shell
            except Exception as e:
                logger.error(f"Failed to load shell: {e}")  # Logs failure and exits
                os._exit(1)
        else:
            # Parent process: handle I/O in a separate thread
            threading.Thread(
                target=self.handle_io, daemon=True
            ).start()  # Start a background thread for I/O handling

    def load_shell(self) -> None:
        """
        Replaces the current process image with the specified shell process.

        This function uses execvp to execute the shell.
        """
        logger.info(
            f"Initializing shell: {self.shell}"
        )  # Logs the shell initialization
        os.execvp(
            self.shell, [self.shell]
        )  # Replaces the current process with the shell

    def handle_io(self, read_size: int = 1024) -> None:
        """
        Handles input/output between the user and the shell running in the PTY.

        This function runs in a loop to continuously read from the PTY and write user input
        to the shell.

        Args:
            read_size (int): Number of bytes to read at a time from the PTY. Defaults to 1024.
        """
        while True:
            try:
                # Wait for data to be available for reading from the PTY
                r, _, _ = select.select([self.master_fd], [], [], 0.1)

                if self.master_fd in r:
                    # Read data from the PTY
                    data: bytes = os.read(self.master_fd, read_size)
                    if not data:
                        break  # Exit if no data is returned (i.e., PTY closed)
                    if self.output_callback:
                        print("Data: ", data)
                        self.output_callback(
                            data.decode("utf-8", errors="replace")
                        )  # Call the callback with the decoded data

                # If there is input data queued, send it to the PTY
                if not self.input_queue.empty() and self.master_fd:
                    input_data = self.input_queue.get()
                    os.write(
                        self.master_fd, input_data.encode("utf-8")
                    )  # Write input data to the PTY

            except OSError as e:
                logger.error(f"OSError in handle_io: {e}")  # Log any OS-related errors
                break
            except Exception as e:
                logger.error(
                    f"Unexpected error in handle_io: {e}"
                )  # Log unexpected errors
                break

    def send_input(self, input_data: str) -> None:
        """
        Sends input to the PTY via a queue.

        This function queues the input, which will be processed by the handle_io function.

        Args:
            input_data (str): The input string to send to the PTY.
        """
        self.input_queue.put(
            input_data + "\n"
        )  # Add the input data to the queue with a newline
        logger.info(f"Input sent to queue: {input_data}")  # Log the input data

    def set_output_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the callback function to handle output from the PTY.

        Args:
            callback (Callable[[str], None]): A function that takes a string as input and handles PTY output.
        """
        self.output_callback = callback  # Assign the output callback


def test_stellar_pty():
    """
    A test function to run the StellarPTY class.

    It sets up the PTY, starts it, and continuously reads input from the user and sends it to the PTY.
    The output from the shell is printed in real-time.
    """

    def print_output(output: str) -> None:
        """
        Callback function to print the output from the PTY.

        Args:
            output (str): The output string from the PTY to be printed.
        """
        print(output, end="")  # Print the output without adding a new line

    # Create an instance of StellarPTY and set the output callback to print_output
    pty = StellarPTY()
    pty.set_output_callback(print_output)
    pty.start()  # Start the PTY session

    print("StellarPTY started. Type 'exit' to quit.")

    try:
        # Continuously read input from the user and send it to the PTY
        while True:
            user_input = input()
            if user_input.strip().lower() == "exit":  # Exit if the user types "exit"
                break
            pty.send_input(user_input)  # Send input to the PTY
    except KeyboardInterrupt:
        print("\nExiting...")  # Handle user interruption with Ctrl+C


if __name__ == "__main__":
    test_stellar_pty()  # Run the test function if this script is executed directly
