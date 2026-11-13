import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

@dataclass
class Harness:
  root: Path
  workspace: Path  = field(init=False)
  reports: Path = field(init=False)
  trace_file: Path = field(init=False)

  def __post_init__(self) -> None:
    self.workspace = (self.root / "workspace").resolve()
    self.reports = (self.root / "reports").resolve()
    self.workspace.mkdir(exist_ok=True)
    self.reports.mkdir(exist_ok=True)
    self.trace_file = self.reports / "trace.jsonl"

  def trace(self, event: str, payload: dict) -> None:
    record = {
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "event": event,
      "payload": payload
    }
    with self.trace_file.open("a", encoding="utf-8") as handle:
      handle.write(json.dumps(record, ensure_ascii=False) + "\n")

  def safe_path(self, relative_path: str) -> Path:
    target = (self.workspace / relative_path).resolve()
    if target != self.workspace and self.workspace not in target.parents:
      raise PermissionError(f"Path escapes workspace: {relative_path}")
    return target

  def read_workspace_snapshot(self, max_files: int = 30, max_chars: int = 30000) -> str:
    parts: list[str] = []
    total = 0
    ignored = {".git", ".venv", "build", ".gradle", "node_modules", "__pychche__"}
    for path in sorted(self.workspace.rglob("*")):
      if not path.is_file() or any(part in ignored for part in path.parts):
        continue
      relative = path.relative_to(self.workspace).as_posix()
      try:
        content = path.read_text(encoding="utf-8")
      except UnicodeDecodeError:
        continue
      block = f"\n--- FILE: {relative} ---\n{content}\n"
      if len(parts) >= max_files or total + len(block) > max_chars:
        break
      parts.append(block)
      total += len(block)
    return "".join(parts) or "(workspace is empty)"

  def apply_files(self, files: list[dict]) -> list[str]:
    applied: list[str] = []
    for item in files:
      target = self.safe_path(item["path"])
      target.parent.mkdir(parents=True, exist_ok=True)
      target.write_text(item["content"], encoding="utf-8")
      applied.append(target.relative_to(self.workspace).as_posix())
    self.trace("file_applied", {"file": applied})
    return applied

  def file_hashes(self, paths: list[str]) -> dict[str, str]:
    result = {}
    for relative in paths:
      target = self.safe_path(relative)
      if target.exists():
        result[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    return result
