import sys
import traceback
import gc
import os
import dearpygui.dearpygui as dpg

from stellar.components.ansi_parser import ANSIParser
from stellar.components.st_pty import StellarPTY
from stellar.settings.config import config
from stellar.utils.logger import StellarLogger

# Set up logger with a basic configuration
logger = StellarLogger("stellar-gui", log_file="stellar-gui.log")


class TerminalWidget:
    def __init__(self, stellar_pty: StellarPTY):
        self.stellar_pty = stellar_pty
        self.stellar_pty.set_output_callback(self.append_output)
        self.prompt = ""
        self.current_command = ""
        self.command_start_position = 0
        self.ansi_parser = ANSIParser()

        self.setup_ui()

    def setup_ui(self):
        with dpg.window(label="Stellar Terminal Emulator", tag="main_window"):
            dpg.add_input_text(
                multiline=True,
                readonly=True,
                tag="terminal_output",
                width=-1,
                height=-1,
            )
            dpg.add_input_text(
                label="",
                callback=self.on_command_enter,
                tag="command_input",
                width=-1,
            )

        # Set colors
        dpg.bind_theme(self.create_theme())

    def create_theme(self):
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_WindowBg,
                    config.theme.hex_to_rgb(config.theme.get_default_bg()),
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_Text,
                    config.theme.hex_to_rgb(config.theme.get_default_fg()),
                )
        return theme

    def initialize_pty(self):
        try:
            logger.info("Initializing StellarPTY")
            self.stellar_pty.start()
            logger.info("StellarPTY initialized successfully")
            self.append_output(self.prompt)
        except Exception as e:
            logger.error(f"Failed to start StellarPTY: {str(e)}")
            logger.error(traceback.format_exc())
            dpg.add_text("Error: Failed to start terminal", color=(255, 0, 0))

    def on_command_enter(self, sender, app_data, user_data):
        command = app_data
        logger.debug(f"Sending command to StellarPTY: {command}")
        self.stellar_pty.send_input(command)
        dpg.set_value("command_input", "")

    def append_output(self, output: str):
        try:
            logger.debug(f"Received output from StellarPTY: {output}")
            current_text = dpg.get_value("terminal_output")
            dpg.set_value("terminal_output", current_text + output)

            if not output.endswith(self.prompt):
                dpg.set_value(
                    "terminal_output", dpg.get_value("terminal_output") + self.prompt
                )

        except Exception as e:
            logger.error(f"Error in append_output: {str(e)}")
            logger.error(traceback.format_exc())


class StellarApp:
    def __init__(self):
        dpg.create_context()
        self.stellar_pty = StellarPTY()
        self.terminal = TerminalWidget(self.stellar_pty)

    def run(self):
        dpg.create_viewport(title="Stellar Terminal Emulator", width=800, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        self.terminal.initialize_pty()
        dpg.start_dearpygui()
        dpg.destroy_context()


def exception_hook(exctype, value, traceback):
    logger.error("Uncaught exception:", exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)


if __name__ == "__main__":
    gc.set_debug(gc.DEBUG_LEAK)
    sys.excepthook = exception_hook
    app = StellarApp()
    app.run()
