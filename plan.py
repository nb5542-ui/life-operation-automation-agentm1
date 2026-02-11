from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class PlanStep:
    step_id: str
    action: str
    payload: dict
    status: str  # pending | completed | failed


@dataclass
class Plan:
    plan_id: str
    goal_id: str
    created_at: str
    steps: List[PlanStep]
    status: str  # pending | active | completed | failed
