from logger import log
from datetime import datetime


def get_time_bucket():
    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 24:
        return "night"
    else:
        return "late_night"


def update_habit_stats(state):

    goals = state.get("goals", [])
    habit_stats = state.get("habit_stats", {})
    processed = set(state.get("habit_processed_goals", []))

    for g in goals:
        goal_id = g.get("goal_id")

        if goal_id in processed:
            continue

        goal_type = g.get("normalized_type", "misc")
        status = g.get("status")
        time_bucket = g.get("time_bucket", get_time_bucket())

        if goal_type not in habit_stats:
            habit_stats[goal_type] = {}

        if time_bucket not in habit_stats[goal_type]:
            habit_stats[goal_type][time_bucket] = {
                "success": 0,
                "fail": 0
            }

        if status == "completed":
            habit_stats[goal_type][time_bucket]["success"] += 1
            processed.add(goal_id)

        elif status == "failed":
            habit_stats[goal_type][time_bucket]["fail"] += 1
            processed.add(goal_id)

    state["habit_stats"] = habit_stats
    state["habit_processed_goals"] = list(processed)

    log(f"[HABIT] Updated stats: {habit_stats}")
def get_habit_weight(goal, state):

    habit_stats = state.get("habit_stats", {})
    goal_type = goal.get("normalized_type", "misc")
    time_bucket = goal.get("time_bucket", "unknown")

    stats = habit_stats.get(goal_type, {}).get(time_bucket)

    if not stats:
        return 1.0

    success = stats.get("success", 0)
    fail = stats.get("fail", 0)

    total = success + fail

    if total == 0:
        return 1.0

    success_rate = success / total

    # 🔥 more aggressive scaling
    return 0.6 + (success_rate * 0.8)