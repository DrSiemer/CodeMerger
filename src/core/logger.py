import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from .paths import PERSISTENT_DATA_DIR
from .. import constants as c

log = logging.getLogger("CodeMerger")

class DummyStream:
    """Swallows all writes to prevent crashes when sys.stdout/stderr are None."""
    def write(self, data):
        pass
    def flush(self):
        pass

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception hook to log unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log.critical("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))

def setup_logging():
    """Configures logging for the entire application."""

    # --- Fix for Windowed Mode (console=False) ---
    # In windowed mode, sys.stdout and sys.stderr are None.
    # Any print() or library writing to stdout will crash the app.
    if sys.stdout is None:
        sys.stdout = DummyStream()
    if sys.stderr is None:
        sys.stderr = DummyStream()

    log.setLevel(logging.INFO)

    # Prevent propagation to the root logger if it has handlers
    log.propagate = False

    # --- Rich Handler for console output ---
    # Only add RichHandler if we actually HAVE a real console/terminal.
    # rich.logging can cause issues if initialized without a functional TTY.
    if not log.handlers:
        # Check if we are running in a real terminal
        if sys.stdout and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            try:
                console_handler = RichHandler(
                    rich_tracebacks=True,
                    tracebacks_show_locals=True
                )
                console_handler.setFormatter(logging.Formatter("%(message)s"))
                log.addHandler(console_handler)
            except Exception:
                # Fallback: if Rich fails to init for any reason, don't crash the app
                pass

        # --- File Handler for persistent logging ---
        # This is the most important handler for windowed mode debugging
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
            # Last resort: if we can't even log to a file, we can't do much
            pass

    # Set the global exception hook
    sys.excepthook = handle_exception