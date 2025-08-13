# agents/llm.py
from tools.llm_client import get_llm
from core.state import AgentState

class LLMAgent:
    @staticmethod
    def process(state: AgentState) -> AgentState:
        ctx = "\n".join(state['conversation_history'])
        prompt = f"""As a financial advisor, respond to:

History: {ctx}
Question: {state['question']}

2-3 sentence professional answer:"""
        
        res = get_llm().invoke(prompt).content
        state.update({
            "generation": res.strip(),
            "source": "llm_knowledge",
            "llm_attempted": True,
            "conversation_history": state['conversation_history'] + [
                f"Client: {state['question']}",
                f"Advisor: {res.strip()}"
            ]
        })
        return state