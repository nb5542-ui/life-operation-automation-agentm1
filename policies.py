from datetime import datetime
from logger import log

# ---------- GLOBAL POLICY RULES ----------

def is_quiet_hours():
    hour = datetime.now().hour
    return hour >= 0 and hour < 6


def system_unhealthy(state):
    return any(
        key.startswith("disabled_") and value
        for key, value in state.items()
    )


def policy_allows_intent(intent, state):
    """
    Returns True if intent is allowed, False otherwise.
    Policy decisions are FINAL.
    """

    # 1) Never act during global pause
    if state.get("global_pause"):
        log("[POLICY] Global pause active. Intent denied.")
        return False

    # 2) No heavy actions during quiet hours
    if is_quiet_hours():
        log("[POLICY] Quiet hours. Intent denied.")
        return False

    # 3) System health gate
    if system_unhealthy(state):
        log("[POLICY] System unhealthy. Intent denied.")
        return False

    # 4) Explicit allow-list (important)
    allowed_intents = {
        "analyze_file_change",
    }

    if intent["actions"] not in allowed_intents:
        log(f"[POLICY] Intent '{intent['actions']}' not allowed.")
        return False

    return True
def policy_allows_override(state):
    """
    Human override must be explicit and temporary.
    """
    return state.get("allow_override", False)

