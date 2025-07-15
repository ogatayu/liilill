import os
from liilill import Agent

os.environ["OPENAI_API_KEY"] = "your-api-key"

try:
    with Agent(model_name="openai/gpt-4o") as agent:
        print("### Streaming Response")
        response = agent.query("Tell me a short story about a robot who discovers human.", stream=True)

        for chunk in response:
            chunk.put()

        print("\n\n### Final Output")
        print(response.output_text)

except Exception as e:
    print(f"\nAn error occurred: {e}")
