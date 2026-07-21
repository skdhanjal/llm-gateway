from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from gateway.token_math import count_tokens
from .providers import stream_openai
from .metrics import log_request
from .config import settings

app = FastAPI(title="llm-gateway", version="0.1.0")

class ChatRequest(BaseModel):
    prompt: str
    max_tokens: int = 512

@app.post("/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    est_token = count_tokens(req.prompt, settings.default_model)  # pre-flight estimate for metrics drift
    async def gen():
        stats = None
        async for delta, stats in stream_openai(req.prompt, req.max_tokens):
            yield delta
        if stats:
            log_request(stats, model=settings.default_model, est_input_tokens=est_token)   # fire-and-forget after stream closes
    return StreamingResponse(gen(), media_type="text/plain")