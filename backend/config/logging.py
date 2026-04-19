import logging
import sys


class ColorFormatter(logging.Formatter):
    """
    Lightweight ANSI color formatter for console logs.

    This is intended for local development only; production should typically
    log plain text (or structured logs) to files/aggregators.
    """

    _RESET = "\x1b[0m"
    _DIM = "\x1b[2m"

    _LEVEL_COLORS: dict[int, str] = {
        logging.DEBUG: "\x1b[36m",  # cyan
        logging.INFO: "\x1b[32m",  # green
        logging.WARNING: "\x1b[33m",  # yellow
        logging.ERROR: "\x1b[31m",  # red
        logging.CRITICAL: "\x1b[1;31m",  # bold red
    }

    def __init__(self, *args, use_colors: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_colors = use_colors

    @staticmethod
    def _should_use_colors_fallback() -> bool:
        stream = getattr(sys, "stderr", None)
        if stream is None:
            return False
        isatty = getattr(stream, "isatty", None)
        if isatty is None:
            return False
        try:
            return bool(isatty())
        except Exception:
            return False

    def format(self, record: logging.LogRecord) -> str:
        use_colors = self.use_colors and self._should_use_colors_fallback()
        if not use_colors:
            return super().format(record)

        original_levelname = record.levelname
        original_name = record.name
        try:
            color = self._LEVEL_COLORS.get(record.levelno, "")
            record.levelname = f"{color}{original_levelname}{self._RESET}" if color else original_levelname
            record.name = f"{self._DIM}{original_name}{self._RESET}"
            return super().format(record)
        finally:
            record.levelname = original_levelname
            record.name = original_name

