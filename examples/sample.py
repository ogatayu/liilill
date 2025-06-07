import os
from liilill import Agent

os.environ["OPENAI_API_KEY"] = "your-api-key"

with Agent(model_name="openai/gpt-4.1-nano") as agent:
    prompt = "日本の首都について、100文字程度で簡潔に教えてください。"
    
    print("--- Streaming output ---")
    response = agent.query(prompt, stream=True)

    for chunk in response:
        chunk.put()

    print("\n\n--- Result ---")
    print(response.output_text)
