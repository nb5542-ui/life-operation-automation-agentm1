from logger import log


def log_goal_table(state):

    goals = state.get("goals", [])

    if not goals:
        log("[INSIGHT] No goals available")
        return

    log("\n====== GOAL DASHBOARD ======")

    for g in goals:
        log(
            f"{g.get('goal_id')} | "
            f"{g.get('status')} | "
            f"score={g.get('score')} | "
            f"type={g.get('normalized_type')}"
        )

    log("============================\n")


def log_active_goal(state):

    goal_id = state.get("active_goal_id")

    if not goal_id:
        log("[INSIGHT] No active goal")
        return

    goal = next(
        (g for g in state.get("goals", []) if g["goal_id"] == goal_id),
        None
    )

    if goal:
        log(
            f"[ACTIVE GOAL] {goal.get('description')} "
            f"(score={goal.get('score')})"
        )


def log_plan_status(state):

    plans = state.get("plans", [])

    if not plans:
        return

    active_goal_id = state.get("active_goal_id")

    for p in plans:
        if p.get("goal_id") != active_goal_id:
            continue

        log(f"\n[PLAN] {p['plan_id']} status={p['status']}")

        for step in p.get("steps", []):
            log(
                f"  - {step['step_id']} | {step['status']} "
                f"(retry={step.get('retry_count', 0)})"
            )

        log("")