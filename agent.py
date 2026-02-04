from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Agent:
    agent_id: str
    role: str
    authority_level: str   # read_only | limited | full
    allowed_action_categories: List[str]
    bound_policies: List[str]
    status: str            # active | paused | restricted
