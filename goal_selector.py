from datetime import datetime, timedelta
from logger import log

FOCUS_DURATION_SECONDS = 20


def select_active_goal(state):

    goals = state.get("goals", [])
    now = datetime.now()

    # 🔍 Find BEST goal first
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

    current_id = state.get("active_goal_id")

    current_goal = next(
        (g for g in goals if g.get("goal_id") == current_id),
        None
    )

    current_score = current_goal.get("score", -1) if current_goal else -1

    # 🔒 CHECK LOCK
    lock_until = state.get("focus_locked_until")

    if lock_until:
        try:
            lock_time = datetime.fromisoformat(lock_until)

            if now < lock_time:
                # 🚨 ONLY SWITCH IF MUCH BETTER
                if best_score > current_score * 1.2:
                    log("[FOCUS OVERRIDE] Higher priority goal detected")
                else:
                    return

        except Exception:
            pass

    # 🧠 APPLY SELECTION
    state["active_goal_id"] = best_goal["goal_id"]

    state["focus_goal_id"] = best_goal["goal_id"]
    state["focus_locked_until"] = (
        now + timedelta(seconds=FOCUS_DURATION_SECONDS)
    ).isoformat()

    log(f"[FOCUS LOCK] Locked on: {best_goal.get('description')} (score={best_score})")