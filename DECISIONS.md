# Day 1 — The Transformer Mental Model

## Benchmark Results

| Scenario | Input Tokens | TTFT p50 (ms) | TPS p50 |
| :--- | :--- | :--- | :--- |
| `short_in/short_out` | 12 | 822 | 84.7 |
| `short_in/long_out` | 17 | 814 | 73.1 |
| `long_in/short_out` | 1457 | 935 | 81.9 |
| `long_in/long_out` | 1462 | 973 | 85.4 |

## Observations

* **Prefill Overhead:** There is a clear correlation between input length and TTFT. The `long_in` scenarios averaged ~950ms TTFT, while `short_in` scenarios averaged ~818ms. This ~130ms difference captures the additional computation required to process the longer prompt (the prefill phase).
* **Decode Throughput Independence:** The TPS values remain relatively stable (ranging between 73 and 85) regardless of whether the input prompt was short (12 tokens) or long (1462 tokens). This validates the architecture: the decode loop (amber phase) is decoupled from the prefill phase (teal phase) in terms of performance throughput.
* **Stable Metrics:** Unlike the initial test run, these results show consistent performance, indicating that the system is properly "warmed up." The variance between runs is minimal, suggesting that the gateway and underlying provider infrastructure are currently handling these load levels efficiently without significant queueing noise.