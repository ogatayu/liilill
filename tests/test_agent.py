import pytest

from liilill import Agent

DEFAULT_MODEL = "ollama/qwen3:0.6b"

def test_ollama_qwen3_query():
    with Agent(model_name="ollama/qwen3:0.6b") as agent:
        prompt = 'Please say only "Hello World!" without any other text."'
        response = agent.query(prompt, stream=False)
        assert 'Hello World!' in response.output_text

def test_ollama_qwen3_query_stream():
    with Agent(model_name="ollama/qwen3:0.6b") as agent:
        prompt = 'Please say only "Hello World!" without any other text."'
        response = agent.query(prompt, stream=True)

        stream_output_test = ""
        for chunk in response:
            stream_output_test += chunk.get()
            
        assert response.output_text in stream_output_test
        assert response.reasoning in stream_output_test
        assert 'Hello World!' in stream_output_test
    
def test_ollama_qwen3_query_with_reasoning():
    with Agent(model_name="ollama/qwen3:0.6b") as agent:
        prompt = 'Please say only "Hello World!" without any other text."'
        response = agent.query(prompt)
        
        # response.reasoning が空ではないこと
        assert len(response.reasoning) > 0

        # response.output_text に <think> と </think> が含まれていないこと
        assert '<think>' not in response.output_text
        assert '</think>' not in response.output_text

        assert 'Hello World!' in response.output_text

def test_message_histories():
    with Agent(model_name=DEFAULT_MODEL) as agent:
        prompt = 'Hello! How are you?'
        response = agent.query(prompt, stream=True)
        for chunk in response:
            chunk.put()
        
        prompt = 'How can you help?'
        response = agent.query(prompt, stream=False)
        
        # messages には SystemMessage 1件とUserとAssistantのメッセージが2件ずつの、合計5件が含まれること
        assert len(agent.get_messages()) == 5

        # クリア後は SystemMessage 1件だけが含まれること
        agent.clear_messages()
        assert len(agent.get_messages()) == 1
