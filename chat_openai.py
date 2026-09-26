from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf",
    api_key="0",  # If you prefer to pass api key in directly
    base_url="http://192.168.2.212:8080/v1"
)

messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]

ai_msg = llm.invoke(messages)
print(ai_msg.text)