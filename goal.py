from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Goal:
    goal_id: str
    type: str                 # e.g. "analyze_change"
    description: str
    status: str               # pending | active | completed | failed
    created_at: str
    related_intent: Optional[dict] = None
