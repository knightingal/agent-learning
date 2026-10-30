from langgraph.graph import END, START, StateGraph
from typing import Literal

from state import ResearchState
from nodes import compare_node, extract_node, report_node, search_node, failure_report_node, quality_node, rewrite_query_node, route_after_quality

QualityRoute = Literal[
  "compare",
  "rewrite",
  "failure"
]

def quality_router(
  state: ResearchState
) -> QualityRoute:
  return route_after_quality(state)

def build_graph():
  builder = StateGraph(ResearchState)
  builder.add_node("search", search_node)
  builder.add_node("extract", extract_node)
  builder.add_node("quality", quality_node)
  builder.add_node("rewrite", rewrite_query_node)
  
  builder.add_node("compare", compare_node)
  builder.add_node("report", report_node)

  builder.add_node("failure", failure_report_node)


  builder.add_edge(START, "search")
  builder.add_edge("search", "extract")
  builder.add_edge("extract", "quality")
  builder.add_conditional_edges("quality", quality_router,{
    "compare":"compare",
    "rewrite":"rewrite",
    "failure":"failure"

  })
  builder.add_edge("rewrite", "search")
  builder.add_edge("compare", "report")
  builder.add_edge("report", END)
  builder.add_edge("failure", END)
  return builder.compile()