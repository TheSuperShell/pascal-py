import logging
import pytest


@pytest.fixture(scope="function")
def logger() -> logging.Logger:
    return logging.Logger("test_logger")
