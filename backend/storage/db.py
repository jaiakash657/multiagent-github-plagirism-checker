# storage/db.py
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    JSON, ForeignKey, DateTime, text
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import insert

# load env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ---------------- MODELS ---------------- #

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    repo_url = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Fingerprint(Base):
    __tablename__ = "fingerprints"

    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"))
    agent = Column(String, nullable=False)
    score = Column(Float)
    extra_data = Column("metadata", JSON)  # ✅ FIX
    created_at = Column(DateTime, server_default=func.now())



# ---------------- DB FUNCTIONS ---------------- #

def get_db():
    return SessionLocal()


def save_repository(repo_url: str, content_hash: str) -> int:
    """
    Insert repo snapshot if not exists, return repo_id
    """
    db = get_db()

    repo = db.query(Repository).filter_by(
        repo_url=repo_url,
        content_hash=content_hash
    ).first()

    if repo:
        db.close()
        return repo.id

    repo = Repository(repo_url=repo_url, content_hash=content_hash)
    db.add(repo)
    db.commit()
    db.refresh(repo)
    db.close()
    return repo.id


from sqlalchemy.dialects.postgresql import insert

def save_fingerprint(
    repo_id: int,
    agent: str,
    score: float,
    metadata: dict | None = None
):
    db = get_db()

    stmt = insert(Fingerprint).values(
        repo_id=repo_id,
        agent=agent,
        score=score,
        metadata=metadata or {},   # ✅ plain dict
    ).on_conflict_do_update(
        index_elements=["repo_id", "agent"],
        set_={
            "score": score,
            "metadata": metadata or {},  # ✅ plain dict
        }
    )

    db.execute(stmt)
    db.commit()
    db.close()




def get_repo_by_hash(content_hash: str) -> Optional[int]:
    """
    Used for identity detection
    """
    db = get_db()
    repo = db.query(Repository).filter_by(content_hash=content_hash).first()
    db.close()
    return repo.id if repo else None


def get_simhash_candidates(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Return all repos + simhash metadata
    (Simhash logic still lives in fingerprinting layer)
    """
    db = get_db()
    rows = db.execute(
        text("""
            SELECT r.repo_url, f.metadata->>'simhash' AS simhash
            FROM repositories r
            JOIN fingerprints f ON r.id = f.repo_id
            WHERE f.agent = 'simhash'
            LIMIT :limit
        """),
        {"limit": limit}
    ).fetchall()
    db.close()

    out = []
    for r in rows:
        try:
            simhash_val = int(r.simhash) if r.simhash else 0
        except Exception:
            simhash_val = 0
        out.append({
            "repo_url": r.repo_url,
            "simhash": simhash_val
        })
    return out
