from logger import log


def select_active_goal(state):

    goals = state.get("goals", [])

    if not goals:
        return

    best_goal = None
    best_score = -1

    for g in goals:

        if g.get("status") in ["completed", "failed"]:
            continue

        score = g.get("score", 0)

        if score > best_score:
            best_score = score
            best_goal = g

    if best_goal:
        state["active_goal_id"] = best_goal["goal_id"]

        log(
            f"[GOAL SELECTED] {best_goal.get('description')} score={best_score}"
        )