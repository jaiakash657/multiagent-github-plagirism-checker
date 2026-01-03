# storage/db.py
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    JSON,
    ForeignKey,
    DateTime,
    text,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import insert

# ------------------------------------------------------
# Load environment
# ------------------------------------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ------------------------------------------------------
# MODELS
# ------------------------------------------------------
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
    agent = Column(String, nullable=False)  # simhash | winnowing
    score = Column(Float)
    extra_data = Column(JSON)     
    created_at = Column(DateTime, server_default=func.now())


# ------------------------------------------------------
# DB SESSION
# ------------------------------------------------------
def get_db():
    return SessionLocal()


# ------------------------------------------------------
# REPOSITORY FUNCTIONS
# ------------------------------------------------------

def save_repository(repo_url: str, content_hash: str) -> int:
    """
    Insert repository snapshot if not exists.
    Returns repo_id.
    """
    db = get_db()

    repo = (
        db.query(Repository)
        .filter_by(repo_url=repo_url, content_hash=content_hash)
        .first()
    )

    if repo:
        db.close()
        return repo.id

    repo = Repository(repo_url=repo_url, content_hash=content_hash)
    db.add(repo)
    db.commit()
    db.refresh(repo)
    db.close()
    return repo.id


def get_repo_by_hash(content_hash: str) -> Optional[int]:
    """
    Identity detection by content hash.
    """
    db = get_db()
    repo = db.query(Repository).filter_by(content_hash=content_hash).first()
    db.close()
    return repo.id if repo else None


# ------------------------------------------------------
# FINGERPRINT STORAGE
# ------------------------------------------------------
def save_fingerprint(
    repo_id: int,
    agent: str,
    score: float,
    extra_data: Dict[str, Any] | None = None,
):
    db = get_db()

    stmt = insert(Fingerprint).values(
        repo_id=repo_id,
        agent=agent,
        score=score,
        extra_data=extra_data or {},   
    ).on_conflict_do_update(
        index_elements=["repo_id", "agent"],
        set_={
            "score": score,
            "extra_data": extra_data or {},  
        },
    )

    db.execute(stmt)
    db.commit()
    db.close()



# ------------------------------------------------------
# DB-FIRST FINGERPRINT FETCH (CRITICAL)
# ------------------------------------------------------
def get_simhash_candidates(limit: int = 50):
    db = get_db()

    rows = db.execute(
        text(
            """
            SELECT
                r.repo_url,

                fs.extra_data->>'simhash' AS simhash,
                fs.extra_data->>'token_count' AS simhash_tokens,

                fw.extra_data->'winnowing' AS winnowing,
                fw.extra_data->>'token_count' AS winnowing_tokens

            FROM repositories r
            LEFT JOIN fingerprints fs
                ON r.id = fs.repo_id AND fs.agent = 'simhash'
            LEFT JOIN fingerprints fw
                ON r.id = fw.repo_id AND fw.agent = 'winnowing'
            LIMIT :limit;
            """
        ),
        {"limit": limit},
    ).fetchall()

    db.close()

    candidates = []

    for r in rows:
        try:
            simhash_val = int(r.simhash) if r.simhash else 0
        except Exception:
            simhash_val = 0

        try:
            token_count = int(r.simhash_tokens or r.winnowing_tokens or 0)
        except Exception:
            token_count = 0

        try:
            winnowing_fp = set(r.winnowing) if r.winnowing else set()
        except Exception:
            winnowing_fp = set()

        candidates.append(
            {
                "repo_url": r.repo_url,
                "simhash": simhash_val,
                "winnowing": winnowing_fp,
                "token_count": token_count,
            }
        )

    return candidates
