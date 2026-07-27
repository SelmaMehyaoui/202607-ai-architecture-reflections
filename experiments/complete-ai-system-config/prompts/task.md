You are participating in a controlled architecture experiment.

Assigned interface: [CONDITION]

Summarize the order CSV at:
[INPUT_PATH]

Write the deterministic JSON summary to:
[OUTPUT_PATH]

Use exactly the assigned interface:

- For the Skill condition, explicitly follow the provided order-summary
  SKILL.md and invoke its declared script. Do not use MCP.
- For the local MCP condition, invoke the registered local `summarize_orders`
  MCP tool. Do not run the Skill script or calculate the CSV directly.
- For the isolated MCP condition, invoke the zero-argument `summarize_orders`
  tool from the registered isolated container server. Do not use the local MCP
  server, Skill script, terminal, or direct calculation.

Do not use another execution path and do not calculate the totals yourself.
After the action succeeds, report the total number of orders and total revenue
concisely.
