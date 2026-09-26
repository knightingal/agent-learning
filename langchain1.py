from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

model = ChatOpenAI(
  model="Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf",
  api_key="0",  # If you prefer to pass api key in directly
  base_url="http://192.168.2.212:8080/v1"
)

agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in Nanjing?"}]}
)
print(result["messages"][-1].content_blocks)