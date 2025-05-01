from flask import Flask, request
import os
import importlib
import inspect
import json
import uuid  # For generating unique session IDs

# In-memory session store
sessions = {}

app = Flask(__name__)

class Manager:
    def __init__(self):
        # Dictionary to hold dynamically loaded agents by filename
        self.agents = {}
        self.load_agents()

    def load_agents(self):
        """
        Dynamically loads all agents in the agents folder using the filename as the key,
        and populates the agents dictionary with the agent instances and their descriptions.
        """
        agents_path = os.path.join(os.path.dirname(__file__), 'agents')
        for filename in os.listdir(agents_path):
            if filename.endswith('.py') and filename != '__init__.py':
                agent_name = filename[:-3]  # Remove the '.py' extension
                module_name = f'agents.{agent_name}'
                module = importlib.import_module(module_name)

                # Find the first class in the module to use as the agent
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ == module_name:
                        agent_instance = obj()
                        description = getattr(agent_instance, "description", "No description provided")
                        self.agents[agent_name] = {
                            "instance": agent_instance,
                            "description": description
                        }
                        break

    def get_agents_list(self):
        """
        Returns a list of all loaded agents with their descriptions.
        """
        return [{"name": name, "description": data["description"]} for name, data in self.agents.items()]

    def get_agent_by_name(self, name):
        """
        Retrieves an agent instance by filename-based name if it exists in the loaded agents.
        """
        return self.agents.get(name, {}).get("instance")


manager = Manager()

# System-prompt definition: instructs the AI to interpret user prompts
def generate_system_prompt():
    agents_list = "\n".join([f"{i+1}. {agent['name']} - {agent['description']}" for i, agent in enumerate(manager.get_agents_list())])
    system_prompt = f"""
You are an assistant capable of analyzing news articles for trustworthiness. 
You will use the following agents to evaluate the article based on different criteria:
{agents_list}

Your task is to:
1. Provide the article to all agents.
2. Collect RAG (Retrieval-Augmented Generation) data from each agent.
3. Combine the RAG data and analyze it to generate a trustworthiness score and detailed explanation.

Always ensure the analysis is comprehensive and includes metadata evaluation, factual consistency, bias detection, and linguistic analysis.
"""
    return system_prompt.strip()

SYSTEM_PROMPT = generate_system_prompt()

@app.route("/infofactagents", methods=["POST"])
def process_prompt():
    session_id = request.form.get('SessionID', '').strip()
    incoming_msg = request.form.get('Body', '').strip()
    selected_agents = request.form.get('Agents', '').split(',')  # Get selected agents from the request
    response_text = ""

    # Create a new session if no SessionID is provided
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"history": []}  # Example: Store session-specific data like history

    # Retrieve session data
    session_data = sessions[session_id]

    if incoming_msg == "list_agents":
        agents_list = manager.get_agents_list()
        response_text = "Available agents:\n" + "\n".join([f"{agent['name']} - {agent['description']}" for agent in agents_list])
        return {"SessionID": session_id, "Response": response_text}, 200

    elif incoming_msg == "system_prompt":
        return {"SessionID": session_id, "Response": SYSTEM_PROMPT}, 200

    else:
        try:
            # Check if no agents were selected
            if not selected_agents or selected_agents == ['']:
                return {"SessionID": session_id, "Error": "No agents selected. Please select at least one agent."}, 400

            # Process the article with selected agents
            formatted_output = []
            formatted_output.append(f"📰 **Article**\n\n{incoming_msg}\n")

            for agent_name in selected_agents:
                agent_data = manager.agents.get(agent_name)
                if agent_data and hasattr(agent_data["instance"], "process_article"):
                    result = agent_data["instance"].process_article(incoming_msg)
                    formatted_output.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n**{agent_name}**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{result}\n")

            # Combine formatted output
            response_text = "\n".join(formatted_output)

            # Optionally store the response in the session history
            session_data["history"].append({"input": incoming_msg, "output": response_text})

        except Exception as e:
            response_text = f"Error processing your prompt: {str(e)}"

        return {"SessionID": session_id, "Response": response_text}, 200

import requests
if __name__ == "__main__":
    try:
        # Fetch and display the public IP address
        public_ip = requests.get("https://api.ipify.org").text
        print(f"Backend is accessible at public IP address: {public_ip}")
    except requests.RequestException as e:
        print(f"Failed to fetch public IP address: {e}")

    # Start the Flask application
    app.run(host="0.0.0.0", port=5000)