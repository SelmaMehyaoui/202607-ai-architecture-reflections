# Complete AI system configuration experiment

This experiment measures the complete path from a user request, through a
Codex agent's action selection, to deterministic execution and the final
answer.

## Primary research question

> When the same Codex model performs the same task, how do a Skill-guided
> execution path and an MCP execution path differ in correctness, action
> reliability, observable latency, and observable context cost?

Codex is the model and agent under test. It is not a wrapper around a local or
remote model endpoint for the primary experiment.

```text
Fresh Codex session A
  -> controlled task prompt
  -> execution-boundaries/skill/SKILL.md
  -> real Python subprocess
  -> final answer

Fresh Codex session B
  -> same controlled task prompt
  -> registered summarize_orders MCP tool
  -> real local MCP server
  -> final answer
```

The two sessions must use the same Codex surface, model, reasoning setting,
repository revision, permissions, and input fixture. Separate fresh sessions
prevent the first condition's tool result or instructions from leaking into
the second.

## What is controlled

- The exact task prompt is stored in [`prompts/task.md`](prompts/task.md).
- Both paths call the same deterministic summarization implementation.
- Both receive the same explicit input and disposable output paths.
- The expected result is fixed before the run.
- Neither condition may fall back to the other condition's interface.
- Condition order alternates across paired repetitions.
- Every run records its environment and any protocol deviation.

The Skill path uses the existing
[`skill/SKILL.md`](../execution-boundaries/skill/SKILL.md) and its declared
script. The MCP path uses the existing local `summarize_orders` MCP server.
The agent must not calculate the CSV directly in either condition.

## Reproducible Codex protocol

Follow [`codex-protocol.md`](codex-protocol.md). It defines session isolation,
the exact operator prompt, availability checks, timing boundaries, preserved
evidence, the run-record schema, and failure rules.

Copy [`templates/codex-run.json`](templates/codex-run.json) once per session and
complete only fields that are observable. Do not estimate missing measurements.

## Measurements

The primary Codex experiment records:

- task success and final-answer correctness;
- action selected and tool-call arguments;
- real tool execution and output;
- elapsed wall time when measured externally;
- number of model turns and action calls;
- permission prompts, failures, and protocol deviations;
- Codex model, surface, reasoning setting, and application version;
- token usage only when the Codex surface exposes a reliable value for that
  isolated run.

This repository cannot infer exact model-token consumption from MCP messages,
terminal output, elapsed time, or text length. If Codex does not expose
per-session token usage, the field must be `null` with
`token_measurement_source` set to `"unavailable"`.

## Optional API-driven extension

[`run_benchmark.py`](run_benchmark.py) is a separate automation extension for
an OpenAI-compatible model endpoint. It is useful later for Colima-hosted and
remote models, but its results must not be mixed with the primary Codex study.
That harness compares:

```text
same API model -> Skill text + narrow runner function
same API model -> MCP schema + local MCP server
```

For example, after independently starting a compatible local model:

```sh
.venv/bin/python experiments/complete-ai-system-config/run_benchmark.py \
  --model <exact-model-id> \
  --runs 10
```

The API extension records provider-reported prompt, completion, and total
tokens. Missing usage remains missing. It also records inference time, tool
time, end-to-end time, request and response bytes, tool-call validity, and raw
traces.

## Results

Codex run records and reviewed API outputs belong under `results/`. Generated
files remain ignored until they have been inspected for local paths, prompts,
model output, and other information that should not be published.

## Interpretation boundary

This experiment compares complete, explicitly recorded configurations. It
cannot establish that MCP, Skills, Codex, or any model is universally faster.
A result may reflect the chosen model, reasoning setting, session context,
Codex version, permissions, process lifecycle, tool description, or task.
