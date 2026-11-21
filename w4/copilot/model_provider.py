import os

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_deepseek import ChatDeepSeek

def create_chat_model() -> BaseChatModel:
  return create_deepseek_model()

def create_deepseek_model() -> ChatDeepSeek:
  return ChatDeepSeek(
    model="deepseek-v4-pro",
    api_key="key1",
    temperature=0,
    timeout=120,
    max_retries=2,
    extra_body={"thinking": {"type": "disabled"}}
  )

def structured_output_method() -> str:
  return "function_calling"


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