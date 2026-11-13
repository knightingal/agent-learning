import argparse
import os
import uuid
from dotenv import load_dotenv
from langgraph.types import Command
from copilot import build_graph
from agents import set_tracing_disabled

set_tracing_disabled(True)


def main() -> None:
  load_dotenv()
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "request",
    nargs="?",
    defautl="Create a small Kotlin utiliy that validates an Android Enterprise enrollment token format and add tests."
  )
  parser.add_argument("--max-iterations", type=int, default=1)
  args = parser.parse_args()

  if not os.getenv("OPENAN_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")
  
  graph = build_graph()
  thread_id = str(uuid.uuid4())
  config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 40}
  result = graph.invoke(
    {"request": args.request, "max_iterations": args.max_iterations},
    config=config,
  )

  while "__interrupt__" in result:
    interrupt_value = result["__interrupt__"][0].value
    print("\nApproval required:\n")
    print(interrupt_value)
    choice = input("Approve file writes? [y/N]: ").strip().lower()
    decision = {"decision":"approve" if choice == "y" else "reject"}
    result = graph.invoke(Command(resume=decision), config=config)

  print("\n" + result["final_report"])
  print("\nReport:", result["report_path"])


if __name__ == "__main__":
  main()