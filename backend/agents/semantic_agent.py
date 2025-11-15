from typing import Tuple, Dict
import os
from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def _get_model(name="sentence-transformers/all-MiniLM-L6-v2"):
    global _model
    if _model is None:
        _model = SentenceTransformer(name)
    return _model

class SemanticAgent:
    def __init__(self, model_name=None):
        self.model_name = model_name or "sentence-transformers/all-MiniLM-L6-v2"
        self.model = _get_model(self.model_name)

    def _file_embedding(self, text: str):
        return self.model.encode([text], convert_to_numpy=True)[0]

    def analyze(self, repo_path: str, depth: int = 1) -> Tuple[float, Dict]:
        # collect file texts (short)
        texts = []
        for root, _, files in os.walk(repo_path):
            for f in files:
                if f.endswith((".py", ".java", ".js", ".md")):
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                            texts.append(fh.read()[:2000])
                    except Exception:
                        continue
        if not texts:
            return 0.0, {"reason": "no_texts"}
        embs = [self._file_embedding(t) for t in texts]
        # naive similarity measure: average pairwise cosine similarity
        vecs = np.vstack(embs)
        # normalized
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms==0] = 1
        nvecs = vecs / norms
        sims = (nvecs @ nvecs.T)
        # ignore diagonal, compute mean of upper triangle
        n = sims.shape[0]
        if n <= 1:
            return 0.0, {"reason": "single_file"}
        tri_ix = np.triu_indices(n, k=1)
        mean_sim = float(sims[tri_ix].mean())
        score = float(mean_sim)
        return score, {"mean_pairwise_similarity": score, "files_analyzed": n}
