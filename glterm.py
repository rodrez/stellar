import os
import pty
import select
import subprocess
import sys
import fcntl
import threading
import struct
import termios
import pygame
import pygame.ftfont
from stellar.components.ansi_parser import ANSIParser
from stellar.settings.config import config
import locale

locale.setlocale(locale.LC_ALL, "")


class TerminalEmulator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buffer = []
        self.scrollback_buffer = []
        self.scrollback_lines = 1000  # Number of lines to keep in scrollback
        self.scroll_position = 0
        self.cursor_x = 0
        self.cursor_y = 0
        self.font = pygame.ftfont.Font(config.font_family, config.font_size)
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
        if ord(char) > 127:  # Non-ASCII character
            print(
                f"Processing non-ASCII character: '{char}' (Unicode: U+{ord(char):04X})"
            )

        # Rest of the method remains the same
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

    def scroll_down(self):
        if self.scrollback_buffer:
            self.buffer.insert(0, self.scrollback_buffer.pop())
            self.buffer.pop()

    def send_input(self, char):
        os.write(self.master_fd, char.encode("utf-8"))

    def render(self, surface):
        surface.fill(
            self.ansi_parser.theme.hex_to_rgb(self.ansi_parser.theme.get_default_bg())
        )
        y_offset = 0
        visible_buffer = self.scrollback_buffer[-self.scroll_position :] + self.buffer
        visible_buffer = visible_buffer[-self.height :]

        for line in visible_buffer:
            x_offset = 0
            for char, style in line:
                text_surface = self.font.render(
                    char, True, style["foreground"], style["background"]
                )
                surface.blit(text_surface, (x_offset, y_offset))
                x_offset += self.font.size(char)[0]
            y_offset += self.font.get_linesize()

        # Render cursor
        if self.scroll_position == 0:
            cursor_pos = (
                self.cursor_x * self.font.size(" ")[0],
                self.cursor_y * self.font.get_linesize(),
            )
            pygame.draw.line(
                surface,
                (255, 0, 0),
                cursor_pos,
                (cursor_pos[0], cursor_pos[1] + self.font.get_linesize()),
            )

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
        """Update the PTY size with the new dimensions."""
        winsize = struct.pack("HHHH", height, width, 0, 0)
        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)


def main():
    pygame.init()
    display = (1920, 1080)
    surface = pygame.display.set_mode(display, pygame.RESIZABLE)
    pygame.display.set_caption("Enhanced ANSI Terminal Emulator")

    color = config.theme.hex_to_rgb(config.theme.get_default_bg())
    surface.fill(color)

    font = pygame.font.Font(config.font_family, config.font_size)
    char_width, char_height = font.size(" ")
    initial_cols = display[0] // char_width
    initial_rows = display[1] // char_height

    terminal = TerminalEmulator(initial_cols, initial_rows)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    terminal.send_input("\n")
                elif event.key == pygame.K_BACKSPACE:
                    terminal.send_input("\b")
                elif event.unicode:
                    terminal.send_input(event.unicode)
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Scroll up
                    terminal.scroll_position = min(
                        terminal.scroll_position + 1, len(terminal.scrollback_buffer)
                    )
                elif event.y < 0:  # Scroll down
                    terminal.scroll_position = max(terminal.scroll_position - 1, 0)
                print(f"Scroll position: {terminal.scroll_position}")
            elif event.type == pygame.VIDEORESIZE:
                surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                new_cols = event.w // char_width
                new_rows = event.h // char_height
                terminal.resize(new_cols, new_rows)

        terminal.render(surface)
        pygame.display.flip()
        clock.tick(120)  # Limit to 60 FPS


if __name__ == "__main__":
    main()
