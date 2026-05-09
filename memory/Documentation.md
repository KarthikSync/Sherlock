# Documentation

## CLI reference

```
sherlock run [--input PATH] [--no-llm] [--summarize]
```

Run one detection cycle. Reads from PATH or stdin.
`--no-llm` and `--summarize` are accepted but no-op in v1.0.

```
sherlock demo [--reset]
```

Run the four-phase demo scenario. Refuses if `memory/cases/` contains existing files.
`--reset` clears existing case files before running.

## Case file location

`memory/cases/CASE-NNNN-<slug>.md`

## Transition stdout format

| Event           | Output                                       |
|-----------------|----------------------------------------------|
| New case        | `NEW CASE: CASE-NNNN <severity> <slug>`      |
| Severity change | `SEVERITY CHANGED: CASE-NNNN <old> -> <new>` |
| Resolved        | `RESOLVED: CASE-NNNN <slug>`                 |
| Steady state    | *(silent)*                                   |

## Telemetry input schema

```json
{
  "service":   "string",
  "metric":    "string",
  "value":     "number",
  "threshold": "number",
  "timestamp": "ISO-8601 UTC string"
}
```

Input may be a single JSON object, a JSON array, or newline-delimited JSON (JSONL).
