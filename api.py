from flask import Flask
from flask import request
from flask import jsonify
from core.workflow import get_workflow_app
from core.state import initialize_state
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

ai_workflow = get_workflow_app()
conversation_states = {}

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"error": "Message is required"}), 400
    
    user_input = data['message']
    session_id = data.get('session_id', 'default')
    
    if session_id not in conversation_states:
        conversation_states[session_id] = initialize_state()
    
    state = conversation_states[session_id]
    
    state.update({
        "question": user_input,
        "generation": "",
        "documents": [],
        "source": "",
        "retry_count": 0
    })
    
    result = ai_workflow.invoke(state)
    state.update(result)
    
    return jsonify({
        "response": state['generation'],
        "session_id": session_id,
        "source": state['source']
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)