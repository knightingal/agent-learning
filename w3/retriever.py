import json
import os
import re
from pathlib import Path
import numpy as np
from openai import OpenAI
from rank_bm25 import BM25Okapi

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR/"index"/"chunks.json"

def tokenize(text: str) -> list[str]:
    """Simple tokenizer for English identifiers and CJK text."""
    return re.findall(r"[a-zA-Z_][a-zA-Z0-9_.-]*|[\u4e00-\u9fff]+", text.lower())

def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
  scores: dict[str, float] = {}
  for ranking in rankings:
    for rank, chunk_id in enumerate(ranking, start=1):
      scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
  return scores

class HybridRetriever:
  def __init__(self):
    if not INDEX_FILE.exists():
      raise RuntimeError("Index missing, Run: python ingest.py")
    self.documents = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    self.by_id = {item["chunk_id"]: item for item in self.documents}
    self.bm25 = BM25Okapi([tokenize(item["content"]) for item in self.documents])
    self.matrix = np.asarray([item["embedding"] for item in self.documents], dtype=np.float32)
    self.matrix /= np.linalg.norm(self.matrix, axis=1, keepdims=True).clip(min=1e-12)
    self.client = OpenAI()
    self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

  def _vector_search(self, query: str, top_k: int) -> list[str]:
    response = self.client.embeddings.create(model=self.embedding_model, input=[query])
    vector = np.asarray(response.data[0].embedding, dtype=np.float32)
    vector /= max(np.linalg.norm(vector), 1e-12)
    scores = self.matrix @ vector
    indices = np.argsort(-scores)[:top_k]
    return [self.documents[int(index)]["chunk_id"] for index in indices]

  def _keyword_search(self, query: str, top_k: int) -> list[str]:
    scores = self.bm25.get_scores(tokenize(query))
    indices = np.argsort(-scores)[:top_k]
    return [self.documents[int(index)]["chunk_id"] for index in indices if scores[int(index)] > 0]

  def search(self, query: str, top_k:int = 6) -> list[dict]:
    candidate_k = max(top_k * 3, 12)
    keyword_ids = self._keyword_search(query, candidate_k)
    vector_ids = self._vector_search(query, candidate_k)
    fused = reciprocal_rank_fusion([keyword_ids, vector_ids])
    ranked = sorted(fused.items(), key=lambda item: item[1], reverse=True)[:top_k]
    return [{**self.by_id[chunk_id], "rrf_score": score} for chunk_id, score in ranked]