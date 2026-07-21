import asyncio, statistics
from unittest import result

from gateway.metrics import log_request
from gateway.providers import stream_openai
from gateway.token_math import count_tokens
from gateway.config import settings

SHORT_Q = "Name three consensus algorithms."
LONG_Q  = "Here is a design doc: " + ("Our service handles user auth via "
          "token exchange with refresh rotation. " * 120) + "Name three risks."

GRID = [  # (label, prompt, max_tokens) — 5 runs each = 20 requests
    ("short_in/short_out", SHORT_Q, 60),
    ("short_in/long_out",  SHORT_Q + " Explain each in depth.", 600),
    ("long_in/short_out",  LONG_Q, 60),
    ("long_in/long_out",   LONG_Q + " Explain each in depth.", 600),
]

async def run_one(prompt, max_tokens):
    est_token = count_tokens(prompt, settings.default_model)  # pre-flight estimate for metrics drift
    stats = None
    async for _, stats in stream_openai(prompt, max_tokens, model=settings.default_model):
        pass
    if stats:
        log_request(stats, route="bench", est_input_tokens=est_token, model=settings.default_model)
        
    return stats

async def warm_up():
    print("Warming up connection...")
    await run_one("Hello", 16) # Smallest possible request

async def main():
    # await warm_up()
    
    for label, prompt, mt in GRID:
        results = [await run_one(prompt, mt) for _ in range(1)]
        ttfts = [r.ttft_ms for r in results]
        tpss  = [r.decode_tps for r in results]
        print(f"{label:22s}  in={results[0].input_tokens:5d} tok   "
              f"TTFT p50={statistics.median(ttfts):7.0f}ms   "
              f"TPS p50={statistics.median(tpss):5.1f}")

asyncio.run(main())