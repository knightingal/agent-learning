import json
import os
from pathlib import Path

from langchain_openai import ChatOpenAI

from schemas import ComparisonResult, ExtractionResult
from search import search_local_docs
from state import ResearchState

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

def get_model() -> ChatOpenAI:
  return ChatOpenAI(
    model="Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf",
    api_key="0",  # If you prefer to pass api key in directly
    base_url="http://192.168.2.212:8080/v1"
  )

def search_node(state: ResearchState) -> dict:
  results = search_local_docs(state["query"], top_k=8)
  if not results:
    raise ValueError("No matching local documents were found.")
  return {"search_results": results}

def extract_node(state: ResearchState) -> dict:
  evidence = [
    {
      "source": item["source"],
      "chunk_index": item["chunk_index"],
      "content": item["content"],
    }
    for item in state["search_results"]
  ]

  structured_model = get_model().with_structured_output(ExtractionResult)
  result = structured_model.invoke(
    [
      (
        "system",
        "You extract only explicit facts from supplied evidence. "
        "Do not use outside knowledge. Preserve source file name. "
        "If a dimension is unsupported, return an empty list."
      ),
      (
        "human"
        f"Research question:\n{state['query']}\n\n"
        f"Evidence JSON:\n{json.dumps(evidence, ensure_ascii=False)}"
      ),
    ]
  )
  return {
    "extracted_facts": [item.model_dump() for item in result.technologies]
  }

def compare_node(state: ResearchState) -> dict:
  facts = state["extracted_facts"]
  if len(facts) < 2:
    raise ValueError("At least two technologies are required for comparison.")

  structured_model = get_model().with_structured_output(ComparisonResult)
  result = structured_model.invoke(
    [
      (
        "system",
        "Compare technologies only from the supplied structured facts. "
        "Use  these dimensions: Agent Loop, Workflow, state Management, "
        "Multi-Agent, Complexity, and Bese Use Case."
        "Do not introduce unsupported claims. Mention evidence gaps as caveats."
      ),
      (
        "human"
        f"Question:\n{state['query']}\n\n"
        f"Structured facts:\n{json.dumps(facts, ensure_ascii=False)}"
      ),
    ]
  )

  return {"comparison": result.model_dump()}

def _escape_cell(value: str) -> str:
  return value.replace("|", "\\|").replace("\n", "<br>")
  

def render_markdown(comparison: dict) -> str:
  lines = [
    f"# {comparison['title']}",
    "",
    "## Comparison",
    "",
    f"| Dimension | {comparison['technology_a_name']} | {comparison['technology_b_name']}|",
    "|---|---|---|"
  ]

  for row in comparison["rows"]:
    lines.append(
      "| "
      + " | ".join(
        [
          _escape_cell(row["dimension"]),
          _escape_cell(row["technology_a"]),
          _escape_cell(row["technology_b"]),
        ]
      )
      + " |"
    )

  lines.extend(["", "## Recommendation", "", comparison["recommendation"], ""])
  if comparison["recommendation_reasons"]:
    lines.append("### Reasons")
    lines.append("")
    lines.extend(f"- {item}" for item in comparison["recommendation_reasons"])
    lines.append("")

  if comparison["caveats"]:
    lines.append("### Caveats")
    lines.append("")
    lines.extend(f"- {item}" for item in comparison["caveats"])
    lines.append("")

  lines.append("## Sources")
  lines.append("")
  lines.extend(f"- {item}" for item in sorted(set(comparison["sources"])))
  return "\n".join(lines).rstrip() + "\n"

def report_node(state: ResearchState) -> dict:
  REPORTS_DIR.mkdir(exist_ok=True)
  report = render_markdown(state["comparison"])
  report_path = REPORTS_DIR / "comparison.md"
  report_path.write_text(report, encoding="utf-8")
  return {"report": report, "report_path": str(report_path)}