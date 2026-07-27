You are participating in a controlled architecture experiment.

Assigned interface: [CONDITION]

Summarize the order CSV at:
[INPUT_PATH]

Write the deterministic JSON summary to:
[OUTPUT_PATH]

Use exactly the assigned interface:

- For the Skill condition, explicitly follow the provided order-summary
  SKILL.md and invoke its declared script. Do not use MCP.
- For the MCP condition, invoke the registered `summarize_orders` MCP tool. Do
  not run the Skill script or calculate the CSV directly.

Do not use another execution path and do not calculate the totals yourself.
After the action succeeds, report the total number of orders and total revenue
concisely.
