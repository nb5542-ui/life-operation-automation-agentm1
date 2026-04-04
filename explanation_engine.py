from logger import log


def explain_goal_selection(state):

    goals = state.get("goals", [])
    active_id = state.get("active_goal_id")

    if not goals or not active_id:
        return

    active_goal = next(
        (g for g in goals if g.get("goal_id") == active_id),
        None
    )

    if not active_goal:
        return

    active_score = active_goal.get("score", 0)

    # compare with others
    comparisons = []

    for g in goals:
        if g.get("goal_id") == active_id:
            continue

        comparisons.append(
            f"{g.get('goal_id')}={g.get('score', 0)}"
        )

    comparison_str = ", ".join(comparisons)

    log("\n[DECISION EXPLANATION]")
    log(f"Selected Goal: {active_goal.get('description')}")
    log(f"Score: {active_score}")
    log(f"Compared against: {comparison_str}")
    log(
        f"Type Weight: {active_goal.get('normalized_type')} "
        f"(weight={active_goal.get('priority_weight')})"
    )
    log("")