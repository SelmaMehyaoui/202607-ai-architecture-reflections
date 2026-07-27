# Language, Knowledge and Action
# _A short essay on AI architectures._

This essay explores a simple idea:

> As AI systems become increasingly capable, the most significant design decisions may progressively shift from model selection to architectural design.

Rather than viewing symbolic AI, machine learning, generative AI, MCP and skills as competing technologies, the essay proposes understanding them as complementary computational abstractions with distinct architectural responsibilities.

## Abstract

The recent evolution of Artificial Intelligence is often described through the rapid succession of increasingly capable foundation models. This essay argues that another transformation deserves equal attention: the emergence of architectures that deliberately distribute language processing, prediction, reasoning and action across specialized computational components. From this perspective, architectural quality depends not only on model capabilities, but also on how computational responsibilities are assigned, governed and orchestrated.

## Paper

📄 **Language, Knowledge and Action – Reflections on AI Architectures**

The pdf is available in the `paper/` directory.

## Acknowledgements

Many thanks to the colleagues and friends who kindly reviewed early drafts and provided thoughtful comments that helped improve the essay.

## Status

Version 1.0

The essay is intentionally presented as a reflection rather than a research paper. Comments, questions and counterpoints are warmly welcome. (Email: selma.mehyaoui@gmail.com)

## Experiments

The first empirical companion is
[`experiments/execution-boundaries`](experiments/execution-boundaries/README.md).
It compares a skill-invoked script, a local MCP server, and the same MCP tool
inside a narrowly mounted container. The experiment is neutral: its purpose is
to measure where code executes and which capabilities each configured runtime
actually has.

The second experiment,
[`experiments/model-tool-composition`](experiments/model-tool-composition/README.md),
tests how externalizing controlled knowledge and deterministic operations behind
the same MCP interface changes the model capability required for end-to-end
task success. It compares lightweight local and remote reference models under
direct-context and MCP-assisted conditions.

The third experiment,
[`experiments/complete-ai-system-config`](experiments/complete-ai-system-config/README.md),
uses Codex as the shared model and agent while comparing three complete
configurations: a Skill plus its declared script, a local MCP server, and a
narrowly mounted container MCP server. Fresh sessions, a frozen prompt,
explicit run records, and honest
handling of unavailable token telemetry make the comparison reproducible. A
separate API-driven harness is retained for later local and remote model runs.

The controlled deterministic task is an order-summary calculation. Each
configuration must read the same synthetic CSV, validate the required
`order_id`, `category`, `quantity`, and `unit_price` fields, calculate revenue
as `quantity × unit_price` for every row, and write the same JSON structure:
total order count and revenue, plus order count and revenue by category. For the
current fixture, the frozen expected result contains 8 orders and total revenue
of `411.49`.

An editable multi-page
[`Draw.io architecture diagram`](docs/ai-architecture-experiments.drawio)
summarizes the experiments, their execution paths, trust boundaries,
methodologies, and evidence flows.

## Roadmap

This repository is a work in progress. Planned extensions include:

- repeat the complete-system comparison to build a larger sample;
- test lightweight local and remote models with the same controlled tools;
- deploy the same MCP server to one European and one US Azure region;
- separate network, connection, server, tool, guardian, and end-to-end latency;
- compare cold connections with reused connections under the same protocol;
- extend the task set beyond the current deterministic order summary.

The regional Azure experiment will keep the MCP implementation, deployment
configuration, data, authentication, and resource limits as consistent as
possible. Results will describe the tested client, regions, and network
conditions rather than claim a universal Europe-versus-US performance ranking.

## Contributions

Reproductions, methodological reviews, counterexamples, additional task
fixtures, and carefully scoped experiment proposals are welcome. Please keep
observations separate from interpretations, preserve failed runs, document the
exact environment, and avoid committing credentials, private data, or personal
paths.
