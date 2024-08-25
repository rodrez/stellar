from .dear import StellarApp as DearStellarApp
from .tkinter import StellarApp as TkStellarApp
from .pyqt6 import StellarApp as QTStellarAPP


GUI_ENGINES = {
    "tkinter": TkStellarApp,
    "dearpygui": DearStellarApp,
    "pyqt": QTStellarAPP,
}
