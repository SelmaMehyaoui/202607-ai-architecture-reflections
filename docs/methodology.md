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
