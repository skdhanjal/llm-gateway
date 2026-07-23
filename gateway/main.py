from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from gateway.guardrails import screen_input
from gateway.schemas import SCHEMA_REGISTRY
from gateway.structured import structured_pipeline

from .sampling import params_for
from .routes_cfg import ROUTES
from gateway.context import BudgetExceeded, enforce_budget
from gateway.routes_cfg import RouteConfig
from .token_math import count_tokens
from .providers import stream_openai
from .metrics import log_request, log_structured
from .config import settings

app = FastAPI(title="llm-gateway", version="0.1.0")

class ChatRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    route: str = "chat"

@app.post("/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    est_token = count_tokens(req.prompt, settings.default_model)  # pre-flight estimate for metrics drift
    
    route_cfg = ROUTES.get(req.route, ROUTES["chat"])
    
    if not route_cfg:
        raise ValueError(f"Unknown route: {req.route}")
    
    try:
        prompt, tokens_dropped = enforce_budget(
            req.prompt, 
            route_cfg.input_budget, 
            route_cfg.truncation, 
            route_cfg.model
        )
    except BudgetExceeded  as e:
        raise HTTPException(
            status_code=413,
            detail={
                "error": "input_budget_exceeded",
                "tokens_have": e.have,
                "tokens_budget": e.budget,
                "hint": "Retrieve instead of stuffing, or split the request.",
            },
        )
    
    extra_params = params_for(route_cfg.model, route_cfg.intent) if route_cfg else {}
    
    verdict = screen_input(req.prompt, source="user")
    
    async def generate():
        stats = None
        async for delta, stats in stream_openai(
            prompt, 
            req.max_tokens, 
            **extra_params
        ):
            yield delta
        if stats:
            log_request(
                stats, 
                route=req.route,
                model=settings.default_model,
                est_input_tokens=est_token,
                tokens_dropped=tokens_dropped,
                truncation=route_cfg.truncation.value if tokens_dropped else None,
                params=extra_params,
                screen_flagged=verdict.flagged,
                screen_source="user"
            )
            
    return StreamingResponse(generate(), media_type="text/plain")

class StructuredRequest(BaseModel):
    task: str
    schema: str                  # registry key, e.g. "company_facts"

@app.post("/v1/structured")
async def structured_endpoint(req: StructuredRequest):
    schema_cls = SCHEMA_REGISTRY.get(req.schema)
    if schema_cls is None:
        raise HTTPException(404, f"unknown schema: {req.schema}")

    # non-streaming by design (Sec 2.1) -- await the whole pipeline, then respond
    result = await structured_pipeline(req.task, schema_cls)

    log_structured(
        route="structured", 
        model=settings.default_model, 
        schema=req.schema,
        status=result.status, 
        attempts=result.attempts,
        total_ms=result.total_ms, 
        usage=result.usage
    )
    
    if result.status == "dead_letter":
        # Sec 2.2's alert -- a real pager rule from Phase 5 onward
        print(f"[ALERT] DLQ write -- schema={req.schema} task={req.task[:80]!r}")

    if result.status in ("refused", "dead_letter"):
        # surface failure explicitly -- a 200 with data=None invites callers to skip the check
        raise HTTPException(422, {"status": result.status, "attempts": result.attempts})
    return result