# Results

Generated CSV/JSON results are ignored until deliberately reviewed and added.
Do not populate a capability matrix from design assumptions. Record environment
metadata beside each run and distinguish observed outcomes from interpretation.

The documented workflow generates:

```text
environment.json
latency-skill.csv
latency-mcp-local.csv
latency-mcp-isolated.csv
permissions.csv
```

Each latency file must contain one architecture only, with the configured cold
and warm observation counts. `permissions.csv` must identify the process that
performed every probe. A failed network connection is not synonymous with an
administratively denied network capability.
