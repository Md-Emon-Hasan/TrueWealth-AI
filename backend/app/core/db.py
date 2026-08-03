from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import text
from sqlmodel import Field, Session, SQLModel, create_engine, select

from app.core.config import SQLITE_PATH

# SQLModel.metadata.create_all only creates missing tables, it never alters existing ones,
# so a column added after the table already exists on disk needs an explicit ALTER TABLE
_ADDED_COLUMNS = [
    ("model_used", "TEXT"),
    ("fallback_used", "BOOLEAN DEFAULT 0"),
    ("compliance_violations", "TEXT"),
]


def _utcnow():
    return datetime.now(timezone.utc)


class QueryLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str
    question: str
    answer: str
    source: str
    agents_run: str
    latency_ms: float
    tokens_used: Optional[int] = None
    degraded: Optional[str] = None
    model_used: Optional[str] = None
    fallback_used: bool = False
    compliance_violations: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)


engine = create_engine(f"sqlite:///{SQLITE_PATH}", connect_args={"check_same_thread": False})


def init_db():
    SQLModel.metadata.create_all(engine)
    with engine.connect() as conn:
        existing = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(querylog)")}
        for name, coltype in _ADDED_COLUMNS:
            if name not in existing:
                conn.execute(text(f"ALTER TABLE querylog ADD COLUMN {name} {coltype}"))
        conn.commit()


def log_query(session_id, question, answer, source, agents_run, latency_ms, tokens_used=None,
              degraded=None, model_used=None, fallback_used=False, compliance_violations=None):
    with Session(engine) as session:
        entry = QueryLog(
            session_id=session_id,
            question=question,
            answer=answer,
            source=source,
            agents_run=",".join(agents_run),
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            degraded=degraded,
            model_used=model_used,
            fallback_used=fallback_used,
            compliance_violations=",".join(compliance_violations) if compliance_violations else None,
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry


def get_history(limit=50, offset=0):
    with Session(engine) as session:
        stmt = select(QueryLog).order_by(QueryLog.id.desc()).offset(offset).limit(limit)
        return session.exec(stmt).all()


def get_stats():
    with Session(engine) as session:
        rows = session.exec(select(QueryLog)).all()

    count = len(rows)
    avg_latency_ms = sum(r.latency_ms for r in rows) / count if count else 0
    degraded_count = sum(1 for r in rows if r.degraded)
    fallback_count = sum(1 for r in rows if r.fallback_used)
    compliance_violation_count = sum(1 for r in rows if r.compliance_violations)
    source_counts = {}
    model_counts = {}
    for r in rows:
        source_counts[r.source] = source_counts.get(r.source, 0) + 1
        if r.model_used:
            model_counts[r.model_used] = model_counts.get(r.model_used, 0) + 1

    return {
        "total_queries": count,
        "avg_latency_ms": avg_latency_ms,
        "degraded_count": degraded_count,
        "fallback_count": fallback_count,
        "compliance_violation_count": compliance_violation_count,
        "source_counts": source_counts,
        "model_counts": model_counts,
    }
