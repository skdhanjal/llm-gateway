# llm-gateway
A foundational LLM gateway designed for observability and performance benchmarking. This service provides a standardized interface for LLM inference, ensuring that every request is instrumented to capture the metrics that matter most to production systems.

Core Features
Streaming Support: Full support for real-time token streaming, enabling responsive UI/UX for generative applications.

Deep Observability: Captures critical performance telemetry including Time To First Token (TTFT) and Tokens Per Second (TPS) for every request.

Structured Logging: Automatically logs performance data to metrics.jsonl for offline analysis, cost modeling, and SLO tracking.

Provider-Agnostic: Designed with an abstraction layer to support multiple LLM providers behind a unified API contract.

Benchmarking Suite: Includes automated scripts for testing and visualizing latency behaviors under different input/output loads.

Architecture
This gateway serves as the primary routing and instrumentation layer, decoupling your application logic from underlying model providers while maintaining strict, high-fidelity monitoring.
