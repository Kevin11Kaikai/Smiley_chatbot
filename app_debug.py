from flask import Flask, request, jsonify, render_template, session
from decision_engine import DecisionEngine
import traceback
import logging
import os
from datetime import datetime
import argparse

# --- Logging Setup ---
if not os.path.exists('logs'):
    os.makedirs('logs')
log_filename = f"logs/chatbot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("="*50)
logger.info("CHATBOT MULTI-TREE APP STARTED")
logger.info(f"Log file: {log_filename}")
logger.info("="*50)

# --- Flask App Setup ---
app = Flask(__name__)
# A secret key is needed for Flask to manage sessions
app.secret_key = os.urandom(24) 

# Save the engine and current tree_name for each session.
engines = {}

# global default decision tree path (can be set via command line argument)
DEFAULT_TREE_PATH = None

def get_engine(session_id, tree_name): # id of session and name of tree
    """
    Get or create the engine for the current session. If the tree name changes, switch to the new tree.
    """
    filepath = os.path.join("decision_trees", f"{tree_name}.json") # path of the tree file
    profile_path = os.path.join("data", f"profile_{session_id}.json") # path of the profile file

    if not os.path.exists(filepath): # check if the tree file exists
        raise FileNotFoundError(f"The specified tree file does not exist: {filepath}")

    if session_id not in engines: # check if the session exists
        logger.info(f"Creating new engine for session '{session_id}' with tree '{tree_name}'")
        engines[session_id] = {
            "engine": DecisionEngine(tree_filepath=filepath, user_profile_path=profile_path),
            "tree_name": tree_name
        }
    else:
        # If the tree name changes, switch to the new tree.
        if engines[session_id]["tree_name"] != tree_name:
            logger.info(f"Switching tree for session '{session_id}' to '{tree_name}'")
            engines[session_id]["engine"].switch_tree(filepath)
            engines[session_id]["tree_name"] = tree_name

    return engines[session_id]["engine"] # return the engine

@app.route('/') # route to the main chat page
def index():
    """
    Serves the main chat page. We can add links here to test different trees.
    """
    # For simplicity, we'll have separate pages or query params to start different chats.
    # Example: /?test=Candice_test
    return render_template('chat.html') # render the chat page

@app.route('/init', methods=['POST']) # route to the init page
def init():
    """
    Initialize the session, the frontend needs to pass the tree_name.
    """
    try:
        data = request.get_json() # get the data from the request
        tree_name = data.get("tree_name") # get the tree name from the data
        # if tree_name is not provided, use the default decision tree specified via command line argument
        if not tree_name:
            global DEFAULT_TREE_PATH
            if DEFAULT_TREE_PATH:
                # only get the file name without extension as tree_name
                tree_name = os.path.splitext(os.path.basename(DEFAULT_TREE_PATH))[0]
            else:
                return jsonify({"success": False, "error": "tree_name not provided and no default specified via --DecisionTrees"}), 400

        session['id'] = session.get('id', os.urandom(16).hex()) # generate a random session id
        session_id = session['id'] # get the session id

        engine = get_engine(session_id, tree_name) # get the engine
        initial_messages = engine.process_turn() # get the initial messages

        logger.info(f"Session '{session_id}' initialized with tree '{tree_name}'.") # log the session initialization
        return jsonify({"success": True, "response": initial_messages}) # return the initial messages
    except FileNotFoundError as e:
        logger.error(f"File not found error in init: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error in init: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "An internal error occurred."}), 500

@app.route('/chat', methods=['POST']) # route to the chat page
def chat():
    """
    Handle the chat request
    """
    try:
        session_id = session.get('id') # get the session id
        if not session_id or session_id not in engines: # check if the session exists
            return jsonify({"success": False, "error": "Session not initialized. Please start a new chat."}), 400

        engine = engines[session_id]["engine"] # get the engine
        data = request.get_json() # get the data from the request
        user_input = data.get("user_input") # get the user input from the data

        logger.info(f"Chat request for session '{session_id}': '{user_input}'") # log the chat request
        response_messages = engine.process_turn(user_input) # get the response messages
        logger.info(f"Responding to session '{session_id}' with {len(response_messages)} messages.") # log the response
        return jsonify({"success": True, "response": response_messages}) # return the response messages

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}\n{traceback.format_exc()}") # log the error
        return jsonify({"success": False, "error": "An internal error occurred."}), 500 # return the error

@app.route('/reset', methods=['POST']) # route to the reset page
def reset():
    """
    Reset the current session
    """
    session_id = session.get('id') # get the session id
    if session_id and session_id in engines: # check if the session exists
        del engines[session_id] # delete the engine
        logger.info(f"Session '{session_id}' has been reset.") # log the reset
    session.clear()
    return jsonify({"success": True, "message": "Conversation has been reset."})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SMILEY Chatbot Debug App')
    parser.add_argument('--DecisionTrees', type=str, help='Path to the default decision tree JSON file')
    args = parser.parse_args()
    if args.DecisionTrees:
        DEFAULT_TREE_PATH = args.DecisionTrees
    app.run(debug=True, host='0.0.0.0', port=5000)