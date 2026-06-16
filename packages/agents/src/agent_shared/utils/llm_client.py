import os

from dotenv import load_dotenv
from openai import OpenAI


def call_llm(prompt):
    load_dotenv()
    client = OpenAI(
        base_url="http://192.168.50.50:5002/v1", api_key=os.getenv("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        model="any-string-works-here",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("## Testing call_llm")
    prompt = "In a few words, what is the meaning of life?"
    print(f"## Prompt: {prompt}")
    response = call_llm(prompt)
    print(f"## Response: {response}")
