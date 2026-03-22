"""
logging_config.py — Resilienz.AI Centralized Logging Configuration

Provides dual output logging:
- Console: colored output for real-time visibility
- Files: human-readable logs for app and tests (append mode)

Format ensures readability with 2 empty lines after each log entry.
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

try:
    from config import LOGS_DIR
except ImportError:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOGS_DIR, exist_ok=True)

APP_LOG_FILE = os.path.join(LOGS_DIR, "app.log")
TEST_LOG_FILE = os.path.join(LOGS_DIR, "tests.log")


class HumanReadableFormatter(logging.Formatter):
    DIVIDER = "═" * 72
    SUB_DIVIDER = "─" * 72

    def __init__(self):
        super().__init__(datefmt="%Y-%m-%d %H:%M:%S")

    def format(self, record):
        timestamp = self.formatTime(record, self.datefmt)
        level = record.levelname
        source = f"{record.module}.py::{record.funcName}::{record.lineno}"
        message = record.getMessage()

        extra = ""
        if hasattr(record, "extra_data"):
            extra = record.extra_data

        log_entry = [
            self.DIVIDER,
            f"[{timestamp}] | {level:^7} | {source}",
            self.SUB_DIVIDER,
            f"MESSAGE: {message}",
        ]

        if extra:
            log_entry.append("")
            log_entry.append("CONTEXT:")
            for key, value in extra.items():
                log_entry.append(f"  - {key}: {value}")

        log_entry.append("")
        log_entry.append(self.DIVIDER)
        log_entry.append("")
        log_entry.append("")

        return "\n".join(log_entry)


class SimpleConsoleFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-7s | %(message)s",
            datefmt="%H:%M:%S",
        )

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        return f"{color}{super().format(record)}{self.RESET}"


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    file_handler = RotatingFileHandler(
        log_file,
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(HumanReadableFormatter())

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(SimpleConsoleFormatter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


app_logger = setup_logger("resilienz_app", APP_LOG_FILE)
test_logger = setup_logger("resilienz_tests", TEST_LOG_FILE)


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **context,
):
    record = logger.makeRecord(
        logger.name,
        getattr(logging, level.upper()),
        "(unknown)",
        0,
        message,
        (),
        None,
    )
    record.extra_data = context
    logger.handle(record)


def get_test_run_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")
