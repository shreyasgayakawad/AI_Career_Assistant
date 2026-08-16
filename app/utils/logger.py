"""
Application Logger

Provides structured logging with rotating file handler and console output.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Base log directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Determine log level from environment
_log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
_log_level = getattr(logging, _log_level_str, logging.INFO)

# Formatter
_formatter = logging.Formatter(
    fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Logger instance
logger = logging.getLogger("AIJobBot")
logger.setLevel(_log_level)

# Avoid duplicate handlers if re-imported
if not logger.handlers:
    # Rotating file handler (5 MB max per file, up to 3 backups)
    _file_handler = RotatingFileHandler(
        filename=LOG_DIR / "job_bot.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    _file_handler.setLevel(_log_level)
    _file_handler.setFormatter(_formatter)
    logger.addHandler(_file_handler)

    # Console stream handler
    _console_handler = logging.StreamHandler()
    _console_handler.setLevel(_log_level)
    _console_handler.setFormatter(_formatter)
    logger.addHandler(_console_handler)