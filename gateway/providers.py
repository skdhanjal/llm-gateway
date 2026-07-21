import time
from dataclasses import dataclass
from typing import AsyncIterator
from pydantic import BaseModel
from .config import settings
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.openai_api_key)

@dataclass
class StreamStats():
    t_start: float = 0.0
    t_first_token: float = 0.0
    t_end: float = 0.0

    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def ttft_ms(self) -> float:
        return (self.t_first_token - self.t_start) * 1000

    @property
    def decode_tps(self) -> float:
        """
        Calculate the decoding tokens per second.
        """
        decode_s = self.t_end - self.t_first_token
        if decode_s > 0:
            return self.output_tokens / decode_s
        return 0


async def stream_openai(prompt: str, max_output_tokens: int = 512, model: str | None = None, **extra) -> AsyncIterator[tuple[str, StreamStats]]:
    """
    Stream responses from OpenAI's API.
    Yields tuples of (response_text, StreamStats).
    """

    stats = StreamStats(t_start=time.perf_counter())

    stream = await client.responses.create(
        model=model or settings.default_model,
        input=prompt,
        max_output_tokens=max_output_tokens,
        stream=True,
        store=False,
        **extra
    )

    async for event in stream:
        if event.type == "response.output_text.delta":
            if stats.t_first_token == 0.0:
                stats.t_first_token = time.perf_counter()
                # print(f"First token received after {stats.ttft_ms:.0f}ms")
            # print(f"Stream delta: {event.delta}")    
            yield event.delta, stats

        elif event.type == "response.completed":
            stats.t_end = time.perf_counter()
            usage = event.response.usage
            stats.input_tokens = usage.input_tokens
            stats.output_tokens = usage.output_tokens
            # print(f"Stream completed: input_tokens={stats.input_tokens}, output_tokens={stats.output_tokens}")
            # yield "", stats  # final yield to indicate completion

        elif event.type == "response.incomplete":
            stats.t_end = time.perf_counter()
            # Capture usage even if incomplete, as it's still billable
            usage = event.response.usage
            stats.input_tokens = usage.input_tokens
            stats.output_tokens = usage.output_tokens
            # print(f"Warning: Request finished incomplete (likely hit max_tokens limit)")    
            
        elif event.type == "error":
            raise RuntimeError(f"stream error: {event}")
