from dotenv import load_dotenv
from openai import OpenAI
import os


def call_llm(messages):
    load_dotenv()
    openai_key = os.getenv("OPENAI_KEY")
    client = OpenAI(api_key=openai_key)

    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=messages,
        temperature=1
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # Test the LLM call
    messages = [{"role": "user", "content": "In a few words, what's the meaning of life?"}]
    response = call_llm(messages)
    print(f"Prompt: {messages[0]['content']}")
    print(f"Response: {response}")
