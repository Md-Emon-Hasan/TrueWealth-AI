# agents/duckduckgo.py
from tools.search_tools import get_ddg_tool
from core.state import AgentState
from langchain.schema import Document

class DuckDuckGoAgent:
    @staticmethod
    def process(state: AgentState) -> AgentState:
        content = get_ddg_tool().run(state['question'])
        state.update({
            "documents": [Document(page_content=content)],
            "ddg_attempted": True,
            "source": 'duckduckgo',
            "conversation_history": state['conversation_history'] + ["AI: Searching web..."]
        })
        return state