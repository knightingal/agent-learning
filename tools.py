from pathlib import Path
import re
from agents import function_tool

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

def tokenize(text: str) -> list[str]:
    """Simple tokenizer for English identifiers and CJK text."""
    return re.findall(r"[a-zA-Z_][a-zA-Z0-9_.-]*|[\u4e00-\u9fff]+", text.lower())

def split_chunks(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """Split text into overlapping character chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap
    return chunks

def score_chunk(query: str, text: str) -> int:
    """Unnormalized keyword-count score."""
    query_terms = tokenize(query)
    text_lower = text.lower()
    return sum(text_lower.count(term) for term in query_terms if term)

def local_search(query: str, top_k: int = 3) -> list[dict]:
    """Search Markdown files and return ranked chunks."""
    query = query.strip()
    if not query:
        return []
    if not KNOWLEDGE_DIR.exists():
        raise FileNotFoundError(f"Knowledge directory not found: {KNOWLEDGE_DIR}")

    results = []
    for file_path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        for index, chunk in enumerate(split_chunks(content)):
            score = score_chunk(query, chunk)
            if score > 0:
                results.append({
                    "source": file_path.name,
                    "chunk_index": index,
                    "score": score,
                    "content": chunk,
                })

    results.sort(key=lambda item: (-item["score"], item["source"], item["chunk_index"]))
    return results[:max(1, min(top_k, 10))]

@function_tool
def search_docs(query: str, top_k: int = 3) -> str:
    """Search the local Android knowledge base for evidence relevant to the question."""
    try:
        results = local_search(query=query, top_k=top_k)
    except Exception as exc:
        return f"Knowledge search failed: {type(exc).__name__}: {exc}"

    if not results:
        return "No relevant evidence was found in the local knowledge base."

    sections = []
    for item in results:
        sections.append(
            f"[Source: {item['source']} | Chunk: {item['chunk_index']} | Score: {item['score']}]\n"
            f"{item['content']}"
        )
    return "\n\n---\n\n".join(sections)
