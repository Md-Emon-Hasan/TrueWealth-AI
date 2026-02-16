def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_chat_endpoint_success(client, mock_workflow, mock_initialize_state):
    # Setup mock return
    mock_workflow.invoke.return_value = {
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
    mock_workflow.invoke.assert_called_once()


def test_chat_endpoint_new_session(client, mock_workflow, mock_initialize_state):
    mock_workflow.invoke.return_value = {
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
    mock_workflow.invoke.side_effect = Exception("Workflow failed")

    payload = {
        "message": "Crash me"
    }

    response = client.post("/api/chat", json=payload)

    assert response.status_code == 500
    assert "Workflow failed" in response.json()["detail"]