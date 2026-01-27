import time
from logger import log

def run_every(interval_seconds, task_function):
    """
    Runs a task function repeatedly every N seconds
    """
    log(f"Scheduler started. Interval: {interval_seconds} seconds")

    while True:
        task_function()
        time.sleep(interval_seconds)
