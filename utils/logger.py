import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DefaultSettings:
    level = logging.DEBUG
    format: str = "%(asctime)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s"


class Formatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    COLORS = {
        "green": "\x1b[32m",
        "grey": "\x1b[38;20m",
        "yellow": "\x1b[33;20m",
        "red": "\x1b[31;20m",
        "bold_red": "\x1b[31;1m",
        "reset": "\x1b[0m",
    }

    def __init__(self, fmt, datefmt="%Y-%m-%d %H:%M:%S"):
        super().__init__(fmt, datefmt)
        self.formats = {
            logging.DEBUG: self.COLORS["grey"] + fmt + self.COLORS["reset"],
            logging.INFO: self.COLORS["green"] + fmt + self.COLORS["reset"],
            logging.WARNING: self.COLORS["yellow"] + fmt + self.COLORS["reset"],
            logging.ERROR: self.COLORS["red"] + fmt + self.COLORS["reset"],
            logging.CRITICAL: self.COLORS["bold_red"] + fmt + self.COLORS["reset"],
        }

    def format(self, record):
        formatter = logging.Formatter(self.formats.get(record.levelno), self.datefmt)
        return formatter.format(record)


class CustomLogger:
    """Enhanced logger with color formatting and file rotation"""

    def __init__(
        self,
        log_dir: Path | None = None,
        settings: DefaultSettings | None = None,
        formatter: Formatter | None = None,
    ):
        self.settings = settings or DefaultSettings()
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.formatter = formatter or Formatter(self.settings.format)

    def get_logger(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(self.settings.level)

        # Avoid adding handlers multiple times
        if logger.handlers:
            return logger

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        logger.addHandler(console_handler)

        # File handler - daily rotating log file
        today = datetime.now().strftime("%Y-%m-%d")
        file_handler = logging.FileHandler(
            self.log_dir / f"{today}.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(self.formatter)
        logger.addHandler(file_handler)

        return logger


_logger_instance = CustomLogger()


def get_logger() -> logging.Logger:
    """Get a logger instance with the specified name."""
    return _logger_instance.get_logger(__name__)
