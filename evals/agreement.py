import asyncio, json, collections
from gateway.providers import stream_openai

async def run_once(prompt: str, **params) -> str:
    chunks = []
    async for delta, _ in stream_openai(prompt, max_output_tokens=300, **params):
        chunks.append(delta)
    return "".join(chunks)

def normalize(raw: str) -> str:
    """Collapse formatting noise so we compare MEANING, not whitespace.
    For JSON tasks: parse and re-dump canonically; else strip/casefold."""
    try:
        return json.dumps(json.loads(raw.strip().strip("`")), sort_keys=True)
    except Exception:
        return " ".join(raw.lower().split())

async def agreement(prompt: str, n: int = 25, concurrency: int = 5, **params):
    sem = asyncio.Semaphore(concurrency)          # be polite to rate limits
    
    async def guarded():
        async with sem:
            return normalize(await run_once(prompt, **params))
        
    outputs = await asyncio.gather(*[guarded() for _ in range(n)])
    tally = collections.Counter(outputs)
    majority, m_count = tally.most_common(1)[0]
    
    return {
        "n": n,
        "distinct_outputs": len(tally),
        "agreement_rate": m_count / n,        # the number that matters
        "majority_preview": majority[:120],
    }

PROMPT = ("Extract as JSON with keys name, sector, employees: "
          "'Veridia Systems, a Ludhiana-based agritech firm, employs 214 people.'")

async def main():
    for label, params in {
        "effort_minimal": {"reasoning": {"effort": "minimal"}},
        "effort_medium":  {"reasoning": {"effort": "medium"}},
    }.items():
        r = await agreement(PROMPT, **params)
        print(label, json.dumps(r, indent=2))

if __name__ == "__main__":
    asyncio.run(main())