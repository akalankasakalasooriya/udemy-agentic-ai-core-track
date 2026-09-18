from pathlib import Path

from dotenv import load_dotenv
from openai import AzureOpenAI
import os

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

model = os.getenv("GPT_MODEL", "gpt-4o")

client = AzureOpenAI(
    api_key=os.getenv("GPT_KEY"),
    api_version=os.getenv("GPT_API_VERSION"),
    azure_endpoint=os.getenv("GPT_ENDPOINT"),
)


def call_llm(messages, json_mode=False):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"} if json_mode else {"type": "text"},
        timeout=120.0,
    )
    return response.choices[0].message.content
