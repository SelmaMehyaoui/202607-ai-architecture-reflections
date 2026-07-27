# Codex-operated protocol

This protocol makes Codex the model and agent under test.

## 1. Freeze the configuration

Before the first pair, record:

- repository commit;
- Codex surface, such as app, IDE extension, or CLI;
- Codex application or CLI version;
- exact displayed model and reasoning setting;
- permission or approval mode;
- operating system and architecture;
- Python and `mcp` package versions.

Do not switch surface, model, reasoning, or permissions within a comparison.

## 2. Verify the deterministic baseline

Run the existing execution-boundaries tests before collecting model-mediated
results:

```sh
.venv/bin/pytest -q
```

Both conditions must resolve to:

```json
{
  "total_orders": 8,
  "total_revenue": "411.49"
}
```

## 3. Prepare the interfaces

For the Skill condition, make
`experiments/execution-boundaries/skill/SKILL.md` available to Codex and
explicitly invoke that Skill in the controlled prompt. Codex must follow its
declared script path and must not use the MCP server.

For the MCP condition, register
`experiments/execution-boundaries/mcp-local/server.py` as a stdio MCP server in
the Codex environment. Start a fresh Codex session after configuration and
verify that it exposes exactly one relevant tool named `summarize_orders`.
Codex must use that MCP tool and must not run the Skill script through the
terminal.

Record the actual Skill discovery method and MCP configuration in each run
record. Codex configuration interfaces can change, so the record, rather than
an assumed global setup command, is authoritative.

## 4. Create a pair

Use two fresh sessions. Session A receives one condition and Session B receives
the other. Alternate order:

```text
even pair: Skill, then MCP
odd pair:  MCP, then Skill
```

Do not discuss the other condition in the session. Do not reuse a thread,
continue from a summary, or preload a previous result.

## 5. Submit the controlled prompt

Replace only the three bracketed values in
[`prompts/task.md`](prompts/task.md):

- `[CONDITION]` with `Skill` or `MCP`;
- `[INPUT_PATH]` with the absolute controlled CSV path;
- `[OUTPUT_PATH]` with a new disposable absolute JSON path.

Submit the complete prompt as one message. Do not add hints after submission.
If Codex asks a blocking question, record the run as unsuccessful. A clarified
attempt is a new run.

## 6. Measure and preserve evidence

If measuring wall time, start immediately before submitting the message and
stop when Codex's final answer is visible.

Preserve:

- the submitted prompt;
- the assistant transcript;
- tool or command calls and arguments;
- permission prompts;
- output JSON and its SHA-256 digest;
- final answer;
- elapsed time;
- exposed per-session tokens and their source, or `null`;
- all errors and protocol deviations.

Copy [`templates/codex-run.json`](templates/codex-run.json) to `results/` and
complete it without deleting null fields. Use one file per session.

## 7. Classify the run

Mark `success` true only if all success criteria in `methodology.md` hold.
Specifically verify that the assigned interface was used and that the final
answer contains both `8` and `411.49`.

Do not repair the output, edit the transcript, or discard failed runs. Review
all artifacts for sensitive local information before publication.
