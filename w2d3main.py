import argparse
import os
from dotenv import load_dotenv
from graph import build_graph

def main() -> None:
  load_dotenv()
  parser = argparse.ArgumentParser(description="Search -> Extract -> Compare -> Report")
  parser.add_argument(
    "query",
    nargs="?",
    default="Compare OpenAI agents SDK and langraph for building a Mobile Dev Copilot",
  )
  parser.add_argument("--stream", action="store_true", help="Print each node state update")
  args = parser.parse_args()

  graph = build_graph()
  initial_state = {"query": args.query}

  if args.stream:
    final_state = initial_state
    for state_snapshot in graph.stream(initial_state, stream_mode="values"):
      final_state = state_snapshot
      print("\n=== STATE SNAPSHOT ===")
      print({key: typ(value).__name__ for key, value in state_snapshot.items()})

  else:
    final_state = graph.invoke(initial_state)

  print("\n=== REPORT ===\n")
  print(final_state["report"])
  print(f"Saved to {final_state['report_path']}")

if __name__ == "__main__":
  main()

