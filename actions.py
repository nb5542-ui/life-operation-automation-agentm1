from logger import log

# ======================================================
# ACTION EXECUTORS
# ======================================================

def analyze_file_action(payload, state):
    file = payload.get("file")
    log(f"[ACTION] Analyzing file: {file}")

def log_result(payload, state):
    message = payload.get("message")
    log(f"[ACTION] {message}")


# ======================================================
# ACTION REGISTRY
# ======================================================

ACTION_REGISTRY = {
    "analyze_file": analyze_file_action,
    "log_result": log_result,
}
