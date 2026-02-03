from logger import log

# ======================================================
# ACTION EXECUTORS
# ======================================================

def analyze_file_action(payload, state):
    file = payload.get("file")
    log(f"[ACTION] Analyzing file: {file}")


# ======================================================
# ACTION REGISTRY
# ======================================================

ACTION_REGISTRY = {
    "analyze_file": analyze_file_action
}
