# agents/generator.py
from tools.llm_client import get_llm
from core.state import AgentState

class ResponseGenerator:
    @staticmethod
    def process(state: AgentState) -> AgentState:
        if state['source'] == 'llm_knowledge':
            return state

        if state['documents']:
            content = "\n".join(doc.page_content for doc in state['documents'])
            prompt = f"""Financial advisor response using:
            
Context: {''.join(state['conversation_history'][-3:])}
Question: {state['question']}
Data: {content}

Respond professionally in 2-3 sentences:"""
            
            res = get_llm().invoke(prompt).content
            state.update({
                "generation": res.strip(),
                "conversation_history": state['conversation_history'] + [f"Advisor: {res.strip()}"]
            })
            return state

        state.update({
            "generation": "I need more financial data to advise properly. Please consult an expert.",
            "conversation_history": state['conversation_history'] + ["Advisor: I need more data..."]
        })
        return state