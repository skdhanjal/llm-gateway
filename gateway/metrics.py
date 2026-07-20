import json, time, pathlib
from .providers import StreamStats

METRICS_FILE = pathlib.Path("metrics.jsonl")

def log_request(stats: StreamStats, route: str = "chat", model: str = "default"):
    record = {
        "ts": time.time(),
        "route": route,
        "model": model,
        "input_tokens": stats.input_tokens,
        "output_tokens": stats.output_tokens,
        "ttft_ms": round(stats.ttft_ms, 1),
        "decode_tps": round(stats.decode_tps, 1),
        "total_ms": round((stats.t_end - stats.t_start) * 1000, 1),
    }
    with METRICS_FILE.open("a") as f:
        f.write(json.dumps(record) + "\n")