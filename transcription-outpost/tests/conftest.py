import os
import pytest
from pathlib import Path

# Set test environment variables
os.environ["APP_NAME"] = "Transcription Outpost Test"
os.environ["DEBUG"] = "true"

# Create test data directory
@pytest.fixture
def test_data_dir():
    """Create and return a temporary test data directory"""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir 