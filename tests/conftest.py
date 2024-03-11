import logging

import pytest


@pytest.fixture(scope="session", autouse=True)
def mock_logging():
    logger = logging.getLogger("coles_vs_woolies")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
