from typing import TypedDict

class RAGState(TypedDict, total=False):
  question: str
  queries: list[str]
  evidence: list[dict]
  grade: dict
  retry_count: int
  max_retries: int
  answer: str
  citations: list[str]
  report_path: str