from app.core.db import (get_history, get_review_queue, get_stats, init_db,
                          log_query, submit_review)


def setup_function():
    init_db()


def test_log_query_and_get_history():
    log_query("s1", "what is a bond", "a bond is a debt security", "llm_knowledge", ["llm"], 120.5)
    rows = get_history(limit=1)
    assert rows[0].question == "what is a bond"
    assert rows[0].source == "llm_knowledge"


def test_get_history_pagination():
    for i in range(3):
        log_query("s1", f"q{i}", "a", "llm_knowledge", ["llm"], 10.0)
    page1 = get_history(limit=2, offset=0)
    page2 = get_history(limit=2, offset=2)
    assert len(page1) == 2
    assert page1[0].id != page2[0].id


def test_get_stats_aggregates():
    log_query("s1", "q", "a", "rag_documents", ["llm", "rag"], 50.0, degraded="no_relevant_documents")
    stats = get_stats()
    assert stats["total_queries"] >= 1
    assert stats["degraded_count"] >= 1
    assert "rag_documents" in stats["source_counts"]


def test_get_stats_tracks_model_and_fallback_usage():
    log_query("s1", "q", "a", "llm_knowledge", ["llm"], 30.0,
              model_used="llama-3.3-70b-versatile", fallback_used=True)
    stats = get_stats()
    assert stats["fallback_count"] >= 1
    assert "llama-3.3-70b-versatile" in stats["model_counts"]


def test_review_queue_contains_flagged_entries():
    entry = log_query("s1", "risky q", "risky a", "llm_knowledge", ["llm"], 10.0, needs_review=True)
    queue = get_review_queue(status="pending")
    assert any(row.id == entry.id for row in queue)
    assert entry.review_status == "pending"


def test_review_queue_excludes_unflagged_entries():
    entry = log_query("s1", "clean q", "clean a", "llm_knowledge", ["llm"], 10.0, needs_review=False)
    queue = get_review_queue(status="pending")
    assert not any(row.id == entry.id for row in queue)


def test_submit_review_records_verdict_without_overwriting_answer():
    entry = log_query("s1", "risky q2", "original answer", "llm_knowledge", ["llm"], 10.0, needs_review=True)
    updated = submit_review(entry.id, "approved")
    assert updated.human_verdict == "approved"
    assert updated.review_status == "reviewed"
    assert updated.answer == "original answer"
    assert updated.reviewed_at is not None


def test_submit_review_missing_id_returns_none():
    assert submit_review(999999, "approved") is None


def test_stats_reports_review_and_agreement_rate():
    entry = log_query("s1", "q", "a", "llm_knowledge", ["llm"], 10.0, needs_review=True)
    submit_review(entry.id, "approved")
    stats = get_stats()
    assert stats["review_completed_count"] >= 1
    assert stats["human_agreement_rate"] is not None


def test_init_db_migrates_missing_columns(tmp_path):
    import app.core.db as db_module
    from sqlmodel import create_engine

    old_path = tmp_path / "legacy.sqlite3"
    old_engine = create_engine(f"sqlite:///{old_path}")
    with old_engine.connect() as conn:
        conn.exec_driver_sql("""
            CREATE TABLE querylog (
                id INTEGER PRIMARY KEY, session_id TEXT, question TEXT, answer TEXT,
                source TEXT, agents_run TEXT, latency_ms FLOAT,
                tokens_used INTEGER, degraded TEXT, created_at DATETIME
            )
        """)
        conn.commit()

    original_engine = db_module.engine
    db_module.engine = old_engine
    try:
        db_module.init_db()
        db_module.log_query("s1", "q", "a", "llm_knowledge", ["llm"], 10.0, model_used="m", fallback_used=True)
    finally:
        db_module.engine = original_engine
