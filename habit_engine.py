from logger import log


def update_habit_stats(state):

    goals = state.get("goals", [])
    habit_stats = state.get("habit_stats", {})

    for g in goals:
        goal_type = g.get("normalized_type", "misc")
        status = g.get("status")

        if goal_type not in habit_stats:
            habit_stats[goal_type] = {
                "success": 0,
                "fail": 0
            }

        if status == "completed":
            habit_stats[goal_type]["success"] += 1

        elif status == "failed":
            habit_stats[goal_type]["fail"] += 1

    state["habit_stats"] = habit_stats


def get_habit_weight(goal, state):

    habit_stats = state.get("habit_stats", {})
    goal_type = goal.get("normalized_type", "misc")

    stats = habit_stats.get(goal_type)

    if not stats:
        return 1.0

    success = stats.get("success", 0)
    fail = stats.get("fail", 0)

    total = success + fail

    if total == 0:
        return 1.0

    success_rate = success / total

    return 0.7 + (success_rate * 0.6)