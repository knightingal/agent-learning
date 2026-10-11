import asyncio
import os

from agents import Agent, Runner, Model, RunConfig
from tools import search_docs
from openai_agents_providers import LlamaCppProvider

provider = LlamaCppProvider(
    base_url="http://192.168.2.212:8080/v1",
    model="Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf",
    api_key="0",
)

def build_agent() -> Agent:
    return Agent(
        name="Android FAQ Agent",
        tools=[search_docs],
        instructions="""
You are an Android development documentation assistant.

Rules:
1. For every technical question, call search_docs before answering.
2. Answer only from the evidence returned by search_docs.
3. Cite source file names in the final answer.
4. If evidence is insufficient, say exactly:
   "I cannot find sufficient evidence in the local knowledge base."
5. Do not claim to execute Gradle, Shell, Git, or modify project files.
6. Keep the answer concise and distinguish documented facts from suggestions.
""".strip(),
    )

async def chat() -> None:
    # if not os.getenv("OPENAI_API_KEY"):
    #     raise RuntimeError("OPENAI_API_KEY is not set")

    agent = build_agent()
    print("Android FAQ Agent")
    print("Type 'exit' or 'quit' to stop.")

    conversation = []
    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break

        conversation.append({"role": "user", "content": user_input})
        result = await Runner.run(agent, conversation, run_config=RunConfig(model_provider=provider))
        answer = result.final_output
        print(f"\nAgent: {answer}")

        # Preserve the SDK-normalized history for the next turn.
        conversation = result.to_input_list()

if __name__ == "__main__":
    asyncio.run(chat())
