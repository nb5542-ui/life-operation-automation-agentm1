from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class Mission:
    mission_id: str
    name: str
    description: str
    active: bool
    created_at: str
    owned_by_agent_id: str
    goal_ids: List[str]
