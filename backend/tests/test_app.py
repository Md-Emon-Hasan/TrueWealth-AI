def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_chat_endpoint_success(client, mock_workflow, mock_initialize_state):
    # Setup mock return
    mock_workflow.ainvoke.return_value = {
        "generation": "Test response",
        "source": "Test source"
    }

    payload = {
        "message": "Hello",
        "session_id": "test_session"
    }

    response = client.post("/api/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Test response"
    assert data["session_id"] == "test_session"
    assert data["source"] == "Test source"

    # Verify mock calls
    mock_workflow.ainvoke.assert_called_once()


def test_chat_endpoint_new_session(client, mock_workflow, mock_initialize_state):
    mock_workflow.ainvoke.return_value = {
        "generation": "New session response",
        "source": "New source"
    }

    # Session ID that doesn't exist yet
    payload = {
        "message": "Start",
        "session_id": "fresh_session_123"
    }

    response = client.post("/api/chat", json=payload)

    assert response.status_code == 200
    assert response.json()["response"] == "New session response"
    mock_initialize_state.assert_called()


def test_chat_endpoint_validation_error(client):
    # Missing message field
    payload = {
        "session_id": "123"
    }

    response = client.post("/api/chat", json=payload)

    # FastAPI automatically handles 422 for missing required fields
    assert response.status_code == 422


def test_chat_endpoint_internal_error(client, mock_workflow):
    # Simulate workflow failure
    mock_workflow.ainvoke.side_effect = Exception("Workflow failed")

    payload = {
        "message": "Crash me"
    }

    response = client.post("/api/chat", json=payload)

    assert response.status_code == 500
    assert "Workflow failed" in response.json()["detail"]


def test_chat_endpoint_caches_non_market_answer(client, mock_workflow, mock_initialize_state):
    mock_workflow.ainvoke.return_value = {"generation": "cached answer", "source": "rag_documents"}
    payload = {"message": "unique cache test question", "session_id": "s1"}

    client.post("/api/chat", json=payload)
    second = client.post("/api/chat", json=payload)

    assert second.json()["response"] == "cached answer"
    mock_workflow.ainvoke.assert_called_once()


def test_chat_endpoint_never_caches_live_market_answer(client, mock_workflow, mock_initialize_state):
    mock_workflow.ainvoke.return_value = {"generation": "AAPL is at $123", "source": "yfinance"}
    payload = {"message": "unique market data question", "session_id": "s1"}

    client.post("/api/chat", json=payload)
    client.post("/api/chat", json=payload)

    assert mock_workflow.ainvoke.call_count == 2


def test_history_endpoint_returns_recorded_query(client, mock_workflow, mock_initialize_state):
    mock_workflow.ainvoke.return_value = {"generation": "history answer", "source": "llm_knowledge"}
    payload = {"message": "unique history question", "session_id": "s1"}
    client.post("/api/chat", json=payload)

    response = client.get("/api/history?limit=5")

    assert response.status_code == 200
    assert any(row["question"] == "unique history question" for row in response.json())


def test_stats_endpoint_returns_aggregates(client):
    response = client.get("/api/stats")

    assert response.status_code == 200
    body = response.json()
    assert "total_queries" in body
    assert "source_counts" in body
    assert "review_pending_count" in body


def test_chat_flags_high_risk_answer_for_review(client, mock_workflow, mock_initialize_state):
    mock_workflow.ainvoke.return_value = {
        "generation": "The fund returned 42% last year.",
        "source": "rag_documents",
        "verification": {"risk": "high", "unsupported_figures": ["42%"]},
    }
    payload = {"message": "unique review-flag question", "session_id": "s1"}
    client.post("/api/chat", json=payload)

    queue = client.get("/api/review?status=pending").json()
    assert any(row["question"] == "unique review-flag question" for row in queue)


def test_submit_review_endpoint_records_verdict(client, mock_workflow, mock_initialize_state):
    mock_workflow.ainvoke.return_value = {
        "generation": "risky answer",
        "source": "rag_documents",
        "verification": {"risk": "high"},
    }
    payload = {"message": "unique verdict question", "session_id": "s1"}
    client.post("/api/chat", json=payload)

    queue = client.get("/api/review?status=pending").json()
    entry_id = next(row["id"] for row in queue if row["question"] == "unique verdict question")

    response = client.post(f"/api/review/{entry_id}", json={"verdict": "approved"})

    assert response.status_code == 200
    assert response.json()["human_verdict"] == "approved"
    assert response.json()["answer"] == "risky answer"


def test_submit_review_endpoint_rejects_invalid_verdict(client):
    response = client.post("/api/review/1", json={"verdict": "not_a_real_verdict"})
    assert response.status_code == 422


def test_submit_review_endpoint_missing_id_returns_404(client):
    response = client.post("/api/review/999999", json={"verdict": "approved"})
    assert response.status_code == 404
