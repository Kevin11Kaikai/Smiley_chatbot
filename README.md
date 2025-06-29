﻿# Smiley_chatbot

SMILEY chatbot is a Flask-based mental health conversational bot that supports multiple decision trees (psychological test/conversation flows). It features a modern web chat interface and allows easy customization of conversation flows via JSON files. The project can optionally use OpenAI GPT to refine bot messages for a more youth-friendly tone.

## Features

- Supports multiple psychological test/conversation flows (customizable via JSON decision trees)
- Local user profile storage, multi-session support
- Modern web chat interface
- Optional OpenAI GPT-3.5 integration for message refinement

## Project Structure

```
smiley_chatbot/
├── app_debug.py           # Main Flask app entry point
├── decision_engine.py     # Decision tree engine
├── gpt_refiner.py         # OpenAI GPT message refiner
├── requirements.txt       # Python dependencies
├── templates/
│   └── chat.html          # Frontend chat page
├── decision_trees/
│   ├── Candice_test.json
│   └── ...                # Other decision trees
├── data/                  # User data (gitignored)
├── logs/                  # Logs (gitignored)
└── ...
```

## Requirements

- Python 3.7+
- Flask
- openai

Install dependencies:
```bash
pip install -r requirements.txt
```

## OpenAI API Key Setup (Important!)

If you want to use the GPT-powered message refinement, you must add your own OpenAI API Key in `gpt_refiner.py`:

1. Open `gpt_refiner.py`.
2. Replace the API key string in this line:
   ```python
   client = OpenAI(api_key="sk-...your-key-here...")
   ```
   with your own OpenAI API Key.

**Security tip:**  
For better security, you can set your API key as an environment variable and change the code to:
```python
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
```
Then set the environment variable in your shell:
```sh
export OPENAI_API_KEY=sk-...your-key-here...
```
(on Windows: `set OPENAI_API_KEY=sk-...your-key-here...`)

If you do not set a valid API key, the chatbot will not be able to use GPT-based message refinement, but the basic flow will still work.

## How to Run

### 1. Start the Service

You can specify the default decision tree via command line:

```bash
python app_debug.py --DecisionTrees decision_trees/Candice_test.json
```

- If the frontend does not specify a `tree_name`, this default will be used.
- You can also switch trees dynamically by passing `tree_name` from the frontend.

### 2. Access the Web Interface

Open your browser and go to [http://localhost:5000/](http://localhost:5000/) to start chatting.

### 3. Switch/Customize Decision Trees

- All decision tree files are in the `decision_trees/` directory (JSON format).
- You can create your own flows by following the structure of `Candice_test.json` or `Cesar_Reject_Negativity_test.json`.
- Supported node types: `prompt` (user input), `menu` (multiple choice), `statement` (bot statement), etc.

### 4. Logs and User Data

- Chat logs are saved in the `logs/` directory (auto-created, gitignored).
- User profiles are saved in the `data/` directory (gitignored).

## Contributing

Contributions, issues, and new decision tree flows are welcome! Feel free to open a PR or issue.

---

## FAQ

- **Q: Why can't I access the chat at port 5000?**  
  **A:** Make sure the Flask server is running and check your terminal for any errors.

- **Q: How do I create my own decision tree?**  
  **A:** Use the JSON format in the `decision_trees/` directory as a template and add your own nodes and flows.

- **Q: How do I securely set my OpenAI API Key?**  
  **A:** Store your key in an environment variable and read it in `gpt_refiner.py` using `os.environ.get('OPENAI_API_KEY')`.

---

## License

MIT License
