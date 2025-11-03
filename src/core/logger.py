import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from .paths import PERSISTENT_DATA_DIR
from .. import constants as c

log = logging.getLogger("CodeMerger")

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception hook to log unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log.critical("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))

def setup_logging():
    """Configures logging for the entire application."""
    log.setLevel(logging.INFO)

    # Prevent propagation to the root logger if it has handlers
    log.propagate = False

    # --- Rich Handler for console output ---
    # Only add RichHandler if no handlers are configured, to avoid duplicates.
    if not log.handlers:
        console_handler = RichHandler(
            rich_tracebacks=True,
            tracebacks_show_locals=True
        )
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        log.addHandler(console_handler)

        # --- File Handler for persistent logging ---
        try:
            log_path = os.path.join(PERSISTENT_DATA_DIR, c.LOG_FILENAME)
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=c.LOG_MAX_BYTES,
                backupCount=c.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            log.addHandler(file_handler)
        except Exception as e:
            log.error(f"Failed to set up file logging at {PERSISTENT_DATA_DIR}: {e}")

    # Set the global exception hook
    sys.excepthook = handle_exception