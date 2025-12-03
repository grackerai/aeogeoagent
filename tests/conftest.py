"""Test configuration and fixtures."""

import pytest


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration before each test."""
    import logging
    # Clear all handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # Reset to default level
    logging.root.setLevel(logging.WARNING)
