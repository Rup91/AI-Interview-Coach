"""Structured logging setup.

Emits one JSON object per log line to stdout. A plain formatter is used
(no third-party logging library) to avoid introducing a new framework
without approval, per CLAUDE.md.
"""

import logging
import sys

_LOG_FORMAT = (
    '{"timestamp":"%(asctime)s","level":"%(levelname)s",'
    '"logger":"%(name)s","message":"%(message)s"}'
)
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def setup_logging(log_level: str = "INFO") -> None:
    """Configure the root logger with a structured stdout handler.

    Safe to call multiple times: existing handlers are replaced rather
    than duplicated.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())
