import argparse
import os
from dotenv import load_dotenv
from w3.graph import build_grade

def main():
  load_dotenv()
  parser = argparse.ArgumentParser()
  parser.add_argument("quesiont", nargs="?", default="What is the difference between a work profile and a fully managed device?")
  parser.add_argument("--max-retries", type=int, default=2)
  parser.add_argument("--stream", action="store_true")
  args = parser.parse_args()

  graph = build_grade()
  initial = {"question": args.question, "max_retries": args.max_retries}
  final = initial
  if args.stream:
    for final in graph.stream(initial, stream_mode="values", config={"recursion_limit": 30}):
      print({"queries": final("queries"), "retry_count": final.get("retry_count"), "grade": final.get("grade")})
  else:
    final = graph.invoke(initial, config={"recursion_limit": 30})

  print("\n" + final["answer"])
  print("Report" + final["report_path"])

if __name__ == "__main__":
  main()
