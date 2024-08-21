import os
import subprocess
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import re
import logging

# Set up logging
logging.basicConfig(filename="terminal_emulator.log", level=logging.DEBUG)

# Regular expression for matching ANSI escape codes
ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


class TerminalEmulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Basic Terminal Emulator")
        self.geometry("800x600")

        # Text area with scroll for displaying terminal output
        self.text_area = ScrolledText(self, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.bind("<Return>", self.on_enter)  # Capture Enter key

        self.cmd = ""  # Command input buffer

        # Start the shell process
        self.process = subprocess.Popen(
            ["/bin/bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Start threads to read stdout and stderr
        threading.Thread(
            target=self.read_output, args=(self.process.stdout,), daemon=True
        ).start()
        threading.Thread(
            target=self.read_output, args=(self.process.stderr,), daemon=True
        ).start()

        # Send initial commands to set up the environment
        self.send_cmd("PS1='$ '")  # Set a simple prompt

    def on_enter(self, event):
        """Handle Enter key pressed in the text area."""
        # Get the command from the text area
        self.cmd = self.text_area.get("insert linestart", "insert").strip()
        # Insert the command in the text widget to simulate typing
        self.text_area.insert(tk.END, "\n")
        self.text_area.mark_set(tk.INSERT, tk.END)
        # Send the command to the shell
        self.send_cmd(self.cmd)
        return "break"  # Prevent the default behavior of the Enter key

    def send_cmd(self, cmd):
        """Send the command to the child process (shell)."""
        # Only send the command if it's not empty
        if cmd:
            logging.debug(f"Sending command: {cmd}")
            if cmd == "clear":
                self.text_area.delete(1.0, tk.END)
            self.process.stdin.write(cmd + "\n")
            self.process.stdin.flush()

    def read_output(self, pipe):
        """Read output from the child process (shell)."""
        for line in pipe:
            # Handle clear command
            if line.strip() == "\x1b[H\x1b[2J":
                self.text_area.delete(1.0, tk.END)
                continue
            # Strip ANSI escape codes
            clean_output = ansi_escape.sub("", line)
            # Insert the cleaned output in the text widget
            self.text_area.insert(tk.END, clean_output)
            self.text_area.see(tk.END)  # Scroll to the end of the output
            logging.debug(f"Received output: {clean_output.strip()}")


if __name__ == "__main__":
    app = TerminalEmulator()
    app.mainloop()
