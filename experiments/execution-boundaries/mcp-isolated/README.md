# Isolated server

Build from the experiment directory:

```sh
docker build -f mcp-isolated/Dockerfile -t orders-mcp-isolated .
```

The benchmark runner starts it with `/input` read-only, a disposable `/output`
mount, `--network none`, `--read-only`, a temporary `/tmp`, 0.5 CPU, and 128 MiB
memory. Those are properties of the run command, not of MCP or the image.
