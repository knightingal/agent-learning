from pathlib import Path
import hashlib
import re

def split_markdown(text: str, chunk_size: int = 1200, overlap: int = 100) -> list[str]:
  sections = re.split(r"(?m)(?=^#{1,3}\s)", text)
  chunks: list[str] = []
  for section in sections:
    section = section.strip()
    if not section:
      continue
    start = 0
    while start < len(section):
      end = min(start + chunk_size, len(section))
      value = section[start: end].strip()
      if value:
        chunks.append(value)
      if end == len(section):
        break
      start = end - overlap
  return chunks

def load_chunks(knowledge_dir: Path) -> list[dict]:
  records = []
  for path in sorted(knowledge_dir.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    source_url = ""
    for line in text.splitlines()[:20]:
      if line.lower().startswith("source_url:"):
        source_url = line.split(":", 1)[1].strip()
      for index, content in enumerate(split_markdown(text)):
        raw_id = f"{path.name}:{index}:{content}"
        chunk_id = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16]
        records.append({
          "chunk_id": chunk_id,
          "source": path.name,
          "source_url": source_url,
          "chunk_index": index,
          "content": content
        })
  return records
