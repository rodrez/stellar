import sys
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import queue


class ANSIParser:
    def __init__(self):
        self.reset_style()

    def reset_style(self):
        self.style = {
            "foreground": "white",
            "background": "black",
            "bold": False,
            "italic": False,
            "underline": False,
        }

    def parse(self, text):
        # This is a simplified ANSI parser. In a real implementation, you'd want to handle more ANSI codes.
        parsed = []
        current_text = ""
        i = 0
        while i < len(text):
            if text[i] == "\033" and text[i + 1] == "[":
                if current_text:
                    parsed.append((current_text, self.style.copy()))
                    current_text = ""
                end = text.find("m", i)
                if end != -1:
                    self.handle_ansi_code(text[i + 2 : end])
                    i = end
            else:
                current_text += text[i]
            i += 1
        if current_text:
            parsed.append((current_text, self.style.copy()))
        return parsed

    def handle_ansi_code(self, code):
        if code == "0":
            self.reset_style()
        elif code == "1":
            self.style["bold"] = True
        elif code == "3":
            self.style["italic"] = True
        elif code == "4":
            self.style["underline"] = True
        elif code.startswith("3") and len(code) == 2:
            color_map = [
                "black",
                "red",
                "green",
                "yellow",
                "blue",
                "magenta",
                "cyan",
                "white",
            ]
            self.style["foreground"] = color_map[int(code[1])]
        elif code.startswith("4") and len(code) == 2:
            color_map = [
                "black",
                "red",
                "green",
                "yellow",
                "blue",
                "magenta",
                "cyan",
                "white",
            ]
            self.style["background"] = color_map[int(code[1])]


class StellarApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        self.ansi_parser = ANSIParser()
        self.command_start_position = "1.0"
        self.current_command = ""
        self.process = None
        self.output_queue = queue.Queue()
        self.after(100, self.check_output_queue)

    def create_widgets(self):
        self.text_area = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, bg="black", fg="white"
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.bind("<KeyPress>", self.on_key_press)
        self.text_area.bind("<KeyRelease>", self.on_key_release)

    def start_process(self):
        try:
            self.process = subprocess.Popen(
                ["bash" if os.name != "nt" else "cmd"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
            )
            threading.Thread(target=self.read_output, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start terminal: {str(e)}")

    def read_output(self):
        while True:
            output = self.process.stdout.readline()
            if output == "" and self.process.poll() is not None:
                break
            if output:
                self.output_queue.put(output.strip())
        rc = self.process.poll()
        return rc

    def check_output_queue(self):
        while not self.output_queue.empty():
            output = self.output_queue.get()
            self.append_output(output + "\n")
        self.after(100, self.check_output_queue)

    def append_output(self, output):
        parsed_output = self.ansi_parser.parse(output)
        for text, style in parsed_output:
            self.text_area.insert(tk.END, text, style)
        self.text_area.see(tk.END)
        self.command_start_position = self.text_area.index(tk.END + "-1c")

    def on_key_press(self, event):
        if event.keysym == "Return":
            self.handle_return()
            return "break"
        elif event.keysym == "BackSpace":
            if self.text_area.index(tk.INSERT) <= self.command_start_position:
                return "break"
        elif event.keysym == "Left":
            if self.text_area.index(tk.INSERT) <= self.command_start_position:
                return "break"
        return None

    def on_key_release(self, event):
        self.current_command = self.text_area.get(self.command_start_position, tk.END)

    def handle_return(self):
        command = self.current_command.strip() + "\n"
        self.text_area.insert(tk.END, "\n")
        self.process.stdin.write(command)
        self.process.stdin.flush()
        self.current_command = ""

    def start(self):
        self.start_process()


def exception_hook(exctype, value, traceback):
    print("Uncaught exception:", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)


if __name__ == "__main__":
    sys.excepthook = exception_hook
    root = tk.Tk()
    root.title("Tkinter Terminal Emulator")
    app = StellarApp(master=root)
    app.start_process()
    root.mainloop()
