from app.agents.planner_agent import initialize_planner as planner


def test_planner():
    state = {"retry_count": 5}
    result = planner(state)
    assert result["retry_count"] == 0
