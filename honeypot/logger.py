# logger.py
"""Logging helpers for the honeypot."""
import logging
import os

LOG_PATH = "/app/logs/honeypot.log"

def create_logger():
    """Return a logger that writes to the log file"""
    logger = logging.getLogger("honeypot")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    os.makedirs("/app/logs", exist_ok=True)

    handler = logging.FileHandler(LOG_PATH)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
