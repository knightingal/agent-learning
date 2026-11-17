import os

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

def create_model():
  provider = "deepseek"
  if provider == "deepseek":
    client = AsyncOpenAI(
      base_url="https://api.deepseek.com",
      api_key=os.environ["DEEPSEEK_API_KEY"]
    )

    return OpenAIChatCompletionsModel(
      model="deepseek-v4-pro",
      openai_client=client
    )

  else:
    client = AsyncOpenAI(
      base_url="https://localhost:8080/v1",
      api_key="1"
    )

    return OpenAIChatCompletionsModel(
      model=os.getenv("MODEL_NAME", "qwen3:8b"),
      openai_client=client
    )