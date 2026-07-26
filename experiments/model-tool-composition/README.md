# Model–tool composition experiment

This experiment studies whether externalizing bounded domain knowledge and
deterministic operations behind a typed MCP interface changes how much model
capability is required for successful task completion.

It does **not** attempt to show that lightweight models are generally equivalent
to frontier models. It tests a narrower architectural proposition:

> For bounded tasks, a model may operate primarily as a language-to-capability
> translation layer when retrieval and calculation are assigned to specialized
> components.

## Research questions

Primary:

> Can a lightweight local model achieve non-inferior end-to-end task success
> relative to a remote reference model when both use the same MCP tools?

Secondary:

> As linguistic ambiguity, tool composition, and error recovery increase, where
> does any performance gap reappear?

## Experimental matrix

| Model class | Direct-context condition | MCP-assisted condition |
|---|---|---|
| Lightweight local model | Receives the controlled domain context | Uses the domain MCP server |
| Remote reference model | Receives the same controlled context | Uses the same MCP server |

The direct-context baseline is essential. In both conditions the system can
access the same experiment-specific facts; only the allocation of retrieval and
calculation differs.

## Controlled domain

The synthetic commerce domain contains:

- deterministic order records;
- fictional return policies;
- deliberately invented facts that should not be known from model pretraining;
- tools for filtered revenue summaries and policy retrieval.

The task suite progresses from explicit one-tool requests through paraphrase,
parameter extraction, multi-tool composition, ambiguity handling, structured
error recovery, and correct tool abstention.

## Structure

```text
model-tool-composition/
├── README.md
├── methodology.md
├── common/
│   ├── domain.py
│   ├── direct-context.md
│   └── input/
│       ├── orders.csv
│       └── policies.json
├── mcp/
│   └── domain_server.py
├── tasks/
│   └── tasks.jsonl
├── evaluation/
│   ├── evaluate.py
│   └── response-schema.json
├── results/
│   └── README.md
└── tests/
    └── test_domain.py
```

## Current milestone

The controlled domain, MCP server, task manifest, response-record schema, and
descriptive evaluator are implemented. Model adapters are intentionally not yet
selected. Before collecting results, record:

- exact local model, checksum, quantization, prompt template, context length,
  sampling settings, runner version, and Colima resources;
- exact remote model snapshot where available, request date, prompt template,
  sampling settings, token usage, and cost;
- a pre-registered non-inferiority margin and grading procedure.

Colima 0.10.3 supports Docker Model Runner and Ramalama. GPU access requires a
`krunkit` VM profile. The container runtime is an implementation convenience,
not part of the scientific claim.

## Validation

From the repository root:

```sh
.venv_aiarch/bin/python -m pytest \
  experiments/model-tool-composition/tests
.venv_aiarch/bin/python \
  experiments/model-tool-composition/evaluation/evaluate.py \
  path/to/reviewed-responses.jsonl
```

No API credentials, model weights, or generated results belong in the
repository.
