from datetime import datetime, timedelta
from logger import log

FOCUS_DURATION_SECONDS = 20


def select_active_goal(state):

    goals = state.get("goals", [])
    now = datetime.now()

    # 🔒 1. CHECK EXISTING LOCK
    lock_until = state.get("focus_locked_until")

    if lock_until:
        try:
            lock_time = datetime.fromisoformat(lock_until)

            if now < lock_time:
                return  # still locked → do nothing

        except Exception:
            pass  # fallback if corrupted

    # 🔍 2. NORMAL SELECTION
    best_goal = None
    best_score = -1

    for g in goals:
        if g.get("status") in ["completed", "failed"]:
            continue

        score = g.get("score", 0)

        if score > best_score:
            best_score = score
            best_goal = g

    if not best_goal:
        return

    # 🧠 3. SET ACTIVE GOAL
    state["active_goal_id"] = best_goal["goal_id"]

    # 🔒 4. APPLY FOCUS LOCK
    state["focus_goal_id"] = best_goal["goal_id"]
    state["focus_locked_until"] = (
        now + timedelta(seconds=FOCUS_DURATION_SECONDS)
    ).isoformat()

    log(f"[FOCUS LOCK] Locked on: {best_goal.get('description')} for 20s")