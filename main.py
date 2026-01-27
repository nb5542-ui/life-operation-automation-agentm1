from logger import log
from config import AGENT_NAME
from scheduler import run_every
from tasks import run_all_tasks

def start_agent():
    log(f"{AGENT_NAME} started")
    run_every(5, run_all_tasks)

if __name__ == "__main__":
    start_agent()

