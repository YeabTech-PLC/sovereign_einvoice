import logging

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure consistent application logging."""
    logging.basicConfig(
        level=settings.log_level,
        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
        datefmt="%Y-%m-%dT%H:%M:%S",
        force=True,
    )
