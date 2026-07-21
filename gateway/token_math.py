import tiktoken
from functools import lru_cache
from .config import MODEL_PRICES

@lru_cache(maxsize=8)
def get_encoding(model: str):
    """Resolve the right encoding for a model; fall back to o200k_base
    for model names newer than the installed tiktoken release."""
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("o200k_base")

def count_tokens(text: str, model: str = "gpt-5-mini") -> int:
    """ESTIMATE of content tokens. Excludes chat scaffolding, tool
    schemas, and reasoning tokens — the billed number will be higher.
    Use for pre-flight budgeting; reconcile against API usage."""
    return len(get_encoding(model).encode(text))

def estimate_cost_usd(in_tok: int, out_tok: int, model: str) -> float:
    p = MODEL_PRICES.get(model)
    if not p:
        return 0.0   # unknown model → visible as $0 rows in the dashboard, not a crash
    return (in_tok * p["input"] + out_tok * p["output"]) / 1_000_000