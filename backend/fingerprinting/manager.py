# fingerprinting/manager.py
import os
import json
from typing import List, Dict, Any
from .simhash import normalize_code, tokenize, compute_simhash
from .winnowing import winnow

# file extensions to include
CODE_EXTS = (".py", ".js", ".java", ".ts", ".cpp", ".c", ".hpp", ".h")

def read_repo_text(repo_path: str) -> str:
    collected = []
    for root, _, files in os.walk(repo_path):
        # skip common large dirs
        if any(ex in root for ex in ("node_modules", ".git", "venv", "__pycache__", "dist")):
            continue
        for f in files:
            if f.lower().endswith(CODE_EXTS):
                fp = os.path.join(root, f)
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                        collected.append(fh.read())
                except Exception:
                    continue
    return "\n".join(collected)

def compute_fingerprints_for_repo(repo_path: str, k: int = 25, window: int = 4) -> Dict[str, Any]:
    """
    Returns dict:
    {
        "simhash": int,
        "winnowing": [ [hash, pos], ... ],
        "token_count": int
    }
    """
    txt = read_repo_text(repo_path)
    if not txt.strip():
        return {"simhash": 0, "winnowing": [], "token_count": 0}

    normalized = normalize_code(txt)
    tokens = tokenize(normalized)
    simhash_v = compute_simhash(tokens)
    wfp = winnow(tokens, k=k, window=window)
    return {
        "simhash": simhash_v,
        "winnowing": wfp,
        "token_count": len(tokens)
    }
