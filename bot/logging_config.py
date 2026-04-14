import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import colorama

# Initialize colorama
colorama.init(autoreset=True)

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

class ColoredConsoleFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    COLORS = {
        logging.DEBUG: colorama.Fore.CYAN,
        logging.INFO: colorama.Fore.GREEN,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Fore.RED + colorama.Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, '')
        reset = colorama.Style.RESET_ALL
        
        # Determine the format string
        # timestamp | level | module | message
        message = super().format(record)
        return f"{color}{message}{reset}"

def get_logger(name: str) -> logging.Logger:
    """
    Sets up and returns a logger that writes to a file and the console.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Standard format: timestamp | level | module | message
    fmt = "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    
    # File Handler - Rotating logs (max 5MB, 3 backups)
    log_file = os.path.join(LOGS_DIR, 'trading_bot.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Keep console slightly cleaner unless debugging
    console_handler.setFormatter(ColoredConsoleFormatter(fmt, datefmt=datefmt))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
