from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"


def tokenize(text: str) -> list[str]:
    """Simple tokenizer for English identifiers and CJK text."""
    return re.findall(r"[a-zA-Z_][a-zA-Z0-9_.-]*|[\u4e00-\u9fff]+", text.lower())


def score(query: str, text: str) -> int:
    """Unnormalized keyword-count score."""
    query_terms = tokenize(query)
    text_lower = text.lower()
    return sum(text_lower.count(term) for term in query_terms if term)

def split_markdown(text: str, max_chars: int = 1800) -> list[str]:
  sections = re.split(r"(?m)(?=^#{1,3}\s)", text)
  chunks: list[str] = []
  for section in sections:
    section = section.strip()
    if not section:
      continue
    if len(section) <= max_chars:
      chunks.append(section)
      continue
    for start in range(0, len(section), max_chars):
      chunks.append(section[start: start + max_chars].strip())
  return chunks


def search_local_docs(query: str, top_k: int = 8) -> list[dict]:
    """Search Markdown files and return ranked chunks."""
    query = query.strip()
    if not query:
        return []
    if not KNOWLEDGE_DIR.exists():
        raise FileNotFoundError(f"Knowledge directory not found: {KNOWLEDGE_DIR}")

    results = []
    for file_path in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        content = file_path.read_text(encoding="utf-8")
        for index, chunk in enumerate(split_chunks(content)):
            chunk_score = score(query, chunk)
            if chunk_score > 0:
                results.append({
                    "source": file_path.name,
                    "chunk_index": index,
                    "score": chunk_score,
                    "content": chunk,
                })

    results.sort(key=lambda item: (-item["score"], item["source"], item["chunk_index"]))
    return results[:top_k]