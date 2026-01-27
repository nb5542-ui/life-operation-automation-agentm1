from logger import log
from config import AGENT_NAME
from memory import load_state, save_state
from datetime import datetime, timedelta

# ---------- TASK DEFINITIONS ----------

def heartbeat_task(state):
    count = state.get("heartbeat_count", 0) + 1
    state["heartbeat_count"] = count
    log(f"{AGENT_NAME} heartbeat #{count}")

def status_task(state):
    log(f"{AGENT_NAME} status OK")

# ---------- TASK REGISTRY WITH COOLDOWNS ----------

TASK_REGISTRY = [
    {
        "name": "heartbeat",
        "priority": 1,
        "cooldown_seconds": 0,     # always allowed
        "task": heartbeat_task
    },
    {
        "name": "status",
        "priority": 5,
        "cooldown_seconds": 15,    # once every 15 seconds
        "task": status_task
    }
]

# ---------- TASK DISPATCHER ----------

def run_all_tasks():
    state = load_state()
    now = datetime.now()

    sorted_tasks = sorted(TASK_REGISTRY, key=lambda t: t["priority"])

    for task_info in sorted_tasks:
        task_name = task_info["name"]
        cooldown = task_info["cooldown_seconds"]

        last_run_key = f"last_run_{task_name}"
        last_run_time = state.get(last_run_key)

        if last_run_time:
            last_run_time = datetime.fromisoformat(last_run_time)
            if now - last_run_time < timedelta(seconds=cooldown):
                continue  # cooldown active, skip

        task_info["task"](state)
        state[last_run_key] = now.isoformat()

    save_state(state)


