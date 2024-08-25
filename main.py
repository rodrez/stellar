import sys
from PyQt6.QtWidgets import QApplication
import tkinter as tk

from stellar.gui import GUI_ENGINES
from stellar.settings.config import config
from stellar.utils.logger import StellarLogger

logger = StellarLogger("stellar-term")

if __name__ == "__main__":
    gui_engine = config.gui_engine
    StellarApp = GUI_ENGINES.get(gui_engine, "pyqt")

    logger.info(f"Using {gui_engine if gui_engine else 'pyqt'} gui engine")
    if gui_engine == "pyqt":
        app = QApplication(sys.argv)  # Create the QApplication instance
        window = StellarApp()  # Create the main window (TerminalApp)
        window.show()  # Display the window
        sys.exit(app.exec())  # Run the application event loop
    elif gui_engine == "tkinter":
        root = tk.Tk()
        root.title("Tkinter Terminal Emulator")
        app = StellarApp(master=root)
        app.start_process()
        root.mainloop()
    elif gui_engine == "dearpygui":
        app = StellarApp()
        app.run()
