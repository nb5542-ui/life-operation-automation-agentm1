import json
import os

MEMORY_FILE = "agent_state.json"


def create_default_state():
    return {
        "goals": [],
        "plans": [],
        "missions": {},
        "intent_queue": [],
        "event_queue": [],
        "active_goal_id": None,

        # 🔒 Focus Lock fields
        "focus_locked_until": None,
        "focus_goal_id": None,

        # system
        "heartbeat_count": 0,
        "global_pause": False
    }


def load_state():

    if not os.path.exists(MEMORY_FILE):
        return create_default_state()

    with open(MEMORY_FILE, "r") as file:
        state = json.load(file)

    # ✅ ensure missing keys are added (important)
    default = create_default_state()

    for key, value in default.items():
        if key not in state:
            state[key] = value

    return state


def save_state(state):
    with open(MEMORY_FILE, "w") as file:
        json.dump(state, file, indent=4)