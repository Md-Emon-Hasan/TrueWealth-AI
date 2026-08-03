from app.core.review import needs_review


def test_flags_high_risk():
    assert needs_review({"risk": "high"}, None, None, "rag_documents") is True


def test_flags_unsupported_figures():
    assert needs_review({"risk": "low", "unsupported_figures": ["42%"]}, None, None, "rag_documents") is True


def test_flags_compliance_violation():
    assert needs_review(None, {"violations": ["guaranteed_returns_claim"]}, None, "llm_knowledge") is True


def test_ignores_missing_disclaimer_alone():
    assert needs_review({"risk": "low"}, {"violations": ["missing_disclaimer"]}, None, "llm_knowledge") is False


def test_flags_market_data_unavailable_for_price_dependent_source():
    assert needs_review({"risk": "low"}, None, "yfinance_no_data", "market_desk") is True


def test_does_not_flag_market_data_unavailable_for_non_price_source():
    assert needs_review({"risk": "low"}, None, "no_relevant_documents", "rag_documents") is False


def test_clean_answer_does_not_need_review():
    verification = {"risk": "low", "unsupported_figures": []}
    compliance = {"violations": ["missing_disclaimer"]}
    assert needs_review(verification, compliance, None, "llm_knowledge") is False
