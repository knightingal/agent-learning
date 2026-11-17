import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from chunking import load_chunks


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
INDEX_FILE = BASE_DIR/"index"/"chunks.json"

def batch(items: list[str], size: int = 64):
  for start in range(0, len(items), size):
    yield items[start:start + size]

def build_index() -> None:
  load_dotenv()
  chunks = load_chunks(KNOWLEDGE_DIR)

  client = OpenAI(
    base_url="http://127.0.0.1:8080/v1",
    api_key="0"
  )
  embeddings: list[list[float]] = []
  contents = [item["content"] for item in chunks]
  for group in batch(contents):
    response = client.embeddings.create(model="nomic-embed-text-v1.5.f16.gguf", input=group)
    embeddings.extend(item.embedding for item in response.data)
  
  for item, vector in zip(chunks, embeddings):
    item['embedding'] = vector

  INDEX_FILE.parent.mkdir(exist_ok=True)
  INDEX_FILE.write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
  print(f"Indexed {len(chunks)} chunks -> {INDEX_FILE}")

if __name__ == "__main__":
  build_index()




