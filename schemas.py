from pydantic import BaseModel, Field

class TechnologyFacts(BaseModel):
  name: str = Field(description="Technology or framework name")
  summary: str = Field(description="Short factual summary")
  agent_loop: list[str] = Field(default_factory=list)
  workflow: list[str] = Field(default_factory=list)
  state_management: list[str] = Field(default_factory=list)
  multi_agent: list[str] = Field(default_factory=list)
  complexity: list[str] = Field(default_factory=list)
  best_use_cases: list[str] = Field(default_factory=list)
  limitations: list[str] = Field(default_factory=list)
  sources: list[str] = Field(default_factory=list)

class ExtractionResult(BaseModel):
  technologies: list[TechnologyFacts]

class ComparisonRow(BaseModel):
  dimension: str
  technology_a: str
  technology_b: str

class ComparisonResult(BaseModel):
  title: str
  technology_a_name: str
  technology_b_name: str
  rows: list[ComparisonRow]
  recommendation: str
  recommendation_reasons: list[str]
  caveats: list[str]
  sources: list[str]