# Methodology

## Unit of analysis

The unit of analysis is an end-to-end system response to a controlled task, not
an isolated model completion or a valid tool call.

A response succeeds only when it exhibits the behavior required by the task:

- tool tasks: correct tool selection, valid arguments, correct final answer, and
  no unsupported claims;
- clarification tasks: an appropriate clarification and no premature tool call;
- abstention tasks: no irrelevant domain-tool call and a suitable response.

## Independent variables

1. Model class:
   - lightweight local model;
   - remote reference model.
2. knowledge/computation allocation:
   - direct context;
   - MCP-assisted.
3. task level:
   - direct mapping;
   - paraphrase;
   - parameter extraction;
   - multi-tool composition;
   - ambiguity handling;
   - error recovery;
   - abstention.

All four model/condition combinations use the same task wording, synthetic
facts, grading rubric, and answer criteria. Client-specific protocol formatting
must be documented.

## Primary endpoint

The primary endpoint is end-to-end task-success rate. Before collection, define
a non-inferiority margin. A possible pilot margin is five percentage points,
but it must be justified against the intended application rather than selected
after viewing results.

The primary contrast is:

```text
local model + MCP minus remote model + MCP
```

The direct-context contrasts show whether MCP composition changes the model
capability gap. Report uncertainty intervals and task-level outcomes. The
included evaluator produces descriptive counts and rates only; inferential
analysis should be added after sample size and repetition policy are fixed.

## Repetitions and randomness

Use deterministic decoding where supported, but do not assume it eliminates
provider or runtime nondeterminism. Pre-register:

- number of independent repetitions;
- task order randomization;
- retry policy;
- timeout policy;
- treatment of malformed tool calls;
- treatment of provider safety refusals and infrastructure failures.

Do not silently retry only one model class.

## Interface-quality controls

The MCP interface is fixed before comparative runs. Its tools must have narrow
semantics, typed parameters, deterministic implementations, structured outputs,
and actionable errors. Both model classes receive the identical tool schema.
Do not tune descriptions against one model after comparative results are known.

## Blinding and grading

Where human judgment is required, graders should not see model identity or
condition. Preserve raw requests, tool traces, tool results, and final responses
under opaque run identifiers. Record rubric components separately; do not ask a
grader for an overall impression of model quality.

## Secondary endpoints

- correct tool selection;
- argument validity;
- clarification and abstention behavior;
- structured-error recovery;
- unsupported-claim rate;
- tool calls and model turns;
- end-to-end, inference, and tool latency;
- local CPU/GPU and memory placement;
- remote tokens and estimated monetary cost;
- information transmitted outside the machine.

Local execution does not by itself guarantee privacy. Report actual network and
logging configuration.

## Interpretation

Comparable MCP-assisted performance would support a bounded claim: architectural
specialization reduced the general model capability required for this task
distribution. It would not establish general model equivalence.

A narrowing gap only on simple tasks would identify an operating region for the
translation-layer architecture. A persistent gap, or a gap that reappears under
ambiguity and composition, is equally informative.
