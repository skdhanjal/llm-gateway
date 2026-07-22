from enum import Enum
from pydantic import BaseModel

class Intent(str, Enum):
    """What the route NEEDS — the gateway maps intent to each model's dials."""
    DETERMINISTIC = "deterministic"   # extraction, classification, structured
    BALANCED      = "balanced"        # general Q&A, summarization
    CREATIVE      = "creative"        # ideation, writing
    
class Truncation(str, Enum):
    TAIL_DROP   = "tail_drop"     # keep beginning — document framing
    HEAD_DROP   = "head_drop"     # keep end — logs, transcripts
    MIDDLE_DROP = "middle_drop"   # keep both ends — exploits the U-curve
    REJECT      = "reject"        # 413 back to caller — when silent loss is unacceptable    

class RouteConfig(BaseModel):
    model: str
    intent: Intent
    max_output_tokens: int = 512
    input_budget: int = 5_000            # tokens, enforced pre-dispatch
    truncation: Truncation = Truncation.REJECT   # explicit per route, no silent default


ROUTES: dict[str, RouteConfig] = {
    "chat":    RouteConfig(model="gpt-4o-mini", intent=Intent.BALANCED),
    "extract": RouteConfig(model="gpt-4o-mini", intent=Intent.DETERMINISTIC,
                           max_output_tokens=256),
    "ideate":  RouteConfig(model="gpt-4o-mini", intent=Intent.CREATIVE),
}