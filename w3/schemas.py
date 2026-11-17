from pydantic import BaseModel, Field

class SearchPlan(BaseModel):
  queries: list[str]
  rationale: str

class EvidenceGrade(BaseModel):
  sufficient: bool
  score: int = Field(ge=0, le=100)
  missing_information: list[str] = Field(default_factory=list)
  retry_query_hint: str = ""

class CitedAnswer(BaseModel):
  answer: str
  citations: list[str] = Field(default_factory=list)
  limitations: list[str] = Field(default_factory=list)