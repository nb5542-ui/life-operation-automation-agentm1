from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Goal:
    goal_id: str
    type: str
    description: str
    status: str                 # pending | active | completed | failed
    created_at: str
    owner_agent_id: str         # NEW
    related_intent: Optional[dict] = None
    updated_at: Optional[str] = None
