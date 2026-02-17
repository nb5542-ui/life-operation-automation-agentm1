from datetime import datetime, timedelta
import traceback

from logger import log
from config import AGENT_NAME
from memory import load_state, save_state
from events import detect_file_event
from decisions import decide_intents
from policies import policy_allows_intent, policy_allows_override
from actions import ACTION_REGISTRY


# ======================================================
# CONTROL HELPERS
# ======================================================

def is_globally_paused(state):
    return state.get("global_pause", False)

def is_task_paused(state, task_name):
    return state.get(f"paused_{task_name}", False)


# ======================================================
# PLANNING (DAY 5)
# ======================================================

def generate_plan_for_goal(goal):
    plan_id = f"plan_{goal['goal_id']}"

    steps = [
        {
            "step_id": f"{plan_id}_step1",
            "action": "analyze_file",
            "payload": goal.get("related_intent", {}),
            "status": "pending"
        },
        {
            "step_id": f"{plan_id}_step2",
            "action": "log_result",
            "payload": {"message": f"Analysis completed for {goal['goal_id']}"},
            "status": "pending"
        }
    ]

    return {
        "plan_id": plan_id,
        "goal_id": goal["goal_id"],
        "created_at": datetime.now().isoformat(),
        "steps": steps,
        "status": "active"
    }
def execute_plan_step(state, agent):
    plans = state.get("plans", [])
    goals = state.get("goals", [])

    # Find active plan
    active_plan = next((p for p in plans if p["status"] == "active"), None)

    if not active_plan:
        return

    # Find next pending step
    step = next((s for s in active_plan["steps"] if s["status"] == "pending"), None)

    if not step:
        # No pending steps → mark plan & goal completed
        active_plan["status"] = "completed"

        goal_id = active_plan["goal_id"]
        for goal in goals:
            if goal["goal_id"] == goal_id:
                goal["status"] = "completed"
                goal["updated_at"] = datetime.now().isoformat()
                log(f"[GOAL COMPLETED] {goal['description']}")

        return

    # Convert step to intent
    intent_queue = state.get("intent_queue", [])

    intent_queue.append({
        "action": step["action"],
        "payload": step["payload"]
    })

    state["intent_queue"] = intent_queue

    step["status"] = "completed"

    log(f"[PLAN] Executed step: {step['step_id']}")



# ======================================================
# GOAL MANAGEMENT (DAY 3 + DAY 5)
# ======================================================

def activate_next_goal(state, agent):
    goals = state.get("goals", [])
    plans = state.get("plans", [])

    has_active = any(
        g["status"] == "active" and g["owner_agent_id"] == agent.agent_id
        for g in goals
    )

    if has_active:
        return

    for goal in goals:
        if goal["status"] == "pending" and goal["owner_agent_id"] == agent.agent_id:
            goal["status"] = "active"
            goal["updated_at"] = datetime.now().isoformat()
            log(f"[GOAL ACTIVATED] {goal['description']}")

            # 🔑 DAY 5: Generate plan
            plan = generate_plan_for_goal(goal)
            plans.append(plan)

            state["plans"] = plans
            return


# ======================================================
# CORE TASKS
# ======================================================

def heartbeat_task(state):
    count = state.get("heartbeat_count", 0) + 1
    state["heartbeat_count"] = count
    log(f"{AGENT_NAME} heartbeat #{count}")

def status_task(state):
    log(f"{AGENT_NAME} status OK")


# ======================================================
# FAILURE TEST TASK
# ======================================================

def unstable_task(state):
    raise RuntimeError("Simulated task failure")


# ======================================================
# EVENT SYSTEM TASKS
# ======================================================

def event_listener_task(state):
    detect_file_event(state)

def event_handler_task(state, agent):
    queue = state.get("event_queue", [])

    if not queue:
        return

    event = queue.pop(0)
    log(f"[EVENT HANDLER] Processing event: {event['type']}")

    intents, goals = decide_intents(event, state, agent)

    # ----- INTENTS -----
    intent_queue = state.get("intent_queue", [])
    intent_queue.extend(intents)
    state["intent_queue"] = intent_queue

    # ----- GOALS + MISSIONS -----
    goal_store = state.get("goals", [])
    missions = state.get("missions", {})

    for goal in goals:
        goal_dict = goal.__dict__
        goal_store.append(goal_dict)

        mission_id = goal_dict.get("mission_id")
        if mission_id:
            missions.setdefault(mission_id, []).append(goal_dict["goal_id"])

    state["goals"] = goal_store
    state["missions"] = missions
    state["event_queue"] = queue


# ======================================================
# RECOVERY TASK
# ======================================================

def recovery_task(state):
    now = datetime.now()

    for key in list(state.keys()):
        if key.startswith("disabled_") and not key.startswith("disabled_at_") and state.get(key):
            task_name = key.replace("disabled_", "")
            disabled_at_key = f"disabled_at_{task_name}"
            disabled_at = state.get(disabled_at_key)

            if not disabled_at:
                state[disabled_at_key] = now.isoformat()
                continue

            disabled_time = datetime.fromisoformat(disabled_at)

            if now - disabled_time > timedelta(seconds=60):
                log(f"[RECOVERY] Re-enabling task '{task_name}'")

                state[f"disabled_{task_name}"] = False
                state.pop(f"retry_count_{task_name}", None)
                state.pop(disabled_at_key, None)


# ======================================================
# INTENT → ACTION EXECUTION
# ======================================================

def intent_executor_task(state):
    intents = state.get("intent_queue", [])

    if not intents:
        return

    intent = intents.pop(0)

    if not policy_allows_intent(intent, state):
        if policy_allows_override(state):
            log(f"[OVERRIDE] Forcing action execution: {intent.get('action')}")
        else:
            log(f"[INTENT BLOCKED] {intent.get('action')}")
            state["intent_queue"] = intents
            return

    action_name = intent.get("action")
    payload = intent.get("payload", {})

    log(f"[INTENT] Executing action: {action_name}")

    action_fn = ACTION_REGISTRY.get(action_name)

    if not action_fn:
        log(f"[ACTION ERROR] No executor registered for action '{action_name}'")
    else:
        action_fn(payload, state)

    state["intent_queue"] = intents


# ======================================================
# HEALTH REPORT
# ======================================================

def health_report_task(state):
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


# ======================================================
# TASK REGISTRY
# ======================================================

TASK_REGISTRY = [
    {"name": "heartbeat", "priority": 1, "cooldown_seconds": 0, "max_retries": 0, "task": heartbeat_task},
    {"name": "event_listener", "priority": 2, "cooldown_seconds": 2, "max_retries": 0, "task": event_listener_task},
    {"name": "event_handler", "priority": 3, "cooldown_seconds": 1, "max_retries": 0, "task": event_handler_task},
    {"name": "intent_executor", "priority": 4, "cooldown_seconds": 1, "max_retries": 1, "task": intent_executor_task},
    {
    "name": "plan_executor",
    "priority": 5,
    "cooldown_seconds": 1,
    "max_retries": 1,
    "task": execute_plan_step
},

    {"name": "status", "priority": 5, "cooldown_seconds": 15, "max_retries": 1, "task": status_task},
    
    {"name": "recovery", "priority": 90, "cooldown_seconds": 30, "max_retries": 0, "task": recovery_task},
    {"name": "health_report", "priority": 100, "cooldown_seconds": 30, "max_retries": 0, "task": health_report_task},
]


# ======================================================
# TASK DISPATCHER
# ======================================================

def run_all_tasks(agent, missions):
    state = load_state()
    now = datetime.now()

    # 🔑 DAY 3 + 5: Goal activation + plan generation
    activate_next_goal(state, agent)

    if is_globally_paused(state):
        log("[CONTROL] Global pause is ON. Skipping all tasks.")
        save_state(state)
        return

    for task_info in sorted(TASK_REGISTRY, key=lambda t: t["priority"]):
        name = task_info["name"]
        task_fn = task_info["task"]
        cooldown = task_info["cooldown_seconds"]
        max_retries = task_info["max_retries"]

        if is_task_paused(state, name):
            continue

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
            if name in ["event_handler", "plan_executor"]:
                task_fn(state, agent)
            else:
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
                state[f"disabled_at_{name}"] = now.isoformat()
                log(f"[ESCALATION] Task '{name}' disabled after repeated failures")

    save_state(state)
