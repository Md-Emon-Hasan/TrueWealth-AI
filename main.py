from core.workflow import get_workflow_app
from core.state import initialize_state

def main():
    """Live test interface: simulates conversation"""
    app = get_workflow_app()
    conversation_state = initialize_state()
    
    print("=== CONVERSATION LOG ===")
    while True:
        query = input("Client: ").strip()
        if query.lower() == 'exit':
            print("=== Consultation Ended ===")
            break

        conversation_state.update({
            "question": query,
            "generation": "",
            "documents": [],
            "source": "",
            "retry_count": 0
        })

        result = app.invoke(conversation_state)
        conversation_state.update(result)

        print(f"\nClient: {query}")
        print(f"Consultant: {conversation_state['generation']}\n")

if __name__ == "__main__":
    main()