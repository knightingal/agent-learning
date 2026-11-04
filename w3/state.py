from typing import TypedDict

class RAGState(TypedDict, total=Flase):
  question: str
  queries: list[str]
  evidence: list[dict]
  grade: dict
  retry_count: int
  max_retries: int
  answer: str
  citations: list[str]
  report_path: str