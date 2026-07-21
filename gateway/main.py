from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .sampling import params_for
from .routes_cfg import ROUTES
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
    route: RouteConfig = ROUTES.get(req.route, {})
    
    if not route:
        raise ValueError(f"Unknown route: {req.route}")
    
    extra_params = params_for(route.model, route.intent) if route else {}
    
    async def gen():
        stats = None
        async for delta, stats in stream_openai(req.prompt, req.max_tokens, **extra_params):
            yield delta
        if stats:
            log_request(stats, model=settings.default_model, est_input_tokens=est_token)   # fire-and-forget after stream closes
    return StreamingResponse(gen(), media_type="text/plain")