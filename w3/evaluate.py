import json
from pathlib import Path
from graph import build_graph

BASE = Path(__file__).resolve().parent

def main():
  cases = [json.loads(line) for line in (BASE / "eval" / "questions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
  graph = build_graph()
  results = []
  for case in cases:
    state = graph.invoke({"question": case['question'], "max_retries": 1}, config={"recursion_limit": 20})
    answer = state["answer"].lower()
    terms = case.get("expected_terms", [])
    hit = sum(1 for term in terms if term.lower() in answer)
    results.append({
      "question": case['question'],
      "term_recall": hit/max(len(terms), 1),
      "grade": state.get("grade",{}).get("score", 0),
      "citations": state.get("citations",[])
    })
  out = BASE/"reports"/"evaluation.json"
  out.parent.mkdir(exist_ok=True)
  out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
  print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
  main()