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

## Day 2 — Tokenization, Cost Mechanics & Formats

### 1. Input Format Benchmark Results
| Format | Tokens | vs json_pretty | $/1M Requests |
| :--- | ---: | ---: | ---: |
| `json_pretty` | 2429 | 100.0% | $364 |
| `yaml` | 1880 | 77.4% | $282 |
| `json_min` | 1550 | 63.8% | $232 |
| `md_table` | 953 | 39.2% | $143 |
| `csv` | 805 | 33.1% | $121 |

### 2. Output-Side Experiment Results
* **`json_out` Average:** ~628 tokens | ~9,327 ms total latency across runs.
* **`csv_out` Average:** ~234 tokens | ~5,132 ms total latency across runs.
* **Impact:** Switching the requested output format from JSON to CSV reduced output token volume by ~62.7% and nearly halved total wall-clock latency (fewer decode passes).
* **Annualized Savings Calculation:** 
  * Token reduction per request: ~394 tokens saved.
  * At a volume of 50,000 requests/day and an illustrative output price tier of $5.00 / 1M output tokens:
  * $\text{394 tokens} \times \text{50,000 req/day} \times \text{365 days} = \text{7.19 billion tokens/year saved}$.
  * **Estimated Annual Saving:** $\approx \$35,950/\text{year}$ on output tokens alone.

### 3. Architectural Rationale & Notes
* **Drift as a First-Class Metric:** The gap between local `tiktoken` pre-flight counts and billed `input_tokens` is tracked as `count_drift_pct` to instantly expose chat scaffolding and template overhead.
* **Resilient Cost Attribution:** Unknown models fallback to `$0` cost attribution rather than throwing exceptions, ensuring observability failures never disrupt the serving path.
* **Format Accuracy Trade-off:** *(Accuracy TBD Day 32)* — While CSV and minified formats dramatically reduce token costs, lower token counts are a false economy if extraction accuracy or schema adherence degrades. Evaluation harness tests will validate task accuracy per format in Phase 2.
* **Multilingual Cost Multipliers:** Non-English scripts (e.g., Devanagari/Gurmukhi) carry higher token fertility (1.5–4x higher counts per unit of meaning). Products targeting Indic-language users must budget per-language cost multipliers and increased latency from day one.