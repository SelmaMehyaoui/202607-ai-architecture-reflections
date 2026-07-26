# Execution-boundary experiment

This experiment runs one trivial order summary through three architectures:

```text
agent runtime → SKILL.md → local script
MCP client    → stdio     → local MCP server process
MCP client    → stdio     → narrowly mounted container MCP server
```

When following a `SKILL.md`, the model may decide that a bundled Python script
should be run and generate the invocation. The agent runtime actually launches
the script, and the resulting Python process executes with the permissions
granted to that runtime. Similarly, for MCP, the model may select a tool and
generate its arguments, while the local server or container process performs
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
```

For isolated execution, first verify a Docker-compatible engine. With Colima:

```sh
colima start --cpu 2 --memory 2
docker context show
docker info
```

Then build and benchmark from the experiment directory:

```sh
cd experiments/execution-boundaries
docker build -f mcp-isolated/Dockerfile -t orders-mcp-isolated .
../../.venv/bin/python benchmarks/benchmark.py mcp-isolated
cd ../..
```

The three commands write separate files:

```text
results/latency-skill.csv
results/latency-mcp-local.csv
results/latency-mcp-isolated.csv
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

The environment command persists `results/environment.json`, including host,
package, active Docker context, Docker server, isolated-image, and Colima
metadata where available.

The permission runner measures host OS authority using a dedicated probe process
under the same user for the skill and local-MCP configurations; it does not
claim those operations are exposed by the narrow MCP tool schema. It then runs a
fixed probe program inside the actual restricted container and records those
outcomes separately. Network connection failures include their error details
and are not treated as proof of administrative denial unless the runtime
configuration (such as `--network none`) supplies that context.

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
provides a three-page visual summary of both experiments, their architectures,
and their evidence pipelines.
