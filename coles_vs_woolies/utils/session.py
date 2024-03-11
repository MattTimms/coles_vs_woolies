import logging
import pathlib
import shutil
import sys
from datetime import timedelta

import platformdirs
import requests_cache
from requests import PreparedRequest, Response
from requests.adapters import HTTPAdapter, Retry

from .wednesday import get_next_wednesday

_logger = logging.getLogger(__name__)
_package_name, *_ = __package__.split(".")
CACHE_LOCATION = pathlib.Path(platformdirs.user_cache_dir(_package_name))


class DefaultTimeoutAdapter(HTTPAdapter):
    def __init__(self, *args, timeout: float, **kwargs):
        self.timeout = timeout
        super().__init__(*args, **kwargs)

    def send(self, request: PreparedRequest, **kwargs) -> Response:
        kwargs["timeout"] = kwargs.get("timeout") or self.timeout
        return super().send(request, **kwargs)


def new_session() -> requests_cache.CachedSession:
    """Return requests_cache.CachedSession with batteries included; i.e. timeout, retries, error-raising."""
    _logger.info(f"requests cache: {CACHE_LOCATION}")
    session = requests_cache.CachedSession(
        CACHE_LOCATION / "requests",
        backend="filesystem",
        serializer="json",
        allowable_methods=["HEAD", "GET", "POST"],
        expire_after=get_next_wednesday(),
        stale_while_revalidate=timedelta(minutes=5),
    )
    session.cache.delete(older_than=timedelta(days=7))

    if "pytest" in sys.modules:
        session = requests_cache.CachedSession(backend="memory")

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    session.mount("https://", DefaultTimeoutAdapter(timeout=5, max_retries=retry_strategy))
    session.hooks = {"response": lambda r, *args, **kwargs: r.raise_for_status()}
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/51.0.2704.103 Safari/537.36"
        }
    )  # some User-Agent
    return session


def clear_cache():
    shutil.rmtree(CACHE_LOCATION)
    _logger.info("cache cleared")
