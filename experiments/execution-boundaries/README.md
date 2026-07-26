# Execution-boundary experiment

This experiment runs one trivial order summary through three architectures:

```text
agent runtime → SKILL.md → local script
MCP client    → stdio     → local MCP server process
MCP client    → stdio     → narrowly mounted container MCP server
```

The model selects or proposes an action; it does not itself execute Python or
access files. The invoking runtime, local server, or container process performs
the action with the authority granted to that configured boundary.

## Task and fixture

All wrappers call `common/summarize.py`. It reads `common/input/orders.csv` and
computes order count and revenue totals overall and by category. The reviewed
deterministic answer is `common/expected/summary.json`. Security fixtures contain
fake data only.

## Setup and validation

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest

.venv/bin/python experiments/execution-boundaries/skill/scripts/summarize_orders.py \
  --input experiments/execution-boundaries/common/input/orders.csv \
  --output /tmp/orders-summary.json
```

Benchmark one cold and at least 30 warm observations:

```sh
.venv/bin/python experiments/execution-boundaries/benchmarks/benchmark.py skill
.venv/bin/python experiments/execution-boundaries/benchmarks/benchmark.py mcp-local
cd experiments/execution-boundaries
docker build -f mcp-isolated/Dockerfile -t orders-mcp-isolated .
../../.venv/bin/python benchmarks/benchmark.py mcp-isolated
```

The isolated runner mounts only the fixture input directory read-only and a
disposable output directory under `results/` writable to container UID 10001.
Locating that directory in the repository keeps it inside Colima's shared
`/Users` tree; it is removed automatically. The runner requests no network, a
read-only root filesystem, a non-root image user, 0.5 CPU, and 128 MiB memory.
Docker or a compatible Colima runtime must be available and the image built
locally.

Environment and safe host permission observations:

```sh
.venv/bin/python experiments/execution-boundaries/benchmarks/environment.py
.venv/bin/python experiments/execution-boundaries/benchmarks/permission_tests.py
```

The initial permission runner measures a probe process under the same host user;
it does not claim those operations are exposed by the narrow MCP tool schema.
Its reserved invalid-domain network probe records that no connection completed,
not proof that host networking is administratively denied. Container outcomes
remain `not run` until they are observed under Docker.

## Protocol

Use 1–3 cold calls and at least 30 warm calls. Cold MCP observations include
server initialization; warm calls reuse one server session. The skill process
is restarted for every observation, so its “warm” label means warmed OS caches,
not a persistent Python interpreter. This limitation must accompany comparisons.

Measure before interpreting. The hypotheses are that invocation and transport
may add overhead, capability exposure can be narrowed, local MCP is not
automatically isolated, configured isolation matters more than labels, resource
placement can move, and typed calls can improve tool-level observability. None
is a conclusion before results exist.

See [`docs/methodology.md`](../../docs/methodology.md) for reporting rules.
The editable
[`Draw.io overview`](../../docs/ai-architecture-experiments.drawio)
provides a two-page visual summary of the architecture and evidence pipeline.
