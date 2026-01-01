from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from storage.db import Base

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
    metadata = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
