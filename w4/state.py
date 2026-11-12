from typing import TypedDict

class CopilotState(TypedDict, total=False):
  request: str
  plan: str
  research: dict
  coding: dict
  approval: dict
  applied_files: list[str]
  verification: dict
  review: dict
  iteration: int
  max_iterations: int
  final_report: str
  report_path: str