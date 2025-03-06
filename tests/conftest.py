"""Test configuration for table_maker."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_output_dir():
    """Provide a temporary directory for output files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)
