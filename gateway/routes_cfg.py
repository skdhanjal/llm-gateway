from enum import Enum
from pydantic import BaseModel

class Intent(str, Enum):
    """What the route NEEDS — the gateway maps intent to each model's dials."""
    DETERMINISTIC = "deterministic"   # extraction, classification, structured
    BALANCED      = "balanced"        # general Q&A, summarization
    CREATIVE      = "creative"        # ideation, writing

class RouteConfig(BaseModel):
    model: str
    intent: Intent
    max_output_tokens: int = 512

# The registry IS the policy. It lives in git; changing it is a deploy.
ROUTES: dict[str, RouteConfig] = {
    "chat":    RouteConfig(model="gpt-4o-mini", intent=Intent.BALANCED),
    "extract": RouteConfig(model="gpt-4o-mini", intent=Intent.DETERMINISTIC,
                           max_output_tokens=256),
    "ideate":  RouteConfig(model="gpt-4o-mini", intent=Intent.CREATIVE),
}