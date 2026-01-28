from logger import log
from config import AGENT_NAME
from memory import load_state, save_state
from datetime import datetime, timedelta
import traceback

# ---------- TASK DEFINITIONS ----------

def heartbeat_task(state):
    count = state.get("heartbeat_count", 0) + 1
    state["heartbeat_count"] = count
    log(f"{AGENT_NAME} heartbeat #{count}")

def status_task(state):
    log(f"{AGENT_NAME} status OK")

def unstable_task(state):
    raise RuntimeError("Simulated task failure")

# ---------- TASK REGISTRY WITH FAILURE POLICY ----------

TASK_REGISTRY = [
    {
        "name": "heartbeat",
        "priority": 1,
        "cooldown_seconds": 0,
        "max_retries": 0,
        "task": heartbeat_task
    },
    {
        "name": "status",
        "priority": 5,
        "cooldown_seconds": 15,
        "max_retries": 1,
        "task": status_task
    },
    {
        "name": "unstable",
        "priority": 10,
        "cooldown_seconds": 10,
        "max_retries": 3,
        "task": unstable_task
    }
]

# ---------- TASK DISPATCHER WITH RETRIES & BACKOFF ----------

def run_all_tasks():
    state = load_state()
    now = datetime.now()

    sorted_tasks = sorted(TASK_REGISTRY, key=lambda t: t["priority"])

    for task_info in sorted_tasks:
        name = task_info["name"]
        task_fn = task_info["task"]
        cooldown = task_info["cooldown_seconds"]
        max_retries = task_info["max_retries"]

        # Disabled task check
        if state.get(f"disabled_{name}"):
            continue

        last_run_key = f"last_run_{name}"
        last_run_time = state.get(last_run_key)

        if last_run_time:
            last_run_time = datetime.fromisoformat(last_run_time)
            if now - last_run_time < timedelta(seconds=cooldown):
                continue

        retry_key = f"retry_count_{name}"
        retries = state.get(retry_key, 0)

        try:
            task_fn(state)

            # Success resets retries
            state[retry_key] = 0
            state[last_run_key] = now.isoformat()

        except Exception as e:
            retries += 1
            state[retry_key] = retries

            log(f"[ERROR] Task '{name}' failed ({retries}/{max_retries}): {e}")
            log(traceback.format_exc())

            # Exponential backoff
            backoff = cooldown * (2 ** retries)
            state[last_run_key] = (now + timedelta(seconds=backoff)).isoformat()

            # Escalation: disable task
            if retries >= max_retries:
                state[f"disabled_{name}"] = True
                log(f"[ESCALATION] Task '{name}' disabled after repeated failures")

    save_state(state)

