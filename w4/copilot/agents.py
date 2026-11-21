import os
from dataclasses import dataclass
from typing import Generic, TypeVar

from langchain_core.language_models.chat_models import (
  BaseChatModel
)

from pydantic import BaseModel

from .schemas import CodingResult, ImplementationPlan, ResearchResult, ReviewResult
from .model_provider import (create_chat_model, structured_output_method)

OutputT = TypeVar(
  "OutputT",
  bound=BaseModel,
)

@dataclass
class StructuredAgent(
  Generic[OutputT],
): 
  name: str
  instructions: str
  output_schema: type[OutputT]
  model: BaseChatModel

  def run(self, prompt: str) -> OutputT:
    structured_model = (
      self.model.with_structured_output(self.output_schema, method=(structured_output_method()), include_raw=False)
    )

    result = structured_model.invoke([
      ("system", self.instructions),
      ("human", prompt),
    ])

    if not isinstance(result, self.output_schema):
      result = (self.output_schema.model_validate(result))
    return result
    

def build_agents():
  model = create_chat_model()

  planner = StructuredAgent(
    name="Mobile Planner",
    model=model,
    output_schema=ImplementationPlan,
    instructions="""
You are a senior mobile architect. 

Convert the request into a small, 
testable implementation plan. 

Rules:

1. Prefer minimal changes, 
2. Define explicit dependencies, 
3. Define acceptance criteria, 
4. Identify mobile security risks. 
5. Do not write code.
""".strip(),
  )


  researcher = StructuredAgent(
    name="Mobile Researcher",
    model=model,
    output_schema=ResearchResult,
    instructions="""
You are an evidence-grounded mobile platform researcher. 

Rules:

1. Use only the supplied knowledge excerpts and workspace snapshot. 
2. Every factual finding must name its source. 
3. Do not use unstated model knowledge.
4. Set evidence_sufficient to false when the evidence does noat support the imlementaion plan.
""".strip()
  )

  coder = StructuredAgent(
    name="Mobile Coder",
    model=model,
    output_schema=CodingResult,
    instructions="""
You are a mobile implementation specialist. 

Rules:

1. Produce complete file contents, not partial diff fragments. 
2. Stay inside the workspace.
3. make the smallest coherent change.
4. Never propose destructive commands. 
5. Do not expose credentials. 
6. Include safe verification commands.
""".strip()
  )

  reviewer = StructuredAgent(
    name="Mobile Reviewer",
    model=model,
    output_schema=ReviewResult,
    instructions="""
You are an independent mobile reviewer. 

Review only the supplied plan, evidence, generated files, and test output. 

Check:

- correctness
- architecture
- lifecycle
- security
- privacy
- performance
- testability

Approve only when no blocking issue remains. 
Do not invent unseen code."
""".strip()
  )
  return planner, researcher, coder, reviewer
