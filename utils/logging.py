"""Console logging by default; optional bounded file logs for local operations."""
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path


def setup_logging():
    handlers = [logging.StreamHandler()]
    log_file = os.environ.get("LOG_FILE")
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5))
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )
    if os.getenv("SQL_ECHO", "false").lower() != "true":
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
