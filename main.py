# main.py

from stellar.engines.tkinter import TkinterWindow
from stellar.components.emulator import StellarEmulator
from stellar.settings.config import Config
import logging
import traceback

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.debug("Starting Stellar Terminal Emulator")
        config = Config()
        logger.debug("Config loaded")

        window = TkinterWindow()
        logger.debug("TkinterWindow instance created")

        window.create_window("Stellar Terminal", 840, 640)
        logger.debug("Tkinter window created")

        emulator = StellarEmulator(window, config)
        logger.debug("StellarEmulator instance created")

        logger.info("Starting emulator")
        emulator.start()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("Exiting Stellar Terminal Emulator")
