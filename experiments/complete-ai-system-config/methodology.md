# Methodology

## Two studies, not one pooled benchmark

The primary study uses Codex itself as the model and agent under test. The
optional API-driven extension uses `run_benchmark.py` with a separately hosted
model. Keep their result sets, labels, and interpretations separate.

## Primary Codex comparison

For one pinned Codex configuration, compare Skill, local MCP, and isolated MCP
conditions on:

1. end-to-end task success;
2. correct use of the designated action interface;
3. final-answer correctness;
4. externally observed elapsed time;
5. token consumption, only when exposed for the isolated session.

The experimental unit is one fresh Codex session performing one condition.
Group the three conditions into a comparison set and rotate their order across
repetitions.

## Success criteria

A run succeeds when:

- the agent uses only the interface assigned to the session;
- the action receives the controlled input and output paths;
- the real executor writes the expected deterministic summary;
- the final response reports 8 orders and total revenue 411.49;
- no unplanned calculation or fallback interface is used.

Failures remain in the result set. Do not silently retry. A repeated attempt is
a new run linked to the failed run.

## Isolation

Use fresh sessions because conversation history is part of the model input.
Record the Codex surface, model, reasoning setting, application or CLI version,
repository commit, permission mode, condition, and position within the set.

The repository contains artifacts for all three conditions. This protocol is
behavioral isolation, not a claim of filesystem isolation. The operator assigns
one interface and the transcript is reviewed for violations. A stronger future
variant may use separate worktrees that expose only the assigned artifacts.

## Timing

When measuring wall time, an external observer starts immediately before
submitting the controlled prompt and stops when the final answer is visible.
Record tool execution time separately when the invoked implementation reports
it.

Codex UI latency, scheduling, permission approval time, MCP startup, Python
startup, and operator delay can all influence end-to-end time. Record permission
prompts and unusual delays rather than removing them after the fact.

## Tokens

Use only a per-session token count explicitly exposed by the Codex surface or
an official exported trace. Record the measurement source. If no such count is
available, store `null` and `"unavailable"`.

Do not derive tokens from MCP bytes, terminal output, character or word counts,
a tokenizer for a guessed model, or the API-extension harness. Consequently, a
Codex run without exposed usage can support latency and reliability findings
but not a token-efficiency claim.

## Repetition and analysis

Use at least 10 three-session comparison sets for a pilot. Report the success count for
each condition and preserve every failed run. For elapsed time, report median,
p95, minimum, and maximum with the number of observations. Treat first-use
startup effects as observed data and label session position.

Do not claim one model or interface is faster from a single run. Cross-model
claims require repeating the same frozen protocol with pinned model identities.

## API-driven extension

The optional harness uses two model turns in both conditions. It requires one
native function call, executes the real Skill script or MCP tool, normalizes
the deterministic result, and asks the model for a final answer.

Provider-reported usage is summed across both turns. Network inference time,
tool time, and end-to-end time remain separate. The Skill text and MCP schema
are different context representations, so their token difference is a property
of the complete configurations, not isolated MCP protocol overhead.

## Security and publication

- Use only dummy data and disposable output paths.
- Do not expose a general shell tool for the API extension.
- Never store API-key values.
- Review transcripts and traces before committing them.
- Record protocol deviations rather than rewriting history.
