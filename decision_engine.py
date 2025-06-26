import json
import os
from gpt_refiner import refine_text

class DecisionEngine:
    """
    A refactored, data-driven decision engine that processes a chat flow
    based on a single, specified JSON file.
    """
    def __init__(self, tree_filepath="decision_trees/Candice_test.json", user_profile_path="data/user_profile.json"):
        """
        Initializes the engine, loading a specific chat tree and user profile.
        """
        self.tree_data = self.load_tree(tree_filepath)
        if not self.tree_data:
            raise FileNotFoundError(f"Chat tree file not found or is invalid: {tree_filepath}")

        self.nodes = self.tree_data.get("nodes", {})
        self.start_node_id = self.tree_data.get("start_node")
        
        self.profile_path = user_profile_path
        self.profile = self.load_user_profile()
        
        self.current_node_id = self.start_node_id

    def load_tree(self, filepath):
        """
        Loads a single, complete chat tree JSON file.
        """
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def load_user_profile(self):
        """
        Loads the user profile from a file if it exists, otherwise returns an empty dictionary.
        """
        if os.path.exists(self.profile_path):
            with open(self.profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_user_profile(self):
        """
        Saves the current user profile to a file.
        """
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)

    def process_turn(self, user_input=None):
        """
        Processes a single turn of the conversation.
        """
        if user_input:
            node = self.nodes.get(self.current_node_id)
            if not node: return ["Error: Current node not found."]
            node_type = node.get("type")

            if node_type == "prompt":
                self.profile[node["collect"]] = user_input.strip()
                self.save_user_profile()
                self.current_node_id = node.get("next")

            elif node_type == "menu":
                matched = False
                for option in node.get("options", []):
                    # support three types of matching: id, text, source_text (for menu options)
                    if (
                        user_input.strip().lower() == option.get("id", "").lower() or # id is the id of the option
                        user_input.strip().lower() == option.get("text", "").lower() or # text is the text of the option
                        user_input.strip().lower() == option.get("source_text", "").lower() # source_text is the text of the option
                    ):
                        if node.get("collect"):  # if the node has a collect field, save the option to the profile
                            self.profile[node["collect"]] = option.get("source_text") 
                            self.save_user_profile()
                        self.current_node_id = option.get("target_node")
                        matched = True
                        break
                if not matched:
                    return ["I'm sorry, I didn't understand that. Please choose one of the available options."]
        
        messages_to_send = []
        while self.current_node_id:
            node = self.nodes.get(self.current_node_id)
            if not node: break

            node_type = node.get("type")
            
            # Generate the message for the current node
            message_text = ""
            if "source_text" in node:
                # For AI-driven nodes, call the refiner
                message_text = refine_text(node["source_text"], self.profile)
            elif "message" in node:
                # For simple nodes, just format the message
                message_text = node["message"].format(**self.profile)

            if message_text:
                if isinstance(message_text, list):
                    messages_to_send.extend(message_text)
                else:
                    messages_to_send.append(message_text)

            if node_type in ["prompt", "menu"]:
                break
            
            self.current_node_id = node.get("next")
        
        return messages_to_send

    def switch_tree(self, new_tree_filepath):
        """
        Switches to a new decision tree by loading the specified JSON file.
        Resets the conversation state to the new tree's start node.
        """
        new_tree_data = self.load_tree(new_tree_filepath)
        if not new_tree_data:
            raise FileNotFoundError(f"Chat tree file not found or is invalid: {new_tree_filepath}")
        self.tree_data = new_tree_data
        self.nodes = self.tree_data.get("nodes", {})
        self.start_node_id = self.tree_data.get("start_node")
        self.current_node_id = self.start_node_id
