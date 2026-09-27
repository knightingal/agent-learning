from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.runnables import Runnable
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import IndexConfig
from dataclasses import dataclass
from langchain_openai import ChatOpenAI


model = ChatOpenAI(
  model="Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf",
  api_key="0",  # If you prefer to pass api key in directly
  base_url="http://192.168.2.212:8080/v1"
)

def embed(texts: Sequence[str]) -> list[list[float]]:
  # Replace with an actual embedding function or LangChain embeddings object
  return [[1.0, 2.0] for _ in texts]

store = InMemoryStore(index=IndexConfig(embed=embed, dims=2))
user_id = "my-user"
application_context = "chitchat"
namespace = (user_id, application_context)
store.put(
  namespace,
  "a-memory",
  {
    "rules": [
      "User likes short, direct language",
      "User only speaks English & python",
    ],
    "my-key": "my-value",
  },
)
# get the "memory" by ID
item = store.get(namespace, "a-memory")
print(item)
# search for "memories" within this namespace, filtering on content equivalence, sorted by vector similarity
items = store.search(
  namespace, filter={"my-key": "my-value"}, query="language preferences"
)
print(items)


@dataclass
class Context:
  user_id: str


# InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production use.
store = InMemoryStore()

store.put(
  (
    "users",
  ),  # Namespace to group refrom langchain_openai import ChatOpenAIlated data together (users namespace for user data)
  "user_123",  # Key within the namespace (user ID as key)
  {
    "name": "John Smith",
    "language": "English",
  },  # Data to store for the given user
)


@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
  """Look up user info."""
  # Access the store - same as that provided to `create_agent`
  assert runtime.store is not None
  user_id = runtime.context.user_id
  # Retrieve data from store - returns StoreValue object with value and metadata
  user_info = runtime.store.get(("users",), user_id)
  return str(user_info.value) if user_info else "Unknown user"


agent: Runnable = create_agent(
  model=model,
  tools=[get_user_info],
  # Pass store to agent - enables agent to access store when running tools
  store=store,
  context_schema=Context,
)

# Run the agent
response = agent.invoke(
  {"messages": [{"role": "user", "content": "look up user information"}]},
  context=Context(user_id="user_123"),
)["messages"][-1].content
print(response)