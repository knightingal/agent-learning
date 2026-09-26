from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  

from langchain_openai import ChatOpenAI


def get_user_info() -> str:
    """Look up information about the current user."""
    return "No user profile on file."


model = ChatOpenAI(
  model="Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf",
  api_key="0",  # If you prefer to pass api key in directly
  base_url="http://192.168.2.212:8080/v1"
)

agent = create_agent(
    model=model,
    tools=[get_user_info],
    checkpointer=InMemorySaver()
)

thread_config = {"configurable": {"thread_id": "1"}}
response = agent.invoke(
    {"messages": [{"role": "user", "content": "Hi! My name is Bob."}]},
    thread_config,
)["messages"][-1].content

print(response)  # "Hi Bob! Nice to see you here. How are you doing?"

response = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    thread_config,
)["messages"][-1].content

print(response)  # "You are Bob!"

response = agent.invoke(
    {"messages": [{"role": "user", "content": "Do you remember me?"}]},
    thread_config,
)["messages"][-1].content
print(response)  # "You are Bob!"