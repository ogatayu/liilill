import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def pytest_configure(config):
    """Print environment variables for debugging."""
    print("Environment variables loaded from .env file:")
    for key, value in os.environ.items():
        if key.startswith(('OLLAMA', 'OPENAI', 'ANTHROPIC')):
            print(f"  {key}={value}")