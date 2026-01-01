# fingerprinting/simhash.py
import re
import hashlib

def normalize_code(text: str) -> str:
    """Normalize code by removing extra whitespace and comments."""
    text = re.sub(r"//.*?$|/\*.*?\*/", "", text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r"#.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokenize(text: str):
    """Very simple tokenizer."""
    return re.findall(r"[A-Za-z_]\w*", text)

def compute_simhash(tokens, hash_bits=64):
    """Compute SimHash for given tokens."""
    v = [0] * hash_bits

    for token in tokens:
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        for i in range(hash_bits):
            bit = 1 if (h >> i) & 1 else -1
            v[i] += bit

    fingerprint = 0
    for i in range(hash_bits):
        if v[i] > 0:
            fingerprint |= (1 << i)

    return fingerprint

def hamming_distance(h1: int, h2: int) -> int:
    """Return hamming distance between two simhash values."""
    return bin(h1 ^ h2).count("1")

def simhash_similarity(h1: int, h2: int) -> float:
    dist = hamming_distance(h1, h2)
    return 1 - dist / 64
