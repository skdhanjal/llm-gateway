from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .providers import stream_openai
from .metrics import log_request

app = FastAPI(title="llm-gateway", version="0.1.0")

class ChatRequest(BaseModel):
    prompt: str
    max_tokens: int = 512

@app.post("/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    async def gen():
        stats = None
        async for delta, stats in stream_openai(req.prompt, req.max_tokens):
            yield delta
        if stats:
            log_request(stats)   # fire-and-forget after stream closes
    return StreamingResponse(gen(), media_type="text/plain")