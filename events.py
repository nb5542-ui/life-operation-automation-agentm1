import os
from logger import log

WATCH_FILE = "event_trigger.txt"

def detect_file_event(state):
    """
    Detects changes in a watched file and records an event.
    """
    if not os.path.exists(WATCH_FILE):
        return

    last_mtime = state.get("watch_file_mtime")
    current_mtime = os.path.getmtime(WATCH_FILE)

    if last_mtime is None:
        state["watch_file_mtime"] = current_mtime
        return

    if current_mtime != last_mtime:
        log("[EVENT] File change detected")
        state["watch_file_mtime"] = current_mtime
        enqueue_event(state, {
            "type": "file_changed",
            "file": WATCH_FILE
        })

def enqueue_event(state, event):
    """
    Adds an event to the queue with deduplication and priority handling.
    """
    queue = state.get("event_queue", [])

    # Deduplicate: skip if same type already queued
    for existing in queue:
        if existing["type"] == event["type"]:
            return

    # Default priority (lower = higher priority)
    event.setdefault("priority", 10)

    queue.append(event)

    # Sort queue by priority
    queue.sort(key=lambda e: e["priority"])

    state["event_queue"] = queue
