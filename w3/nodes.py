import json
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from retriever import HybridRetriever
from w3.schemas import CitedAnswer, EvidenceGrade, SearchPlan
from w3.state import RAGState

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
_retriever: HybridRetriever | None = None

def get_model() -> ChatOpenAI:
  return ChatOpenAI()

def get_retriever() -> HybridRetriever:
  global _retriever
  if _retriever is None:
    _retriever = HybridRetriever()
  return _retriever

def initialize_node(state: RAGState) -> dict:
  model = get_model().with_structured_output(SearchPlan)
  grade = state.get("grade")
  prompt = f"Question:\n{state["question"]}"
  if grade:
    prompt += f"\n\nPrevious evidence grade:\n{json.dumps(grade, ensure_ascii=False)}"
  result = model.invoke([
    ("system", "Create 2 to 4 concise retrieval queries for Android Enterprise documentation. Preserve product names and target distinct aspects. If this is a retry, target the stated missing information."),
    ("human", prompt)
  ])
  queries = list(dict.fromkeys([state["question"], *result.queries]))[:4]
  return {"queries": queries}

def retrieve_node(state: RAGState) -> dict:
  merged: dict[str, dict] = {}
  retriever = get_retriever()
  for query in state["queries"]:
    for item in retriever.search(query, top_k=6):
      chunk_id = item["chunk_id"]
      if chunk_id not in merged or item["rrf_score"] > merged[chunk_id]["rrf_score"]:
        merged[chunk_id] = {**item, "matched_query": query}
  evidence = sorted(merged.values(), key=lambda item: item["rrf_score"], reverse=True)[:10]
  for index, item in enumerate(evidence, start=1):
    item["citation_id"] = f"S{index}"
  return {"evidence": evidence}

def grade_evidence_node(state: RAGState) -> dict:
  if not state.get("evidence"):
    return {"grade": {"sufficient": False, "score": 0, "missing_information":["No evidence retrieved"], "retry_query_hint": "Use exact Android Enterprise product and policy terms."}}
  compact = [{"citation_id": x["citation_id"], "source": x["source"], "content":x["content"]} for x in state['evidence']]
  model = get_model().with_structured_output(EvidenceGrade)
  result = model.invoke([
    ("system", "Grade whether the supplied evidence can answer the question without outside knowledge. Score 0-100. sufficient may be the true only at score >= 75 and when the answer can be cited directly."),
    ("human", f"Question:\n{state['question']}\n\nEvidence:\n{json.dumps(compact, ensure_ascii=False)}"),
  ])
  grade = result.model_dump()
  grade["sufficient"] = bool(grade["sufficient"] and grade["score"] >= 75)
  return {"grade": grade}
