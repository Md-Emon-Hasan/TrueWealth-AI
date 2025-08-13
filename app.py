from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from core.workflow import get_workflow_app
from core.state import initialize_state
from dotenv import load_dotenv
import time

app = Flask(__name__)
load_dotenv()

ai_workflow = get_workflow_app()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    session_id = request.json.get('session_id', 'default')
    
    if not hasattr(app, 'conversation_states'):
        app.conversation_states = {}
    
    if session_id not in app.conversation_states:
        app.conversation_states[session_id] = initialize_state()
    
    state = app.conversation_states[session_id]
    
    # Simulate AI thinking animation
    time.sleep(0)
    
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

if __name__ == '__main__':
    app.run(debug=True)