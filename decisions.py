from datetime import datetime
from logger import log
from goal import Goal


def is_quiet_hours():
    hour = datetime.now().hour
    return 0 <= hour < 6


def system_unhealthy(state):
    return any(
        key.startswith("disabled_") and value
        for key, value in state.items()
    )


def decide_intents(event, state, agent):
    """
    Convert an event into intents AND mission-bound goals.
    """

    intents = []
    goals = []

    if is_quiet_hours():
        log("[DECISION] Quiet hours active. Deferring non-critical actions.")
        return intents, goals

    if system_unhealthy(state):
        log("[DECISION] System unhealthy. Limiting actions.")
        return intents, goals

    if event["type"] == "file_changed":
        intent = {
            "type": "analyze_change",
            "file": event["file"]
        }
        intents.append(intent)

        goal = Goal(
            goal_id=f"goal_{event['file']}_{int(datetime.now().timestamp())}",
            type="analyze_change",
            description=f"Analyze changes in {event['file']}",
            status="pending",
            created_at=datetime.now().isoformat(),
            owner_agent_id=agent.agent_id,
            related_intent=intent
        )

        # 🔑 DAY 4: bind goal to mission
        goal.mission_id = "mission_codebase_health"

        goals.append(goal)

        log(f"[GOAL CREATED] {goal.description}")

    return intents, goals
