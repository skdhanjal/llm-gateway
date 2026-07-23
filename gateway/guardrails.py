from dataclasses import dataclass

@dataclass
class ScreenResult:
    flagged: bool
    reason: str
    score: float

# Day 100–101 replaces the body with a real classifier (e.g. a small
# fine-tuned detector). The INTERFACE is what matters today — everything
# downstream calls screen_input() and never knows the implementation.
SUSPICIOUS = ["ignore the above", "ignore all previous", "system:",
              "disregard", "verbatim", "you are dan", "new directive"]

def screen_input(text: str, source: str = "user") -> ScreenResult:
    """source='untrusted' for retrieved/fetched content — Phase 2/3 will
    screen those far more strictly than user text."""
    low = text.lower()
    hits = [s for s in SUSPICIOUS if s in low]
    # heuristic only — will MISS encoded/hidden/reframed attacks (that's the point:
    # today you learn WHY naive screening is insufficient, from your own numbers)
    score = min(1.0, len(hits) * 0.4)
    return ScreenResult(flagged=score >= 0.4,
                        reason=f"matched: {hits}" if hits else "clean",
                        score=score)