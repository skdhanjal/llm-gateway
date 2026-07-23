import time
from pydantic import BaseModel, ValidationError
from .providers import client          # the AsyncOpenAI instance from Day 1
from .config import settings
import json, pathlib

DLQ = pathlib.Path("dead_letter.jsonl")

class StructuredResult(BaseModel):
    data: dict | None
    status: str            # "ok" | "repaired" | "refused" | "dead_letter"
    attempts: int
    total_ms: float
    usage: dict

async def call_structured(task: str, schema_cls: type[BaseModel],
                          model: str | None = None) -> tuple:
    """One strict-mode call. Returns (parsed | None, refusal | None, usage)."""
    resp = await client.responses.parse(
        model=model or settings.default_model,
        input=task,
        text_format=schema_cls,           # SDK compiles Pydantic → strict json_schema
        reasoning={"effort": "minimal"},  # Day 3: extraction = cheap route
        store=False,
    )
    usage = {"input_tokens": resp.usage.input_tokens,
             "output_tokens": resp.usage.output_tokens}
    # Refusal path: strict mode's documented escape hatch — check before parsing.
    refusal = next((c.refusal for item in resp.output if item.type == "message"
                    for c in item.content if c.type == "refusal"), None)
    return resp.output_parsed, refusal, usage


async def structured_pipeline(task: str, schema_cls, model=None) -> StructuredResult:
    t0 = time.perf_counter()
    attempts, agg_usage = 0, {"input_tokens": 0, "output_tokens": 0}

    async def attempt(prompt: str):
        nonlocal attempts
        attempts += 1
        parsed, refusal, usage = await call_structured(prompt, schema_cls, model)
        for k in agg_usage: agg_usage[k] += usage[k]
        return parsed, refusal

    parsed, refusal = await attempt(task)
    if refusal:
        return StructuredResult(data=None, status="refused", attempts=attempts,
            total_ms=(time.perf_counter()-t0)*1000, usage=agg_usage)
    try:
        # output_parsed already ran schema validation; re-validating runs
        # OUR field_validators (semantics) — the part strict mode can't do.
        data = schema_cls.model_validate(parsed.model_dump())
        return StructuredResult(data=data.model_dump(), status="ok",
            attempts=attempts, total_ms=(time.perf_counter()-t0)*1000, usage=agg_usage)
    except ValidationError as e:
        # ONE repair: the actual error, verbatim, plus the offending output.
        repair_prompt = (
            f"{task}\n\nYour previous answer failed validation.\n"
            f"Previous answer: {json.dumps(parsed.model_dump())}\n"
            f"Validation errors: {e}\n"
            f"Produce a corrected answer.")
        parsed2, refusal2 = await attempt(repair_prompt)
        try:
            if refusal2: raise ValueError("refused on repair")
            data = schema_cls.model_validate(parsed2.model_dump())
            return StructuredResult(data=data.model_dump(), status="repaired",
                attempts=attempts, total_ms=(time.perf_counter()-t0)*1000, usage=agg_usage)
        except Exception as e2:
            DLQ.open("a").write(json.dumps({"task": task,
                "schema": schema_cls.__name__, "errors": str(e2),
                "raw": parsed2.model_dump() if parsed2 else None}) + "\n")
            return StructuredResult(data=None, status="dead_letter",
                attempts=attempts, total_ms=(time.perf_counter()-t0)*1000, usage=agg_usage)