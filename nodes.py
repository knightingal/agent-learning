import json
import os
from pathlib import Path

from langchain_openai import ChatOpenAI

from schemas import ComparisonResult, ExtractionResult, QualityAssessment, QueryRewrite
from search import search_local_docs
from state import ResearchState

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
QUALITY_THRESHOLD = 70

def get_model() -> ChatOpenAI:
  return ChatOpenAI(
    model="Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf",
    api_key="0",  # If you prefer to pass api key in directly
    base_url="http://127.0.0.1:8080/v1"
  )

def search_node(state: ResearchState) -> dict:
  query = state.get("active_query", state["query"])
  results = search_local_docs(query, top_k=8)
  if not results:
    raise ValueError("No matching local documents were found.")
  return {"search_results": results}

def extract_node(state: ResearchState) -> dict:
  search_results = state["search_results"]
  if not search_results:
    return {
      "extracted_facts": []
    }
  evidence = [
    {
      "source": item["source"],
      "chunk_index": item["chunk_index"],
      "content": item["content"],
    }
    for item in search_results
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

def quality_node(state: ResearchState) -> dict:
  facts = state["extracted_facts"]

  if len(facts) < 2:
    return {
      "quality": {
        "passed": False,
        "score": 0,
        "missing_dimensions": [],
        "evidence_gaps": [
          "Facts for at least two technologies are required."
        ],
        "retry_query_hint": (
          "Search for both technologies explicitly."
        )
      }
    }
  
  structured_model = get_model().with_structured_output(QualityAssessment)
  result = structured_model.invoke(
    [
      (
        "system",
        "Evaluate whether the supplied facts are sufficient "
        "for a fair technology comparison. "
        "Evaluate these dimensions: Agent Loop, Workflow, "
        "State Management, Multi-Agent, Complexity, "
        "and Best Use Case."
        "Use only supplied facts."
        # f"A score of at least {QUALITY_THRESHOLD} is required to pass."
        "Give a score from 0 to 100 to mark the quality."
        "If evidence is insufficient, explain what is missing "
        "and suggest what the next search should target."
      ), 
      (
        "human",
        f"Research question:\n{state['query']}\n\n"
        f"Structured facts:\n"
        f"{json.dumps(facts, ensure_ascii=False)}"
      )
    ]
  )

  quality = result.model_dump()

  print(quality)

  quality["passed"] = (
    quality["passed"] and quality["score"] >= QUALITY_THRESHOLD
  )

  return {
    "quality": quality
  }

def route_after_quality(state: ResearchState) -> str:
  quality = state["quality"]
  if quality["passed"]:
    return "compare"

  retry_count = state.get("retry_count", 0)
  max_retries = state.get("max_retries", 2)

  if retry_count < max_retries:
    print("go to rewrite")
    return "rewrite"

  print("go to failure")
  return "failure"

def rewrite_query_node(state: ResearchState) -> dict:
  print("enter rewrite_query_node")
  quality = state["quality"]

  previous_query = state.get("active_query", state["query"])
  structured_model = get_model().with_structured_output(QueryRewrite)
  result = structured_model.invoke(
    [
      (
        "system",
        "Rewrite the search query to improve retrieval. "
        "Keep the original comparison goal."
        "Target the missing dimensions and evidence gaps."
        "Return on concise search query."
      ),
      (
        "human",
        f"Original question:\n{state['query']}\n\n"
        f"Previous query:\n{previous_query}\n\n"
        f"Quality assessment:\n"
        f"{json.dumps(quality, ensure_ascii=False)}"
      )
    ]
  )

  new_query = result.rewritten_query
  print("new_query:" + new_query)
  retry_count = state.get("retry_count", 0) + 1
  query_history = [
    *state.get("query_history", []), 
    new_query
  ]

  return {
    "active_query": new_query,
    "retry_count": retry_count,
    "query_history": query_history
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

def failure_report_node(state: ResearchState) -> dict:
  REPORTS_DIR.mkdir(
    exist_ok=True
  )

  quality = state["quality"]
  lines = [
    "# Insufficient Evidence",
    "",
    (
      "The research workflow stopped because "
      "the evidence quality is insufficient."
    ),
    "",
    f"Quality score: {quality['score']}",
    "",
    "## Evidence gaps",
    ""
  ]

  for gap in quality["evidence_gaps"]:
    lines.append(
      f"- {gap}"
    )

  lines.extend(
    [
      "",
      "## Missing dimensions",
      "",
    ]
  )

  for dimension in quality["missing_dimensions"]:
    lines.append(
      f"- {dimension}"
    )


  report = (
    "\n".join(lines).rstrip() + "\n"
  )
  
  report_path = (
    REPORTS_DIR / "insufficient_evidence.md"
  )

  report_path.write_text(report, encoding="utf-8")
  return {
    "report": report,
    "report_path": str(report_path)
  }