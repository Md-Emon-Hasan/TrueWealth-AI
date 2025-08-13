# main.py
from dotenv import load_dotenv
from core.workflow import get_workflow_app
from core.state import initialize_state

from dotenv import load_dotenv
load_dotenv()

def main():
    load_dotenv()
    app = get_workflow_app()
    state = initialize_state()

    print("=== FINANCIAL ADVISOR ===")
    while True:
        query = input("\nClient: ").strip()
        if query.lower() == 'exit':
            print("\n=== Session Ended ===")
            break

        state.update({
            "question": query,
            "generation": "",
            "documents": [],
            "source": "",
            "retry_count": 0
        })

        result = app.invoke(state)
        state.update(result)
        print(f"\nAdvisor: {state['generation']}\n")

if __name__ == "__main__":
    main()