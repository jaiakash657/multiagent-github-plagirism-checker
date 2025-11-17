# storage/db.py  (full replacement)
import sqlite3
import json
import os
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fingerprints.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS repos (
        id INTEGER PRIMARY KEY,
        repo_url TEXT UNIQUE,
        simhash TEXT,
        winnowing TEXT,
        token_count INTEGER,
        metadata TEXT,
        last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def save_fingerprints(repo_url: str, simhash: int, winnowing: List, token_count: int, metadata: Optional[Dict]=None):
    """
    Store fingerprints. simhash saved as TEXT to avoid SQLite INTEGER overflow.
    winnowing and metadata are JSON-encoded strings.
    """
    conn = _get_conn()
    cur = conn.cursor()
    # convert simhash to string to avoid integer overflow in SQLite
    simhash_str = str(simhash) if simhash is not None else None
    cur.execute("""
        INSERT INTO repos (repo_url, simhash, winnowing, token_count, metadata)
        VALUES (?,?,?,?,?)
        ON CONFLICT(repo_url) DO UPDATE SET
          simhash=excluded.simhash,
          winnowing=excluded.winnowing,
          token_count=excluded.token_count,
          metadata=excluded.metadata,
          last_scanned=CURRENT_TIMESTAMP
    """, (repo_url, simhash_str, json.dumps(winnowing), token_count, json.dumps(metadata or {})))
    conn.commit()
    conn.close()

def load_fingerprints(repo_url: str) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM repos WHERE repo_url = ?", (repo_url,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None

    # parse simhash back to int (Python supports big ints)
    simhash_val = None
    if row["simhash"] is not None:
        try:
            simhash_val = int(row["simhash"])
        except Exception:
            # fallback: keep as 0 if unparsable
            simhash_val = 0

    return {
        "repo_url": row["repo_url"],
        "simhash": simhash_val or 0,
        "winnowing": json.loads(row["winnowing"] or "[]"),
        "token_count": int(row["token_count"] or 0),
        "metadata": json.loads(row["metadata"] or "{}")
    }

def get_all_repos() -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT repo_url, simhash FROM repos")
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        # convert stored simhash string back to int (safe for Python)
        simhash_val = 0
        try:
            if r["simhash"] is not None:
                simhash_val = int(r["simhash"])
        except Exception:
            simhash_val = 0
        out.append({"repo_url": r["repo_url"], "simhash": simhash_val})
    return out

def query_simhash_candidates(simhash_value: int, max_hamming: int = 6, limit: int = 50) -> List[str]:
    """
    Simple scan of DB simhash values, checks Hamming distance <= max_hamming.
    For dev use; if DB big, replace with LSH or optimized index.
    """
    from fingerprinting.simhash import hamming_distance
    rows = get_all_repos()
    out = []
    for r in rows:
        other = r["simhash"]
        if not other:
            continue
        try:
            dist = hamming_distance(int(simhash_value), int(other))
        except Exception:
            continue
        if dist <= max_hamming:
            out.append((r["repo_url"], dist))
    # sort by distance ascending
    out.sort(key=lambda x: x[1])
    return [u for u,_ in out[:limit]]
