import json

from openai import OpenAI
import os
import json

def stream_llm(prompt):
    client = OpenAI(
        base_url="http://192.168.50.50:5002/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )


    # Make a streaming chat completion request
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        stream=True  # Enable streaming
    )
    return response


if __name__ == "__main__":
    print("## Testing streaming LLM")
    prompt = "What's the meaning of life?"
    print(f"## Prompt: {prompt}")
    response = stream_llm(prompt)
    first_chunk = next(response)
    print(json.dumps(first_chunk.model_dump(), indent=2))
    print(response)
    print(f"## Response: ")
    for chunk in response:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
            chunk_content = chunk.choices[0].delta.content
            # Print the incoming text without a newline (simulate real-time streaming)
            # print(chunk_content, end="", flush=True)

