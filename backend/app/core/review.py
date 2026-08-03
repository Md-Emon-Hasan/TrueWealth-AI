from app.core.config import (REVIEW_IGNORED_VIOLATIONS, REVIEW_ON_COMPLIANCE_VIOLATION,
                             REVIEW_ON_HIGH_RISK, REVIEW_ON_MARKET_DATA_UNAVAILABLE,
                             REVIEW_ON_UNSUPPORTED_FIGURES)

_PRICE_DEPENDENT_SOURCES = {"yfinance", "market_desk", "portfolio_analysis"}


def needs_review(verification, compliance, degraded, source):
    verification = verification or {}
    compliance = compliance or {}

    if REVIEW_ON_HIGH_RISK and verification.get("risk") == "high":
        return True

    if REVIEW_ON_UNSUPPORTED_FIGURES and verification.get("unsupported_figures"):
        return True

    violations = set(compliance.get("violations") or []) - REVIEW_IGNORED_VIOLATIONS
    if REVIEW_ON_COMPLIANCE_VIOLATION and violations:
        return True

    if REVIEW_ON_MARKET_DATA_UNAVAILABLE and source in _PRICE_DEPENDENT_SOURCES and degraded:
        return True

    return False
