from typing import Literal
from langgraph.graph import StateGraph, END, START
from w3.nodes import answer_node, grade_evidence_node, initialize_node, plan_queries_node, refuse_node, report_node, retrieve_node, retry_node, route_after_grade
from w3.state import RAGState

GradeRoute = Literal["answer", "retry", "refuse" ]

def grade_router(state: RAGState) -> GradeRoute:
  return route_after_grade(state)

def build_grade():
  graph = StateGraph(RAGState)
  graph.add_node("initialize", initialize_node)
  graph.add_node("plan_queries", plan_queries_node)
  graph.add_node("retrieve", retrieve_node)
  graph.add_node("grade_evidence", grade_evidence_node)
  graph.add_node("retry", retry_node)
  graph.add_node("answer", answer_node)
  graph.add_node("refuse", refuse_node)
  graph.add_node("report", report_node)

  graph.add_edge(START, "initialize")
  graph.add_edge("initialize", "plan_queries")
  graph.add_edge("plan_queries", "retrieve")
  graph.add_edge("retrieve", "grade_evidence")
  graph.add_conditional_edges("grade_evidence", grade_router, {"answer":"answer", "retry":"retry", "refuse":"refuse"})
  graph.add_edge("retry", "plan_queries")
  graph.add_edge("answer", "report")
  graph.add_edge("refuse", "refuse")
  graph.add_edge("report", END)
  return graph.compile()