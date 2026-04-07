from dotenv import load_dotenv
from openai import OpenAI
import os


def call_llm(messages):
    load_dotenv()

    client = OpenAI(
        base_url="http://192.168.50.50:5002/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        model="any-string-works-here", # Kobold just uses whatever GGUF is currently loaded
        messages=messages,
        temperature=0.9,
    )
    print(response)
    return response.choices[0].message.content


if __name__ == "__main__":
    # Test the LLM call
    messages = [{"role": "user", "content": "Write a C++ function that adds two numbers."}]
    response = call_llm(messages)
    print(f"Prompt: {messages[0]['content']}")
    print(f"Response: {response}")
