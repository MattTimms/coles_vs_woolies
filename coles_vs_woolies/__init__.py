from importlib import metadata

__version__ = metadata.version(__package__)

from .emails import send_weekly_email

__all__ = ["send_weekly_email"]
