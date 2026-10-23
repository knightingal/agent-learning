from typing import TypedDict

class ResearchState(TypedDict, total=False):
  query: str
  search_results: list[dict]
  extracted_facts: list[dict]
  comparison: dict
  report: str
  report_path: str