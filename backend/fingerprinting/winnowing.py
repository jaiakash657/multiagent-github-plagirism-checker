# fingerprinting/winnowing.py
import hashlib
from typing import List, Tuple

def rolling_hash(kgram: str) -> int:
    """Simple deterministic hash for a k-gram (use md5 and reduce)."""
    h = hashlib.md5(kgram.encode("utf-8")).hexdigest()
    return int(h, 16) & 0xFFFFFFFFFFFFFFFF  # 64-bit

def kgrams(tokens: List[str], k: int) -> List[str]:
    if len(tokens) < k:
        return []
    return [" ".join(tokens[i:i+k]) for i in range(len(tokens)-k+1)]

def winnow(tokens: List[str], k: int = 25, window: int = 4) -> List[Tuple[int,int]]:
    """
    Winnowing algorithm:
      - build k-grams
      - compute rolling hash for each k-gram
      - for each window choose the minimum hash (with index) -> fingerprint
    Returns list of (hash, position)
    """
    kg = kgrams(tokens, k)
    if not kg:
        return []

    hashes = [rolling_hash(g) for g in kg]
    fingerprints = []
    w = window
    n = len(hashes)
    if w > n:
        # reduce window if repo small
        w = n

    # sliding window min (choose rightmost min for reproducibility)
    for i in range(n - w + 1):
        window_hashes = hashes[i:i+w]
        min_val = min(window_hashes)
        # pick the rightmost index of the min within the window
        rel_idx = (w - 1) - window_hashes[::-1].index(min_val)
        absolute_idx = i + rel_idx
        fingerprints.append((min_val, absolute_idx))

    # deduplicate while preserving order
    seen = set()
    uniq = []
    for h,pos in fingerprints:
        if h not in seen:
            seen.add(h)
            uniq.append((h,pos))
    return uniq

def jaccard_from_fingerprints(fp_a: List[Tuple[int,int]], fp_b: List[Tuple[int,int]]) -> float:
    set_a = set(h for h,_ in fp_a)
    set_b = set(h for h,_ in fp_b)
    if not set_a or not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union
