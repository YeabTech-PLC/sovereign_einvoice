import json
import logging
from datetime import UTC, datetime

from app.core.config import Settings


class SafeJsonFormatter(logging.Formatter):
    """Output JSON logs using an explicit allowlist of fields."""

    ALLOWED_FIELDS = (
        "event",
        "correlation_id",
        "method",
        "route",
        "status_code",
        "duration_ms",
        "exception_type",
        "app_env",
    )

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=UTC,
            ).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "event": "application_event",
        }

        for field in self.ALLOWED_FIELDS:
            value = getattr(record, field, None)

            if isinstance(value, (str, int, float, bool)):
                payload[field] = value

        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )


def configure_logging(settings: Settings) -> None:
    """Configure application logging with safe JSON output."""
    handler = logging.StreamHandler()
    handler.setFormatter(SafeJsonFormatter())

    root_logger = logging.getLogger()

    for existing_handler in root_logger.handlers[:]:
        root_logger.removeHandler(existing_handler)
        existing_handler.close()

    root_logger.addHandler(handler)
    root_logger.setLevel(settings.log_level)

    # Uvicorn's normal access logs can include raw paths and query strings.
    # Our request middleware will produce sanitized access events instead.
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.disabled = True
