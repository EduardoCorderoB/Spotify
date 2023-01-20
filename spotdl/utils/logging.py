"""
Module for logging
"""

import logging

from rich import get_console
from rich.logging import RichHandler
from rich.theme import Theme
from rich.traceback import install

__all__ = [
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARNING",
    "WARN",
    "INFO",
    "MATCH",
    "DEBUG",
    "NOTSET",
    "init_logging",
    "SpotdlFormatter",
    "LEVEL_TO_NAME",
    "NAME_TO_LEVEL",
]

# https://github.com/python/cpython/blob/3.10/Lib/logging/__init__.py
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
MATCH = 15
DEBUG = 10
NOTSET = 0

LEVEL_TO_NAME = {
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    MATCH: "MATCH",
    DEBUG: "DEBUG",
    NOTSET: "NOTSET",
}

NAME_TO_LEVEL = {
    "CRITICAL": CRITICAL,
    "FATAL": FATAL,
    "ERROR": ERROR,
    "WARN": WARNING,
    "WARNING": WARNING,
    "INFO": INFO,
    "MATCH": MATCH,
    "DEBUG": DEBUG,
    "NOTSET": NOTSET,
}

THEME = Theme(
    {
        "bar.back": "grey23",
        "bar.complete": "rgb(165,66,129)",
        "bar.finished": "rgb(114,156,31)",
        "bar.pulse": "rgb(165,66,129)",
        "general": "green",
        "nonimportant": "rgb(40,100,40)",
        "progress.data.speed": "red",
        "progress.description": "none",
        "progress.download": "green",
        "progress.filesize": "green",
        "progress.filesize.total": "green",
        "progress.percentage": "green",
        "progress.remaining": "rgb(40,100,40)",
        "logging.level.debug": "blue",
        "logging.level.info": "green",
        "logging.level.warning": "yellow",
        "logging.level.error": "red",
        "logging.level.critical": "bold red",
    }
)


class SpotdlFormatter(logging.Formatter):
    """
    A custom logger for spotdl.
    """

    highlight = RichHandler.HIGHLIGHTER_CLASS()

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record.
        """

        result = super().format(record)

        if record.levelno == DEBUG:
            return f"[blue]{result}"

        if record.levelno == MATCH:
            return f"[magenta]{result}"

        if record.levelno == INFO:
            return f"[green]{result}"

        if record.levelno == WARNING:
            return f"[yellow]{result}"

        if record.levelno == ERROR:
            return f"[red]{result}"

        if record.levelno == CRITICAL:
            return f"[bold red]{result}"

        return result


def init_logging(log_level: str):
    """
    Initialize logging for spotdl.

    ### Arguments
    - `console`: The console to use.
    - `log_level`: The log level to use.
    """

    # Don't log too much
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("spotipy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("syncedlyrics").setLevel(logging.WARNING)

    # Create console
    console = get_console()
    console.push_theme(THEME)

    # Add matching level loggers
    logging.addLevelName(MATCH, "MATCH")

    # Create a rich handler
    rich_handler = RichHandler(
        show_time=log_level == "DEBUG",
        log_time_format="[%X]",
        omit_repeated_times=False,
        console=console,
        level=log_level,
        markup=True,
        show_path=log_level == "DEBUG",
        show_level=log_level == "DEBUG",
        rich_tracebacks=True,
    )

    msg_format = "%(message)s"
    if log_level == "DEBUG":
        msg_format = "%(threadName)s - %(message)s"

    # Add rich handler to spotdl logger
    rich_handler.setFormatter(SpotdlFormatter(msg_format))

    # Create spotdl logger
    spotdl_logger = logging.getLogger("spotdl")

    # Setup spotdl logger
    spotdl_logger.setLevel(log_level)
    spotdl_logger.addHandler(rich_handler)

    # Install rich traceback handler
    install(show_locals=False, extra_lines=1, console=console)
