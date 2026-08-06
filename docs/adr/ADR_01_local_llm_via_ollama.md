# ADR-0001: Local LLM (Ollama) over a cloud API

## Status
Accepted

## Context
The system needs an LLM for two jobs: routing/intent evaluation in the agent loop, and generating final answers. Cloud APIs like OpenAI are the default choice in most RAG tutorials, but this project is built without a budget — every embedding call and every chat completion through a paid API has a real per-token cost, and a support system fielding many test queries during development would run that cost up quickly with no revenue behind it.

## Decision
Run the LLM locally via [Ollama](https://ollama.com), using `llama3.1:8b` (or a comparable open model) as the default backend, accessed through `langchain-ollama`. The LLM is accessed through an `LLMProvider` abstraction rather than calling `langchain-ollama` directly from application code, so a cloud provider can be swapped in later via configuration without touching the agent logic.

## Alternatives considered
- **OpenAI API (`langchain-openai`)** — best-in-class tool-calling reliability and response quality, but direct, unavoidable per-call cost. Kept as a documented, swappable option via the provider abstraction rather than ruled out entirely.
- **Local inference via raw `llama.cpp`** — more control, no Ollama daemon dependency, but significantly more setup and maintenance overhead (model conversion, manual serving) for no functional benefit at this project's scale. Ollama wraps this cleanly.

## Consequences
- Zero ongoing inference cost during development.
- Tool-calling accuracy is measurably weaker with local 8B-class models than with GPT-4-class models — this is a known, documented limitation, not a hidden gap. Worth running a deliberate side-by-side comparison (swap the provider to OpenAI for one evaluation run) later to quantify the difference; that comparison is itself a strong eval artifact.
- Requires Ollama running locally as a prerequisite for anyone cloning the repo to run the project end-to-end — documented in setup instructions.
- The `LLMProvider` abstraction is extra code that a single-provider project wouldn't need, but it's what makes "local-first for cost, cloud-ready via config" a real, testable claim rather than just a README statement.