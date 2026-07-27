# Results

Primary Codex run records and optional API-harness outputs are ignored until
reviewed. For a Codex run, copy `../templates/codex-run.json` once per fresh
session and preserve its prompt, transcript, action trace, and output digest.
Do not replace unavailable token counts with estimates.

An API-harness snapshot must include:

- exact endpoint type and model identifier;
- model checksum and quantization where available;
- model-runner and tokenizer information;
- complete prompt and tool-schema revision;
- all success and failure rows;
- raw traces with secrets and personal paths removed;
- token-usage limitations;
- environment metadata and checksums.
