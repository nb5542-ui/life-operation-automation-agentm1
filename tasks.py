from logger import log
from config import AGENT_NAME
from events import detect_file_event

from memory import load_state, save_state
from datetime import datetime, timedelta
import traceback

# ---------- TASK DEFINITIONS ----------
def is_globally_paused(state):
    return state.get("global_pause", False)

def is_task_paused(state, task_name):
    return state.get(f"paused_{task_name}", False)
def event_listener_task(state):
    detect_file_event(state)
def event_handler_task(state):
    queue = state.get("event_queue", [])

    if not queue:
        return

    event = queue.pop(0)

    log(f"[EVENT HANDLER] Processing event: {event['type']}")

    if event["type"] == "file_changed":
        log(f"[EVENT HANDLER] File changed: {event['file']}")

    state["event_queue"] = queue

    if not queue:
        return

    event = queue.pop(0)

    if event["type"] == "file_changed":
        log(f"[EVENT HANDLER] Handling file change for {event['file']}")

    state["event_queue"] = queue



def heartbeat_task(state):
    count = state.get("heartbeat_count", 0) + 1
    state["heartbeat_count"] = count
    log(f"{AGENT_NAME} heartbeat #{count}")

def status_task(state):
    log(f"{AGENT_NAME} status OK")

def unstable_task(state):
    raise RuntimeError("Simulated task failure")

def health_report_task(state):
    """
    Summarizes system health and task status.
    """
    disabled_tasks = [
        key.replace("disabled_", "")
        for key, value in state.items()
        if key.startswith("disabled_") and value
    ]

    failure_counts = {
        key.replace("retry_count_", ""): value
        for key, value in state.items()
        if key.startswith("retry_count_") and value > 0
    }

    log("---- SYSTEM HEALTH REPORT ----")
    log(f"Disabled tasks: {disabled_tasks or 'None'}")
    log(f"Tasks with failures: {failure_counts or 'None'}")
    log("--------------------------------")


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
    },
    {
    "name": "health_report",
    "priority": 100,          # lowest priority
    "cooldown_seconds": 30,   # once every 30 seconds
    "max_retries": 0,
    "task": health_report_task
},
{
    "name": "event_listener",
    "priority": 2,
    "cooldown_seconds": 2,
    "max_retries": 0,
    "task": event_listener_task
},
{
    "name": "event_handler",
    "priority": 3,
    "cooldown_seconds": 1,
    "max_retries": 0,
    "task": event_handler_task
}


]

# ---------- TASK DISPATCHER WITH RETRIES & BACKOFF ----------

def run_all_tasks():
    state = load_state()
    now = datetime.now()

    # -------- GLOBAL PAUSE --------
    if is_globally_paused(state):
        log("[CONTROL] Global pause is ON. Skipping all tasks.")
        save_state(state)
        return

    sorted_tasks = sorted(TASK_REGISTRY, key=lambda t: t["priority"])

    for task_info in sorted_tasks:
        name = task_info["name"]
        task_fn = task_info["task"]
        cooldown = task_info["cooldown_seconds"]
        max_retries = task_info["max_retries"]

        # -------- PER-TASK PAUSE --------
        if is_task_paused(state, name):
            log(f"[CONTROL] Task '{name}' is paused. Skipping.")
            continue

        # -------- DISABLED TASK CHECK --------
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
            state[retry_key] = 0
            state[last_run_key] = now.isoformat()

        except Exception as e:
            retries += 1
            state[retry_key] = retries
            log(f"[ERROR] Task '{name}' failed ({retries}/{max_retries}): {e}")
            log(traceback.format_exc())

            backoff = cooldown * (2 ** retries)
            state[last_run_key] = (now + timedelta(seconds=backoff)).isoformat()

            if retries >= max_retries:
                state[f"disabled_{name}"] = True
                log(f"[ESCALATION] Task '{name}' disabled after repeated failures")

    save_state(state)


