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

An editable two-page
[`Draw.io architecture diagram`](docs/execution-boundaries-architecture.drawio)
summarizes the execution paths, trust boundaries, benchmark methodology, and
evidence flow.
