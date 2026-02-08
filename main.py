from logger import log
from config import AGENT_NAME
from scheduler import run_every
from tasks import run_all_tasks
from agent import Agent
from mission import Mission


# =========================
# SYSTEM AGENT
# =========================
SYSTEM_AGENT = Agent(
    agent_id="system",
    role="core_automation",
    authority_level="full",
    allowed_action_categories=["*"],
    bound_policies=["default"],
    status="active",
)


# =========================
# SYSTEM MISSIONS (STATIC)
# =========================
SYSTEM_MISSIONS = [
    Mission(
        mission_id="mission_codebase_health",
        name="Codebase Health",
        description="Maintain codebase stability and quality",
        active=True,
        created_at="2026-02-01T00:00:00",
        owned_by_agent_id=SYSTEM_AGENT.agent_id,
        goal_ids=[]
    )
]


def start_agent():
    log(f"{AGENT_NAME} started")
    run_every(5, lambda: run_all_tasks(SYSTEM_AGENT, SYSTEM_MISSIONS))


if __name__ == "__main__":
    start_agent()
