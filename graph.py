from langgraph.graph import END, START, StateGraph

from state import ResearchState
from nodes import compare_node, extract_node, report_node, search_node

def build_graph():
  builder = StateGraph(ResearchState)
  builder.add_node("search", search_node)
  builder.add_node("extract", extract_node)
  builder.add_node("compare", compare_node)
  builder.add_node("report", report_node)

  builder.add_edge(START, "search")
  builder.add_edge("search", "extract")
  builder.add_edge("extract", "compare")
  builder.add_edge("compare", "report")
  builder.add_edge("report", END)
  return builder.compile()