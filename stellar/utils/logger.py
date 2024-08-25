import logging
from logging.handlers import RotatingFileHandler


class StellarLogger(logging.Logger):
    def __init__(self, name: str, log_file: str = "stellar.log", level=logging.INFO):
        """
        Custom logger class that inherits from logging.Logger.

        Args:
            name (str): The name of the logger.
            log_file (str): The log file path. Defaults to "stellar.log".
            level (int): The logging level. Defaults to logging.DEBUG.
        """
        # Call the parent class (Logger) __init__ method
        super().__init__(name, level)

        # Create handlers: Console and File handlers
        console_handler = logging.StreamHandler()  # Output logs to console
        file_handler = RotatingFileHandler(
            log_file, maxBytes=1024 * 1024, backupCount=3
        )  # Output logs to a rotating file

        # Define log format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
        )

        # Attach formatters to handlers
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to the logger instance (self)
        self.addHandler(console_handler)
        self.addHandler(file_handler)
