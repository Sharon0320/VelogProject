from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self) -> None:
        # Small, fast model suitable for 384-dim embeddings
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        vectors = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True)
        return [np.asarray(v, dtype=np.float32) for v in vectors]

    def embed_single(self, text: str) -> np.ndarray:
        return self.embed_texts([text])[0]


