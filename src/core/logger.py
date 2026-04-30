import logging
import sys
import os
import re
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from .paths import PERSISTENT_DATA_DIR
from .. import constants as c

log = logging.getLogger("CodeMerger")

_SECRET_PATTERNS = [
    (re.compile(r"(?i)(bearer\s+)[^\s\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(api[_-]key[\"']?\s*[:=]\s*[\"']?)[^\s\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(sk-[A-Za-z0-9]{20,})"), "[REDACTED_OPENAI]"),
    (re.compile(r"(?i)(ghp_[A-Za-z0-9]{20,})"), "[REDACTED_GITHUB]"),
    (re.compile(r"(?i)(https?://)[^:@\s]+:[^@\s]+@"), r"\1[USER:PASS_REDACTED]@")
]

class RedactingFormatter(logging.Formatter):
    """Wraps log records to scrub sensitive data before output."""
    def format(self, record):
        msg = super().format(record)
        for pattern, replacement in _SECRET_PATTERNS:
            msg = pattern.sub(replacement, msg)
        return msg

class DummyStream:
    """Swallows writes to prevent crashes when standard streams are unavailable"""
    def write(self, data):
        pass
    def flush(self):
        pass

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log.critical("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))

def setup_logging():
    # In windowed mode sys.stdout/stderr are None; DummyStream prevents attribute errors
    if sys.stdout is None:
        sys.stdout = DummyStream()
    if sys.stderr is None:
        sys.stderr = DummyStream()

    log.setLevel(logging.INFO)

    log.propagate = False

    if not log.handlers:
        is_console_forced = "--console" in sys.argv
        is_tty = sys.stdout and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

        if is_console_forced or is_tty:
            try:
                console_handler = RichHandler(
                    rich_tracebacks=True,
                    tracebacks_show_locals=True,
                    markup=True
                )
                console_handler.setFormatter(RedactingFormatter("%(message)s"))
                log.addHandler(console_handler)
            except Exception:
                pass

        try:
            log_path = os.path.join(PERSISTENT_DATA_DIR, c.LOG_FILENAME)
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=c.LOG_MAX_BYTES,
                backupCount=c.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_formatter = RedactingFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            log.addHandler(file_handler)
        except Exception as e:
            pass

    sys.excepthook = handle_exception