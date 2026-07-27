# Set 000 - isolated MCP transcript extract

This is a publication-oriented extract from Codex session
`019fa453-533b-7412-8a17-58a8fbb92742`. Personal absolute paths are replaced
with `$REPOSITORY`. Encrypted reasoning and general system instructions are not
published.

## Recorded configuration

- Source: VS Code Codex extension
- Model: `gpt-5.6-sol`
- Reasoning effort: `low`, displayed as Light
- Repository commit: `ac3bb354a3f37839bd2d9d68ae6732a2da1f0de2`
- MCP server: `ai-architecture-orders-isolated`
- Container image ID:
  `sha256:836f2a783568c29680a917be6672abe320796d6874eb4a354e725bbedebd42fd`
- Task started: `2026-07-27T16:05:52.323Z`
- Task completed: `2026-07-27T16:06:08.851Z`
- Duration: `16,595 ms`
- Time to first token: `3,829 ms`

## User prompt

```text
You are participating in a controlled architecture experiment.

Assigned interface: isolated MCP

Summarize the controlled order CSV using the registered
`ai-architecture-orders-isolated` MCP server.

That server has fixed container paths:

- read-only input: `/input/orders.csv`
- writable output: `/output/summary.json`

The host publication output will appear at:
$REPOSITORY/experiments/complete-ai-system-config/results/20260727-mac/03-isolated-output/summary.json

Invoke exactly the zero-argument `summarize_orders` tool exposed by
`ai-architecture-orders-isolated`.

Do not use the local MCP server, the Skill script, a terminal command, or direct
calculation. After the MCP action succeeds, report the total number of orders
and total revenue concisely.
```

## Observable action sequence

1. Codex searched for the zero-argument tool on the assigned isolated server.
2. Codex invoked `ai-architecture-orders-isolated/summarize_orders` once with
   `{}`.
3. An automatic guardian model reviewed and allowed the action.
4. The container MCP server returned structured content and wrote the expected
   JSON through its dedicated output mount.
5. No terminal command, local MCP call, Skill invocation, or user-facing
   permission prompt was observed.

The MCP event reported 27.720750 ms for the tool invocation. The server
reported:

```json
{
  "business_logic_ns": 5395418,
  "server_duration_ns": 7420157
}
```

The interval from function call to returned result was approximately 6,350 ms
and includes the automatic guardian review. It is not container-server
execution time.

## Final answer

> Total orders: **8**
>
> Total revenue: **411.49**

## Final token events

Main Codex agent:

```json
{
  "input_tokens": 57842,
  "cached_input_tokens": 36352,
  "output_tokens": 116,
  "reasoning_output_tokens": 15,
  "total_tokens": 57958
}
```

Automatic guardian:

```json
{
  "input_tokens": 4693,
  "cached_input_tokens": 3584,
  "output_tokens": 77,
  "reasoning_output_tokens": 59,
  "total_tokens": 4770
}
```

Complete-system total: `62,728` tokens. Cached input tokens are included in
input and total tokens. The guardian cost is kept separate as well as included
in the complete-system total.
