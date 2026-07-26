# Methodology

This project compares configured execution boundaries, not architecture labels.
The model may propose an action; the agent or MCP client decides whether and how
to request it; the script or MCP server process performs the computation.

## Controlled variable

Every architecture calls the same `common/summarize.py` implementation over the
same CSV fixture. JSON serialization is deterministic. Runs must record the
architecture, cold/warm classification, wall time, business-logic time, success,
timestamp, and environment identifier. Use 1–3 cold observations and at least
30 warm observations. Report median, p95, minimum, and maximum rather than
treating one run as representative.

## Permission observations

Only dummy data and disposable output directories may be probed. Each result
must identify the attempted capability, expected and actual outcome, executing
process, and relevant configuration. A local MCP server running as the same OS
user is a process boundary, not necessarily an authorization boundary.

The isolated configuration mounts only input as read-only and a temporary
output directory as writable. The repository is not mounted, the process runs
as a non-root user, and the benchmark requests no container network. Resource
limits are runner settings because a Dockerfile cannot enforce them.

## Reporting

Keep observations separate from interpretations:

- Observed fact: “This configured container could not see the restricted
  fixture.”
- Interpretation: “Narrow mounts reduced filesystem authority in this run.”

Do not generalize a deployment result into a property of MCP or skills. Record
unavailable metrics and unexecuted probes as limitations; never fabricate them.

## Model–tool composition study

The model–tool composition experiment is methodologically separate from the
execution-boundary benchmark. It varies model class and the allocation of
controlled knowledge/computation in a 2×2 design. Its primary endpoint is
end-to-end task success, not raw model output quality or tool-call validity.

Both model classes receive the same synthetic facts, tasks, and answer criteria.
The direct-context condition supplies those facts in the prompt; the MCP
condition exposes them through a fixed typed interface. Model identity should be
hidden during rubric grading. A non-inferiority margin, repetition count, retry
policy, and uncertainty method must be fixed before comparative results are
collected.

Comparable performance supports only a bounded inference about the tested task
distribution. It does not establish general equivalence between lightweight and
remote models. See
[`experiments/model-tool-composition/methodology.md`](../experiments/model-tool-composition/methodology.md).
