# fingerprinting/manager.py
import os
from typing import Dict, Any, List

from .simhash import normalize_code, tokenize, compute_simhash
from .winnowing import winnow

CODE_EXTS = (".py", ".js", ".java", ".ts", ".cpp", ".c", ".hpp", ".h")
SKIP_DIRS = ("node_modules", ".git", "venv", "__pycache__", "dist", "build")


def iter_code_files(repo_path: str):
    for root, _, files in os.walk(repo_path):
        if any(skip in root for skip in SKIP_DIRS):
            continue
        for file in files:
            if file.lower().endswith(CODE_EXTS):
                yield os.path.join(root, file)


def compute_fingerprints_for_repo(
    repo_path: str,
    k: int = 15,
    window: int = 4
) -> Dict[str, Any]:
    """
    Compute repo-level fingerprints (DB ingestion).

    Returns:
    {
        "repo_simhash": int,
        "winnowing": Set[int],
        "total_tokens": int
    }
    """

    all_tokens: List[str] = []

    for file_path in iter_code_files(repo_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
        except Exception:
            continue

        if not code.strip():
            continue

        normalized = normalize_code(code)
        tokens = tokenize(normalized)

        if tokens:
            all_tokens.extend(tokens)

    if not all_tokens:
        return {
            "repo_simhash": 0,
            "winnowing": set(),
            "total_tokens": 0,
        }

    repo_simhash = compute_simhash(all_tokens)
    repo_winnowing = winnow(all_tokens, k=k, window=window)

    return {
        "repo_simhash": repo_simhash,
        "winnowing": repo_winnowing,
        "total_tokens": len(all_tokens),
    }
