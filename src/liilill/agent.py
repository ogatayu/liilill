import litellm
import sys
import re

class Agent:
    """
    A class to manage an agent for interacting with an LLM.
    It is intended to be used with a `with` statement so that resources are automatically released after use.
    """
    def __init__(
        self,
        model_name: str,
        api_base: str = None,
        system_prompt: str = None,
        ):
        """
        Initializes the Agent.

        Args:
            model_name (str): Specify the model name to use in litellm format.
            api_base (str, optional): The base URL for the API.
        """
        self._model_name = model_name
        self._api_base = api_base
        self._system_prompt = system_prompt if system_prompt else "You are a helpful assistant."
        self._messages = []
        self.clear_messages()

    def query(self, prompt: str, prefix: str = None, stream: bool = False):
        """
        Sends a query to the LLM and returns an object to handle the response.

        Args:
            prompt (str): The input prompt to the LLM.
            stream (bool): Whether to receive the response as a stream.

        Returns:
            AgentResponse: An object that wraps the response from the LLM.
        """
        self._messages.append({"role": "user", "content": prompt})
        
        messages = self._messages.copy()
        
        if prefix is not None:
            messages.append({"role": "assistant", "content": prefix})

        kwargs = {
            "model": self._model_name,
            "stream": stream,
            "messages": messages,
        }
        if self._api_base is not None:
            kwargs["api_base"] = self._api_base
            
        response = litellm.completion(**kwargs)
        return AgentResponse(self, response, stream)

    def get_messages(self) -> list[dict]:
        return self._messages

    def clear_messages(self) -> None:
        """Clears all messages in the conversation."""
        self._messages = [
            {"role": "system", "content": self._system_prompt},
        ]

    def __enter__(self):
        """Called at the beginning of a `with` statement."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called at the end of a `with` statement. No resource cleanup is necessary."""
        pass


class AgentResponse:
    """
    A class to manage the response from the LLM.
    It handles the iteration of streaming responses and holds the final text.
    """
    def __init__(self, agent: "Agent", api_response, stream: bool):
        self._agent = agent
        self._api_response = api_response
        self._stream = stream
        self._full_text = None
        if not stream:
            self._full_text = api_response.choices[0].message.content
            self._agent._messages.append({"role": "assistant", "content": self.output_text})

    def __iter__(self):
        """An iterator that yields response chunks. Used in `for` loops."""
        if self._full_text is not None:
            # If the text has already been generated, return the full text as a single chunk
            yield ResponseChunk(self._full_text)
            return

        if self._stream:
            # Process the API response only if the stream has not been consumed yet
            collected_chunks = []
            for chunk in self._api_response:
                content = chunk['choices'][0]['delta'].content or ""
                collected_chunks.append(content)
                yield ResponseChunk(content)
            self._full_text = "".join(collected_chunks)
            self._agent._messages.append({"role": "assistant", "content": self.output_text})
        else: # For non-streaming cases
            self._full_text = self._api_response.choices[0].message.content
            yield ResponseChunk(self._full_text)
    
    @property
    def output_text(self) -> str:
        """
        Returns the final, complete response text.
        If the stream has not yet been consumed, it is consumed internally to generate the text.
        """
        if self._full_text is None:
            self._full_text = "".join(str(chunk) for chunk in self)

        text = re.sub(r'<think>[\s\S]*?</think>', '', self._full_text).strip()
        
        return text
    
    @property
    def reasoning(self) -> str:
        """
        Returns the text enclosed between <think> and </think> markers.
        Returns empty string if markers are not found.
        """
        # If the reasoning content is available, use it
        if hasattr(self._api_response, 'choices') and hasattr(self._api_response.choices[0].message, 'reasoning_content'):
            return self._api_response.choices[0].message.reasoning_content

        # If not available, try to extract it from the full text
        if self._full_text is None:
            self._full_text = "".join(str(chunk) for chunk in self)

        text = self._full_text
        start = text.find('<think>')
        end = text.find('</think>')
        if start != -1 and end != -1 and end > start:
            return text[start+1:end].strip()
        
        return ""
    

class ResponseChunk:
    """
    A class representing each part (chunk) of a streaming response.
    """
    def __init__(self, content: str):
        self.content = content

    def put(self):
        """
        Writes the chunk's string to standard output.
        """
        sys.stdout.write(self.content)
        sys.stdout.flush()
        
    def get(self):
        """
        Returns the chunk's string.
        """
        return self.content

    def __str__(self):
        """Returns the string of the chunk."""
        return self.content
