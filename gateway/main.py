from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .sampling import params_for
from .routes_cfg import ROUTES
from gateway.context import BudgetExceeded, enforce_budget
from gateway.routes_cfg import RouteConfig
from .token_math import count_tokens
from .providers import stream_openai
from .metrics import log_request
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
                params=extra_params
            )
            
    return StreamingResponse(generate(), media_type="text/plain")