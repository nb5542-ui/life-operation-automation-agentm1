from datetime import datetime
from logger import log


def is_quiet_hours():
    """
    Define quiet hours where non-critical work should be avoided.
    Example: 12 AM – 6 AM
    """
    hour = datetime.now().hour
    return hour >= 0 and hour < 6


def system_unhealthy(state):
    """
    System is unhealthy if any task is disabled.
    """
    return any(
        key.startswith("disabled_") and value
        for key, value in state.items()
    )


def decide_intents(event, state):
    """
    Convert an event into intents using context + state.
    """
    intents = []

    # -------- CONTEXT CHECKS --------
    if is_quiet_hours():
        log("[DECISION] Quiet hours active. Deferring non-critical actions.")
        return intents

    if system_unhealthy(state):
        log("[DECISION] System unhealthy. Limiting actions.")
        return intents

    # -------- EVENT-BASED DECISIONS --------
    if event["type"] == "file_changed":
        intents.append({
    "action": "analyze_file",
    "payload": {
        "file": event["file"]
    }
})


    return intents
