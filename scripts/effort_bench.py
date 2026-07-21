import asyncio
from gateway.providers import stream_openai

PROMPT = ("Extract as JSON with keys name, sector, employees: "
          "'Veridia Systems, a Ludhiana-based agritech firm, employs 214 people.'")

async def main():
    for effort in ("minimal", "low", "medium"):
        for _ in range(3):
            stats = None
            async for _, stats in stream_openai(
                PROMPT, max_output_tokens=400,
                reasoning={"effort": effort},
            ):
                pass
            print(f"{effort:8s} out_tokens={stats.output_tokens:4d} "
                  f"ttft_ms={stats.ttft_ms:6.0f} "
                  f"total_ms={(stats.t_end-stats.t_start)*1000:6.0f}")

asyncio.run(main())