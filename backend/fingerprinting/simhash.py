# fingerprinting/simhash.py
import re
import hashlib
from collections import Counter

def normalize_code(text: str) -> str:
    """
    Light normalization:
    - remove comments
    - normalize whitespace
    """
    text = re.sub(r"//.*?$|/\*.*?\*/", "", text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r"#.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str):
    """
    Code-oriented tokenizer:
    - identifiers
    - keywords
    - numeric literals
    """
    return re.findall(r"[A-Za-z_]\w*|\d+", text)


def compute_simhash(tokens, hash_bits: int = 64) -> int:
    """
    Compute weighted SimHash.
    """
    v = [0] * hash_bits
    token_freq = Counter(tokens)

    for token, weight in token_freq.items():
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)

        for i in range(hash_bits):
            bit = 1 if (h >> i) & 1 else -1
            v[i] += bit * weight   # 🔥 WEIGHTED

    fingerprint = 0
    for i in range(hash_bits):
        if v[i] > 0:
            fingerprint |= (1 << i)

    return fingerprint


def hamming_distance(h1: int, h2: int) -> int:
    return (h1 ^ h2).bit_count()


def simhash_similarity(h1: int, h2: int, hash_bits: int = 64) -> float:
    return 1 - hamming_distance(h1, h2) / hash_bits
