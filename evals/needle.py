import asyncio, itertools, random
from gateway.providers import stream_openai
from gateway.token_math import get_encoding

NEEDLE = ("The access code for the Meridian archive vault is 7-4-9-2-6. ")
QUESTION = ("\n\nAnswer with the digits only: what is the access code "
            "for the Meridian archive vault?")
ANSWER = "7-4-9-2-6"
ANSWER_DIGITS = "74926"

FILLER = open("evals/filler.txt").read()

def build_haystack(total_tokens: int, depth_pct: int, model: str) -> str:
    enc = get_encoding(model)
    fill_ids = (enc.encode(FILLER) * 50)[:total_tokens] 
    cut = int(len(fill_ids) * depth_pct / 100)
    return enc.decode(fill_ids[:cut]) + NEEDLE + enc.decode(fill_ids[cut:])

async def trial(size: int, depth: int, model: str = "gpt-5-mini") -> bool:
    prompt = build_haystack(size, depth, model) + QUESTION
    out = []
    async for delta, _ in stream_openai(
        prompt, 
        max_output_tokens=40,
        temperature=0.0,
    ):
        out.append(delta)
    text = "".join(out)
    digits = "".join(ch for ch in text if ch.isdigit())
    return ANSWER in text or digits == ANSWER_DIGITS   # format-tolerant scoring

async def main():
    SIZES  = [2_0000, 30_000, 40_000]
    DEPTHS = [10, 50, 90]
    N = 1
    sem = asyncio.Semaphore(3)
    
    async def cell(size, depth):
        async with sem:
            hits = 0
            for _ in range(N):
                hits += await trial(size, depth)
            return size, depth, hits / N
        
    results = await asyncio.gather(*[cell(s, d) for s, d in itertools.product(SIZES, DEPTHS)])
    
    print(f"{'size':>8s} | " + " | ".join(f"depth {d:>3d}%" for d in DEPTHS))
    for s in SIZES:
        row = [r[2] for r in results if r[0] == s]
        # results arrive per (size,depth) in product order — index accordingly
        print(f"{s:8d} | " + " | ".join(f"{v:9.0%}" for v in row))

asyncio.run(main())