import asyncio, json
from gateway.providers import stream_openai
from gateway.structured import structured_pipeline
from gateway.schemas import CompanyFacts

TASK = ("Extract company facts from this forum post:\n"
  "'ngl veridia systems (the agritech ppl from ludhiana?? ~214 staff i think, "
  "started back in 2019) just raised again lol'")

def is_valid(raw: str) -> bool:
    try:
        CompanyFacts.model_validate(json.loads(raw.strip().strip("`").removeprefix("json")))
        return True
    except Exception:
        return False

async def tier_prompted():
    """Tier 1: politeness."""
    out = []
    async for d, _ in stream_openai(
        TASK + "\nRespond ONLY with JSON: reasoning, name, sector, employees, founded_year.",
        max_output_tokens=300, reasoning={"effort": "minimal"}):
        out.append(d)
    return is_valid("".join(out))

async def tier_strict():
    """Tier 3: contract (pipeline reports its own status)."""
    r = await structured_pipeline(TASK, CompanyFacts)
    return r.status in ("ok", "repaired"), r.status

async def main():
    N = 25
    p = [await tier_prompted() for _ in range(N)]
    print(f"tier1 prompted   valid: {sum(p)}/{N}")
    s = [await tier_strict() for _ in range(N)]
    statuses = [x[1] for x in s]
    print(f"tier3 strict     valid: {sum(x[0] for x in s)}/{N}  "
          f"statuses: { {st: statuses.count(st) for st in set(statuses)} }")

asyncio.run(main())