import pytest

from liilill import Agent

MODEL_NAME = "ollama/gemma3:1b"

def test_query():
    with Agent(model_name=MODEL_NAME) as agent:
        prompt = 'Please say only "Hello World!" without any other text."'
        response = agent.query(prompt, stream=False)
        assert 'Hello World!' in response.output_text

def test_query_stream():
    with Agent(model_name=MODEL_NAME) as agent:
        prompt = 'Please say only "Hello World!" without any other text."'
        response = agent.query(prompt, stream=True)

        stream_output_test = ""
        for chunk in response:
            stream_output_test += chunk.get()
            
        assert stream_output_test == response.output_text
        assert 'Hello World!' in stream_output_test
    
