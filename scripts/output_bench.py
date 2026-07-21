import asyncio
from gateway.providers import stream_openai

DATA_TASK = ("List 15 fictional products for an electronics store with "
             "fields: sku, name, price_inr, stock. ")

VARIENTS = {
    "json_out": DATA_TASK + "Respond as a pretty-printed JSON array only.",
    "csv_out": DATA_TASK + "Respond as CSV with a header row only.",
}

async def main():
    for name, prompt in VARIENTS.items():
        for run in range(3):
            stats = None
            async for _, stats in stream_openai(prompt, max_output_tokens=1500):
                pass
            
            print(f"{name}  run{run+1}  out_tokens={stats.output_tokens:5d}  "
                  f"total_ms={(stats.t_end-stats.t_start)*1000:7.0f}")

asyncio.run(main())