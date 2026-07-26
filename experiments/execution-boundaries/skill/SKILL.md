# Summarize orders

Use this skill only when asked to summarize the experiment's order CSV.

Invoke `scripts/summarize_orders.py` with explicit `--input` and `--output`
paths. Do not infer, enumerate, or broaden either path. Report the returned
timing metadata and any non-zero exit status. Compare the produced JSON with
`../common/expected/summary.json` when validation is requested.

The Markdown file grants no runtime authority. The script process inherits the
filesystem, environment, subprocess, and network authority of the agent runtime
that invokes it.
