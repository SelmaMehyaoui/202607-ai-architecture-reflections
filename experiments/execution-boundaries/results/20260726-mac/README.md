# Published results - 26 July 2026, Mac

This directory is the reviewed evidence snapshot supporting the root report
[`20260726-RESULTS.html`](../../../../20260726-RESULTS.html).

## Run identity

- Date: 26 July 2026
- Environment ID: `Darwin-arm64-py3.14.6`
- Host: macOS 26.5.2, Apple Silicon (`arm64`)
- Python: 3.14.6
- MCP SDK: 1.28.1
- Colima: 0.10.3, macOS Virtualization.Framework
- Docker: client 29.6.2, server 29.5.2
- Container user: `experiment` (UID 10001)
- Container limits: 0.5 CPU, 128 MiB memory, read-only root filesystem,
  network disabled

## Published evidence

| File | Contents |
|---|---|
| `20260726_environment.json` | Host, package, Docker, image, and Colima metadata |
| `20260726_latency-skill.csv` | 1 cold and 30 warm skill-process observations |
| `20260726_latency-mcp-local.csv` | 1 cold and 30 warm local-MCP observations |
| `20260726_latency-mcp-isolated.csv` | 1 cold and 30 warm isolated-MCP observations |
| `20260726_permissions.csv` | 10 capability observations per architecture |
| `SHA256SUMS` | Checksums for the five evidence files |

All 93 latency observations completed successfully. Warm p95 values in the
HTML report use the nearest-rank definition.

## Provenance and review

The files were copied from the generated top-level `results/` outputs after the
end-to-end README workflow and structural checks completed. The generated
top-level files remain ignored and may be overwritten by later runs.

The home-directory prefix in the Colima socket paths was replaced with
`<HOME>`. No timing, capability, runtime, package, image, or configuration value
was otherwise changed. The fixtures contain dummy data only.

Recompute the checksums from this directory with:

```sh
shasum -a 256 20260726_*
```
