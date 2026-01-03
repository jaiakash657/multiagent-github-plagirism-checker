# fingerprinting/winnowing.py
import hashlib
from typing import List, Set


def rolling_hash(tokens: List[str]) -> int:
    """
    Deterministic rolling hash for a k-gram token list.
    """
    h = hashlib.md5(" ".join(tokens).encode("utf-8")).hexdigest()
    return int(h, 16) & 0xFFFFFFFFFFFFFFFF  # 64-bit


def winnow(tokens: List[str], k: int = 15, window: int = 4) -> Set[int]:
    """
    Winnowing algorithm (hash-only fingerprints).
    Returns a set of hash values.
    """
    n = len(tokens)
    if n < k:
        return set()

    # build rolling hashes
    hashes = [
        rolling_hash(tokens[i : i + k])
        for i in range(n - k + 1)
    ]

    w = min(window, len(hashes))
    fingerprints = []

    for i in range(len(hashes) - w + 1):
        window_hashes = hashes[i : i + w]
        min_val = min(window_hashes)

        # rightmost min for stability
        idx = (w - 1) - window_hashes[::-1].index(min_val)
        fingerprints.append(min_val)

    return set(fingerprints)


def jaccard_similarity(fp_a: Set[int], fp_b: Set[int]) -> float:
    if not fp_a or not fp_b:
        return 0.0

    inter = len(fp_a & fp_b)
    union = len(fp_a | fp_b)
    return inter / union
