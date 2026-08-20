"""SkillBridge AI — Structured & Masked Logging."""

from __future__ import annotations

import logging
import re
import sys
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ANSI Color Codes for terminal
CLR_RESET = "\033[0m"
CLR_CYAN = "\033[36m"
CLR_GREEN = "\033[32m"
CLR_YELLOW = "\033[33m"
CLR_RED = "\033[31m"
CLR_MAGENTA = "\033[35m"
CLR_DIM = "\033[2m"
CLR_BOLD = "\033[1m"


class SensitiveDataFilter(logging.Filter):
    """Masks API keys and secrets before printing to logs."""

    PATTERNS = [
        re.compile(r"(api[_-]?key[\"'\s:=]+)([A-Za-z0-9_\-\.]{8,})", re.IGNORECASE),
        re.compile(r"(app[_-]?key[\"'\s:=]+)([A-Za-z0-9_\-\.]{8,})", re.IGNORECASE),
        re.compile(r"(authorization[\"'\s:=]+Bearer\s+)([A-Za-z0-9_\-\.]{8,})", re.IGNORECASE),
        re.compile(r"(AQ\.[A-Za-z0-9_\-]{15,})"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern in self.PATTERNS:
                msg = pattern.sub(r"\1***MASKED***", msg)
            record.msg = msg
        return True


class PrettyFormatter(logging.Formatter):
    """Custom colorized console log formatter."""

    LEVEL_COLORS = {
        logging.DEBUG: CLR_DIM,
        logging.INFO: CLR_CYAN,
        logging.WARNING: CLR_YELLOW,
        logging.ERROR: CLR_RED,
        logging.CRITICAL: CLR_BOLD + CLR_RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelno, CLR_RESET)
        timestamp = time.strftime("%H:%M:%S", time.localtime(record.created))
        level = f"{record.levelname:<7}"
        prefix = f"{CLR_DIM}[{timestamp}]{CLR_RESET} {color}{level}{CLR_RESET} {CLR_BOLD}[{record.name}]{CLR_RESET}"
        return f"{prefix} {record.getMessage()}"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure root and application loggers with color formatting and secret filtering."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(PrettyFormatter())
        handler.addFilter(SensitiveDataFilter())
        root_logger.addHandler(handler)

    app_logger = logging.getLogger("skillbridge")
    app_logger.setLevel(level)
    return app_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs incoming HTTP requests with method, path, response status, and duration."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.monotonic()
        path = request.url.path
        method = request.method

        response: Response = await call_next(request)
        duration_ms = (time.monotonic() - start_time) * 1000

        # Don't clutter logs with static asset or polling noise
        if path not in {"/health"} and not path.startswith("/static/"):
            status = response.status_code
            status_color = CLR_GREEN if status < 400 else CLR_YELLOW if status < 500 else CLR_RED
            logger = logging.getLogger("skillbridge.http")
            logger.info(
                f"{CLR_BOLD}{method:<6}{CLR_RESET} {path:<30} -> {status_color}{status}{CLR_RESET} ({duration_ms:.1f}ms)"
            )

        return response
