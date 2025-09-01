from typing import List, Tuple, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .nlp import extract_skills_simple

def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    a = a.reshape(1, -1)
    b = b.reshape(1, -1)
    return float(cosine_similarity(a, b)[0][0])

def compute_score(resume_text: str, jd_text: str, embedder=None) -> Tuple[float, float, float, List[str]]:
    # semantic
    if embedder is None:
        # fallback: TF-IDF inside embedder-like interface
        from .embed import TFIDFEmbedder
        embedder = TFIDFEmbedder()

    vecs = embedder.embed([resume_text, jd_text])
    semantic = max(0.0, _cosine_sim(vecs[0], vecs[1]) * 100.0)

    # skills overlap
    jd_skills = extract_skills_simple(jd_text)
    resume_skills = extract_skills_simple(resume_text)
    overlap = sorted(list(jd_skills & resume_skills))
    overlap_pct = (len(overlap) / len(jd_skills) * 100.0) if jd_skills else 0.0

    final = 0.4 * semantic + 0.6 * overlap_pct
    return final, semantic, overlap_pct, overlap
