# agents/yfinance.py
from tools.search_tools import get_yfinance_tool
from core.state import AgentState
from langchain.schema import Document

class YFinanceAgent:
    @staticmethod
    def process(state: AgentState) -> AgentState:
        content = get_yfinance_tool().run(state['question'])
        state.update({
            "documents": [Document(page_content=content)],
            "yfinance_attempted": True,
            "source": 'yfinance',
            "conversation_history": state['conversation_history'] + ["AI: Checking market data..."]
        })
        return state