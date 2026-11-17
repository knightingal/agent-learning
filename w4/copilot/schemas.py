from pydantic import BaseModel, Field

class TaskItem(BaseModel):
  id: str
  title: str
  description: str
  dependencies: list[str] = Field(default_factory=list)
  acceptance_criteria: list[str] = Field(default_factory=list)

class ImplementationPlan(BaseModel):
  goal: str
  assumptions: list[str] = Field(default_factory=list)
  tasks: list[TaskItem]
  risks: list[str] = Field(default_factory=list)

class ResearchFinding(BaseModel):
  clain: str
  evidence: str
  source: str

class ResearchResult(BaseModel):
  summary: str
  findings: list[ResearchFinding] = Field(default_factory=list)
  constraints: list[str] = Field(default_factory=list)
  evidence_sufficient: bool

class FileChange(BaseModel):
  path: str
  purpose: str
  content: str

class CodingResult(BaseModel):
  summary: str
  files: list[FileChange]
  verification_commands: list[str] = Field(default_factory=list)
  notes: list[str] = Field(default_factory=list)

class ReviewIssue(BaseModel):
  severity: str
  category: str
  file: str
  description: str
  recommendation: str

class ReviewResult(BaseModel):
  approved: bool
  summary: str
  issues: list[ReviewIssue] = Field(default_factory=list)
  required_fixes: list[str] = Field(default_factory=list)