import json
import os

MEMORY_FILE = "agent_state.json"

def load_state():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as file:
        return json.load(file)

def save_state(state):
    with open(MEMORY_FILE, "w") as file:
        json.dump(state, file, indent=4)
