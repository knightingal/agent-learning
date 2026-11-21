import re
from pathlib import Path


def tokenize(text: str) -> list[str]:
    """Simple tokenizer for English identifiers and CJK text."""
    print(text)
    return re.findall(r"[a-zA-Z_][a-zA-Z0-9_.-]*|[\u4e00-\u9fff]+", text.lower())


def search_knowledge(root: Path, query: str, top_k: int = 8) -> list[dict]:
    """Search Markdown files and return ranked chunks."""
    terms = tokenize(query)
    results = []

    for path in sorted((root / "knowledge").glob("*.md")):
        content = path.read_text(encoding="utf-8")
        score = sum(content.lower().count(term) for term in terms if len(term) > 1)
        if score > 0:
          results.append({
            "source": path.name,
            "score": score,
            "content": content[:5000],
          })
    return sorted(results, key=lambda item: -item["score"])[:top_k]
