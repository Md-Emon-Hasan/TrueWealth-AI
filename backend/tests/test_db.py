from app.core.db import get_history, get_stats, init_db, log_query


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
