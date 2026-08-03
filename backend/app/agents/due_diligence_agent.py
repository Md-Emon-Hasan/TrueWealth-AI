import json
import re

from app.core.config import DUE_DILIGENCE_MAX_REVISIONS, DUE_DILIGENCE_SKIP_WHEN_CLEAN
from app.core.state import AgentState
from app.tools.llm_client import extract_tokens
from app.tools.model_gateway import get_llm

FIGURE_PATTERN = re.compile(r"\$\s?\d[\d,]*(\.\d+)?|\b\d+(\.\d+)?\s?%")

CRITIQUE_PROMPT = """You are a due-diligence reviewer checking a financial advisor's answer against its evidence.

Question:
{question}

Answer:
{generation}

Evidence the answer is supposed to be based on (empty if the answer used general knowledge only):
{evidence}

Check whether every claim is supported by the evidence, whether any specific number in the answer is not
present in the evidence, and whether the answer needs revision to remove unsupported claims.

Respond with strict JSON only, no markdown, in this exact shape:
{{"grounded": true|false, "citations_valid": true|false, "unsupported_figures": ["..."], \
"needs_revision": true|false, "risk": "low"|"medium"|"high"}}"""

REVISION_PROMPT = """Revise this financial advisor answer to remove or hedge any specific figures not \
supported by the evidence below. Keep the same professional tone, 2-3 sentences, do not add new claims.

Original answer:
{generation}

Evidence:
{evidence}

Unsupported figures to remove or hedge: {unsupported}

Return only the revised answer."""


def _extract_figures(text):
    return [m.group(0) for m in FIGURE_PATTERN.finditer(text)]


def _pre_check(generation, evidence_text, source):
    figures = _extract_figures(generation)
    if source == "llm_knowledge":
        unsupported = figures
    else:
        unsupported = [f for f in figures if f not in evidence_text]

    grounded = source != "llm_knowledge" and not unsupported
    citations_valid = source == "llm_knowledge" or bool(evidence_text.strip())
    risk = "high" if unsupported else ("medium" if source == "llm_knowledge" and figures else "low")

    verification = {
        "grounded": grounded,
        "citations_valid": citations_valid,
        "unsupported_figures": unsupported,
        "risk": risk,
    }
    return verification, risk == "low"


def _parse_verdict(content):
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[-1] if "\n" in text else text
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return None


def due_diligence_agent(state: AgentState):
    generation = state.get('generation', '')
    evidence_text = "\n".join(doc.page_content for doc in state.get('documents', []))
    source = state.get('source', '')
    question = state.get('question', '')

    verification, clean = _pre_check(generation, evidence_text, source)

    if clean and DUE_DILIGENCE_SKIP_WHEN_CLEAN:
        verification["revised"] = False
        state['verification'] = verification
        return state

    llm = get_llm("reasoning")
    message = llm.invoke(CRITIQUE_PROMPT.format(question=question, generation=generation, evidence=evidence_text))
    state['tokens_used'] = state.get('tokens_used', 0) + extract_tokens(message)

    verdict = _parse_verdict(message.content)
    if verdict is None:
        verification["revised"] = False
        state['verification'] = verification
        state['degraded'] = state.get('degraded') or message.degraded or 'due_diligence_critique_unparseable'
        return state

    verification = {
        "grounded": verdict.get("grounded", verification["grounded"]),
        "citations_valid": verdict.get("citations_valid", verification["citations_valid"]),
        "unsupported_figures": verdict.get("unsupported_figures", verification["unsupported_figures"]),
        "risk": verdict.get("risk", verification["risk"]),
    }

    if verdict.get("needs_revision") and DUE_DILIGENCE_MAX_REVISIONS > 0:
        revision_llm = get_llm("answer")
        revision_prompt = REVISION_PROMPT.format(
            generation=generation, evidence=evidence_text,
            unsupported=", ".join(verification["unsupported_figures"]) or "none listed"
        )
        revised = revision_llm.invoke(revision_prompt)
        state['tokens_used'] = state.get('tokens_used', 0) + extract_tokens(revised)
        state['generation'] = revised.content.strip()
        verification["revised"] = True
    else:
        verification["revised"] = False

    state['verification'] = verification
    return state
