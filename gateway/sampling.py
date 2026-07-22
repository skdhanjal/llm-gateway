from .routes_cfg import Intent

# Capability map: which parameter regime each model family speaks.
# Extend on Day 8 (Groq gpt-oss, Gemini) and Day 12 (fallback chains).
PINNED_SAMPLING_PREFIXES = ("gpt-5", "o3", "o4")   # reasoning models: no temp/top_p

def params_for(model: str, intent: Intent) -> dict:
    """Translate route intent into the dials THIS model supports.
    Returns kwargs merged into the Responses API call."""
    if model.startswith(PINNED_SAMPLING_PREFIXES):
        # Sampling is pinned; reasoning effort is the dial.
        # Reasoning tokens bill as OUTPUT (Day 2) — effort is also a cost dial.
        effort = {
            Intent.DETERMINISTIC: "minimal",
            Intent.BALANCED:      "low",
            Intent.CREATIVE:      "medium",
        }[intent]
        return {"reasoning": {"effort": effort}}
    # Knob models (open-weight chat tiers): classic sampling applies.
    knobs = {
        Intent.DETERMINISTIC: {"temperature": 0.0},
        Intent.BALANCED:      {"temperature": 0.7, "top_p": 0.95},
        Intent.CREATIVE:      {"temperature": 1.2, "top_p": 0.9},
    }[intent]
    return knobs