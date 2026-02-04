from logger import log
from config import AGENT_NAME
from scheduler import run_every
from tasks import run_all_tasks
from agent import Agent


# =========================
# DEFAULT SYSTEM AGENT
# =========================
SYSTEM_AGENT = Agent(
    agent_id="system",
    role="core_automation",
    authority_level="full",
    allowed_action_categories=["*"],
    bound_policies=["default"],
    status="active",
)


def start_agent():
    log(f"{AGENT_NAME} started")
    run_every(5, lambda: run_all_tasks(SYSTEM_AGENT))


if __name__ == "__main__":
    start_agent()
