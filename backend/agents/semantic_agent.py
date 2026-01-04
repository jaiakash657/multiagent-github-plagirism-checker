from typing import Dict, List
import os
import numpy as np
from sentence_transformers import SentenceTransformer

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

    def _collect_texts(self, repo_path: str) -> List[str]:
        texts = []
        for root, _, files in os.walk(repo_path):
            for f in files:
                if f.endswith((".py", ".java", ".js", ".md")):
                    try:
                        with open(
                            os.path.join(root, f),
                            "r",
                            encoding="utf-8",
                            errors="ignore",
                        ) as fh:
                            content = fh.read().strip()
                            if content:
                                texts.append(content[:2000])
                    except Exception:
                        continue
        return texts

    def _embed(self, texts: List[str]) -> np.ndarray:
        vecs = self.model.encode(texts, convert_to_numpy=True)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return vecs / norms

    def run(self, input_repo_path: str, cand_repo_path: str) -> Dict:
        input_texts = self._collect_texts(input_repo_path)
        cand_texts = self._collect_texts(cand_repo_path)

        if not input_texts or not cand_texts:
            return {
                "agent": "semantic",
                "score": 0.0,
                "details": {
                    "status": "failed",
                    "reason": "no_texts",
                },
            }

        input_vecs = self._embed(input_texts)
        cand_vecs = self._embed(cand_texts)

        # Cross-repo similarity
        sims = input_vecs @ cand_vecs.T

        # 🔑 Use strongest signal
        best_sim = float(sims.max())

        return {
            "agent": "semantic",
            "score": round(best_sim, 4),
            "details": {
                "status": "executed",
                "input_files": len(input_texts),
                "candidate_files": len(cand_texts),
                "best_similarity": best_sim,
            },
        }
