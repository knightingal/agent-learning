from typing import Literal
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from .nodes import (
  apply_node,
  approval_node,
  code_node,
  finalize_node,
  initialize_node,
  plan_node,
  reject_node,
  research_node,
  review_node,
  revise_node,
  route_after_approval,
  route_after_review,
  verify_node,
)
from .state import CopilotState

ApprovalRoute = Literal["apply", "reject"]
ReviewRoute = Literal["finalize", "revise"]


def approval_router(state: CopilotState) -> ApprovalRoute:
  return route_after_approval(state)


def review_router(state: CopilotState) -> ReviewRoute:
  return route_after_review(state)


def build_graph():
  graph = StateGraph(CopilotState)

  graph.add_node("initialize", initialize_node)
  graph.add_node("plan", plan_node)
  graph.add_node("research", research_node)
  graph.add_node("code", code_node)
  graph.add_node("approval", approval_node)
  graph.add_node("apply", apply_node)
  graph.add_node("reject", reject_node)
  graph.add_node("verify", verify_node)
  graph.add_node("review", review_node)
  graph.add_node("revise", revise_node)
  graph.add_node("finalize", finalize_node)

  graph.add_edge(START, "initialize")
  graph.add_edge("initialize", "plan")
  graph.add_edge("plan", "research")
  graph.add_edge("research", "code")
  graph.add_edge("code", "approval")

  graph.add_conditional_edges(
    "approval",
    approval_router,
    {"apply": "apply", "reject": "reject"},
  )

  graph.add_edge("apply", "verify")
  graph.add_edge("verify", "review")
  graph.add_conditional_edges(
    "review",
    review_router,
    {"finalize":"finalize", "revise":"revise"},
  )
  graph.add_edge("revise", "code")
  graph.add_edge("reject", "finalize")
  graph.add_edge("finalize", END)

  return graph.compile(checkpointer=InMemorySaver())
