import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class PolicyRAGEngine:
    """RAG Engine for indexing and semantic search over NorthStar Retail policies."""
    def __init__(self, policy_json_path: Path):
        self.policy_path = Path(policy_json_path)
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = None
        self._load_and_index()

    def _load_and_index(self):
        if not self.policy_path.exists():
            return
        
        with open(self.policy_path, "r", encoding="utf-8") as f:
            docs = json.load(f)

        self.chunks = []
        texts = []
        for doc in docs:
            doc_id = doc.get("doc_id", "")
            title = doc.get("title", "")
            for sec in doc.get("sections", []):
                chunk_text = f"{title} [{doc_id}] Section {sec.get('section_id')}: {sec.get('title')}. {sec.get('content')}"
                texts.append(chunk_text)
                self.chunks.append({
                    "doc_id": doc_id,
                    "title": title,
                    "section_id": sec.get("section_id"),
                    "section_title": sec.get("title"),
                    "content": sec.get("content"),
                    "full_text": chunk_text
                })

        if texts:
            self.matrix = self.vectorizer.fit_transform(texts)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves top-k most relevant policy sections for a query."""
        if self.matrix is None or len(self.chunks) == 0:
            return []
        
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            chunk = self.chunks[idx].copy()
            chunk["similarity_score"] = round(score, 4)
            results.append(chunk)
        return results
