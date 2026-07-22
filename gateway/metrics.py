import json
import time
import pathlib

from .token_math import estimate_cost_usd
from .providers import StreamStats

METRICS_FILE = pathlib.Path("metrics.jsonl")

def log_request(
        stats: StreamStats, 
        route: str = "chat", 
        model: str = "gpt-5-mini", 
        est_input_tokens: int = 0, 
        **extra_params
    ):
    drift_pct = 0.0

    if est_input_tokens and stats.input_tokens:
        drift_pct = (stats.input_tokens - est_input_tokens) / stats.input_tokens * 100

    record = {
        "ts": time.time(),
        "route": route,
        "model": model,
        "input_tokens": stats.input_tokens,
        "output_tokens": stats.output_tokens,
        "est_input_tokens": est_input_tokens,     # our tiktoken pre-flight
        "count_drift_pct": round(drift_pct, 1),
        "cost_usd": round(estimate_cost_usd(stats.input_tokens, stats.output_tokens, model), 6),
        "ttft_ms": round(stats.ttft_ms, 1),
        "decode_tps": round(stats.decode_tps, 1),
        "total_ms": round((stats.t_end - stats.t_start) * 1000, 1),
    }
    
    record.update(extra_params)
    
    with METRICS_FILE.open("a") as f:
        f.write(json.dumps(record) + "\n")
