import os
from typing import List, Iterable

import numpy as np

# Optional imports are inside classes to avoid heavy imports on cold start

EMBED_MODE = os.getenv("EMBED_MODE", "tfidf").lower()
OPENAI_EMBED_MODEL = os.getenv("EMBED_MODEL_OPENAI", "text-embedding-3-small")
HF_EMBED_MODEL = os.getenv("EMBED_MODEL_HF", "sentence-transformers/all-MiniLM-L6-v2")

def get_embedder():
    if EMBED_MODE in {"openai", "oai"}:
        return OpenAIEmbedder(model=OPENAI_EMBED_MODEL)
    if EMBED_MODE in {"hf", "local", "sentence"}:
        return HFEmbedder(model=HF_EMBED_MODEL)
    return TFIDFEmbedder()  # default

class BaseEmbedder:
    def embed(self, texts: Iterable[str]) -> np.ndarray:
        raise NotImplementedError

class TFIDFEmbedder(BaseEmbedder):
    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def embed(self, texts: Iterable[str]) -> np.ndarray:
        X = self.vectorizer.fit_transform(list(texts))
        return X.toarray().astype("float32")

class HFEmbedder(BaseEmbedder):
    def __init__(self, model: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model)

    def embed(self, texts: Iterable[str]) -> np.ndarray:
        embs = self.model.encode(list(texts), normalize_embeddings=True, convert_to_numpy=True)
        return embs.astype("float32")

class OpenAIEmbedder(BaseEmbedder):
    def __init__(self, model: str):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def embed(self, texts: Iterable[str]) -> np.ndarray:
        batch = list(texts)
        # openai returns list of data with embeddings
        resp = self.client.embeddings.create(model=self.model, input=batch)
        vecs = [item.embedding for item in resp.data]
        return np.array(vecs, dtype="float32")
