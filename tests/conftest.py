import pytest
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

@pytest.fixture(autouse=True)
def load_env_vars():
    """Fixture to load environment variables before each test."""
    load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
    print("Environment variables loaded from .env file:")
    for key, value in os.environ.items():
        if key.startswith(('OLLAMA', 'API')):
            print(f"  {key}={value}")