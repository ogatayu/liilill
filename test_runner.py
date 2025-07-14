#!/usr/bin/env python3
"""
Test runner script that loads environment variables from .env file
and mocks external API calls for testing.
"""

import os
import sys
from dotenv import load_dotenv
import pytest
from unittest.mock import patch, MagicMock

class MockResponseChunk:
    """Mock response chunk that behaves like the real ResponseChunk."""
    def __init__(self, content):
        self.content = content

    def put(self):
        """Mock put method that does nothing."""
        pass

    def get(self):
        """Return the content as string."""
        return str(self.content)

    def __str__(self):
        """Return the content as string."""
        return str(self.content)

class MockStreamChunk(dict):
    """Mock streaming chunk that behaves like the real streaming response."""
    def __init__(self, content):
        super().__init__()
        delta_obj = MagicMock()
        delta_obj.content = content
        self['choices'] = [{
            'delta': delta_obj
        }]

def main():
    # Load environment variables from .env file
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

    print("Environment variables loaded from .env file:")
    for key, value in os.environ.items():
        if key.startswith(('OLLAMA', 'API')):
            print(f"  {key}={value}")

    # Mock litellm.completion to avoid actual API calls
    with patch('litellm.completion') as mock_completion:
        # Create a mock response object for non-streaming case
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Hello World!", reasoning_content="Mock reasoning"))
        ]

        # Create a mock streaming response
        mock_stream_response = MagicMock()
        mock_stream_chunks = [
            MockStreamChunk("Hello "),
            MockStreamChunk("World!"),
            MockStreamChunk("<think>Mock reasoning</think>")
        ]
        mock_stream_response.__iter__.return_value = mock_stream_chunks
        mock_stream_response.choices = [
            MagicMock(message=MagicMock(content="Hello World!", reasoning_content="Mock reasoning"))
        ]

        # Set up the mock to return different responses based on stream parameter
        def side_effect(stream, **kwargs):
            if stream:
                return mock_stream_response
            return mock_response

        mock_completion.side_effect = side_effect

        # Run pytest
        sys.exit(pytest.main(['-v', 'tests/']))

if __name__ == '__main__':
    main()