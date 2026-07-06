from dataclasses import dataclass, field
from typing import Callable, Any

@dataclass
class AgentConfig:
    name: str
    purpose: str
    instruction: str
    tools: list[Callable | str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
