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

def fingerprint_file(file_path: str, k: int, window: int) -> Dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
    except Exception:
        return None

    if not code.strip():
        return None

    normalized = normalize_code(code)
    tokens = tokenize(normalized)

    if not tokens:
        return None

    return {
        "path": file_path,
        "extension": os.path.splitext(file_path)[1],
        "token_count": len(tokens),
        "simhash": compute_simhash(tokens),
        "winnowing": winnow(tokens, k=k, window=window)
    }

def compute_fingerprints_for_repo(
    repo_path: str,
    k: int = 25,
    window: int = 4
) -> Dict[str, Any]:
    """
    Returns:
    {
        "repo_simhash": int,
        "files": [ {...file_fingerprint}, ... ],
        "total_tokens": int
    }
    """

    file_fingerprints: List[Dict[str, Any]] = []
    all_tokens: List[str] = []

    for file_path in iter_code_files(repo_path):
        fp = fingerprint_file(file_path, k, window)
        if not fp:
            continue

        file_fingerprints.append(fp)
        all_tokens.extend(fp["token_count"] * ["_"])  # weight aggregation

    repo_simhash = compute_simhash(all_tokens) if all_tokens else 0

    return {
        "repo_simhash": repo_simhash,
        "files": file_fingerprints,
        "total_tokens": sum(f["token_count"] for f in file_fingerprints)
    }
