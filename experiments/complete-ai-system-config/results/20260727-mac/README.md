# 20260727 macOS Codex results

Status: comparison set 000 complete.

Frozen repository revision:
`ac3bb354a3f37839bd2d9d68ae6732a2da1f0de2`

The deterministic baseline passed with 18 tests. Comparison set 000 is ordered
Skill, local MCP, then isolated MCP.

Published prompt and transcript copies replace the local absolute repository
path with `$REPOSITORY`. No semantic prompt content was changed.

The Skill condition succeeded with the assigned interface, produced the
expected summary, and returned the correct final answer. Its completed run
record and sanitized transcript extract are included in this folder.

The MCP condition also succeeded with its assigned interface and returned the
same deterministic output. Its complete-system token total includes both the
main Codex agent and the automatic guardian review triggered by the MCP action.
This separation is retained in the run record.

The isolated MCP condition also succeeded without fallback. It used the
zero-argument tool inside the constrained container and produced the same
deterministic output. Its automatic guardian activity is recorded separately
and included in the complete-system total.

Before publication:

- complete the Codex-specific fields in `00-environment.json`;
- preserve one run record, transcript, output, and checksum per session;
- confirm personal absolute paths are absent from published artifacts;
- retain failures and protocol deviations;
- generate `SHA256SUMS` only after the evidence set is final.
