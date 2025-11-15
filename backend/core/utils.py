import os
import hashlib

def compute_file_hash(filepath):
    """Compute SHA256 hash of a file (useful for FingerprintAgent)."""
    sha = hashlib.sha256()

    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)

    return sha.hexdigest()


def list_all_files(base_path):
    """Return list of all files in repo."""
    paths = []
    for root, dirs, files in os.walk(base_path):
        for f in files:
            paths.append(os.path.join(root, f))
    return paths
