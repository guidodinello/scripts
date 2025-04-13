import logging
import os
import sys
from datetime import datetime


class LoggerSetup:
    def __init__(self, log_dir="logs", log_level=logging.INFO, console_output=True):
        self.log_dir = log_dir
        self.log_level = log_level
        self.console_output = console_output

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        current_date = datetime.now().strftime("%Y-%m-%d")
        self.log_file = os.path.join(log_dir, f"app_{current_date}.log")

    def setup(self, logger_name=None):
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)

        if logger.handlers:
            logger.handlers.clear()

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        )

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger


def get_logger(
    name=None,
    log_dir="logs",
    log_level=logging.INFO,
    console_output=True,
) -> logging.Logger:
    logger_setup = LoggerSetup(log_dir, log_level, console_output)
    return logger_setup.setup(name)
