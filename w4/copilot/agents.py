import os
from agents import Agent
from .schemas import CodingResult, ImplementationPlan, ResearchResult, ReviewResult
from .model_provider import create_model

def build_agints():
  model = create_model()

  planner = Agent(
    name="Mobile Planner",
    model=model,
    instructions=(
      "You are a senior mobile architect. Convert the request into a small, testable "
      "implementation plan. Prefer minimal changes, explicit dependencies, acceptance "
      "criteria, and concrete mobile security risks. Do not write code."
    ),
    output_type=ImplementationPlan,
  )

  researcher = Agent(
    name="Mobile Researcher",
    model=model,
    instructions=(
      "You are an evidence-grounded mobile platform researcher. Use only the supplied "
      "knowledge excerpts and workspace snapshot. Every factual finding must name its "
      "source. Mark evidence_sufficient false when the material does noat support the plan."
    ),
    output_type=ResearchResult
  )

  coder = Agent(
    name="Mobile Coder",
    model=model,
    instructions=(
      "You are a mobile implementation specialist. Produce complete file contents, not "
      "diff fragments. Stay inside the workspace, make the smallest coherent change, "
      "and never propose destructive shell commands, credential changes, git push, or "
      "network side effects. Include safe verification commands only."
    ),
    output_type=CodingResult,
  )

  reviewer = Agent(
    name="Mobile Reviewer",
    model=model,
    instructions=(
      "You are an independent mobile reviewer. Review only the supplied plan, evidence, "
      "and resulting files. Check correctness, architecture, Android/iOS lifecycle, "
      "security, privacy, performance, and testability. Approve only when no high-severity "
      "issue remains. Do not invent unseen code."
    ),
    output_type=ReviewResult,
  )
  return planner, researcher, coder, reviewer
