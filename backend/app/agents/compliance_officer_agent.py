import re

from app.core.state import AgentState

DISCLAIMER = "This is not financial advice; consult a licensed advisor before making investment decisions."

_INJECTION_PATTERNS = [
    re.compile(r"ignore (all|any|the)?\s*previous instructions", re.I),
    re.compile(r"disregard (all|any|the)?\s*(above|prior|previous)", re.I),
    re.compile(r"\byou are now\b", re.I),
    re.compile(r"^\s*(system|assistant)\s*:", re.I | re.M),
    re.compile(r"new instructions\s*:", re.I),
]

_GUARANTEE_PATTERNS = [
    re.compile(r"guaranteed?\s+(return|profit|gain)", re.I),
    re.compile(r"risk[- ]free", re.I),
    re.compile(r"can'?t lose", re.I),
    re.compile(r"will (definitely|certainly)\s+(rise|increase|go up|grow)", re.I),
]

_DIRECTIVE_PATTERNS = [
    re.compile(r"\b(you should|i recommend|recommend that you)\s+(buy|sell)\b", re.I),
    # imperative sentence-starting "Buy X" / "Sell X", not a mid-sentence mention of the words
    re.compile(r"(?:^|[.!?]\s+)(buy|sell)\b", re.I),
]
_HEDGE_WORDS = ("consider", "might", "could", "may want to", "one option", "generally", "typically")

_PII_PATTERNS = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b"),
}

_FIGURE_PATTERN = re.compile(r"\$\s?\d[\d,]*(\.\d+)?|\b\d+(\.\d+)?\s?%")


class ComplianceOfficerAgent:
    def sanitize_input(self, text):
        """Neutralise instruction-like content from untrusted PDF/web text before it reaches a prompt"""
        if not text:
            return text
        sanitized = text
        for pattern in _INJECTION_PATTERNS:
            sanitized = pattern.sub("[redacted instruction-like content]", sanitized)
        return sanitized

    def check_output(self, text, question="", source=""):
        violations = []

        if any(p.search(text) for p in _GUARANTEE_PATTERNS):
            violations.append("guaranteed_returns_claim")

        has_directive = any(p.search(text) for p in _DIRECTIVE_PATTERNS)
        if has_directive and not any(h in text.lower() for h in _HEDGE_WORDS):
            violations.append("unhedged_directive")

        for label, pattern in _PII_PATTERNS.items():
            if pattern.search(text) and not pattern.search(question):
                violations.append(f"pii_{label}")

        if source == "llm_knowledge" and _FIGURE_PATTERN.search(text):
            violations.append("unsourced_figure")

        has_disclaimer = DISCLAIMER in text
        if not has_disclaimer:
            violations.append("missing_disclaimer")

        sanitised_text = text if has_disclaimer else f"{text}\n\n{DISCLAIMER}"

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "sanitised_text": sanitised_text,
        }


def compliance_officer_agent(state: AgentState):
    agent = ComplianceOfficerAgent()
    result = agent.check_output(
        state.get('generation', ''), state.get('question', ''), state.get('source', '')
    )
    state['generation'] = result['sanitised_text']
    state['compliance'] = result
    return state
