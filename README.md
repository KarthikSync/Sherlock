# Sherlock

> *Sherlock is a local, stateful detective loop that turns repeated telemetry or eval failures into durable cases, appends evidence over time, and notifies humans only when case state changes.*

Sherlock is **not** a monitoring tool, not an autonomous remediation agent, and not an AIOps platform.

## Requirements

- Python ≥ 3.11

## Install

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# Run one detection cycle from a file
sherlock run --input examples/telemetry/run1_new_case.json

# Run from stdin
cat telemetry.json | sherlock run

# Run the four-phase demo
sherlock demo

# Reset demo cases and re-run
sherlock demo --reset
```

## Demo output

```
Run 1
NEW CASE: CASE-0001 high checkout-p95-latency-ms

Run 2
(no human-visible transitions; evidence appended to CASE-0001)

Run 3
SEVERITY CHANGED: CASE-0001 high -> critical

Run 4
RESOLVED: CASE-0001 checkout-p95-latency-ms
```

## Case files

Cases are stored as human-readable markdown in `memory/cases/CASE-NNNN-<slug>.md`.
Each file has YAML frontmatter tracking status, severity, and timestamps, plus
append-only evidence and decision logs.

## LLM summarization (optional)

By default Sherlock runs fully deterministic with no LLM calls. To enable
AI-generated hypothesis text on new case files, install the LLM extra and
set your [OpenRouter](https://openrouter.ai) API key:

```bash
pip install -e ".[llm]"
export OPENROUTER_API_KEY=sk-or-...
sherlock run --input telemetry.json --summarize
```

To pick a specific model (defaults to `openai/gpt-4o-mini`):

```bash
export OPENROUTER_MODEL=anthropic/claude-3-haiku
sherlock run --input telemetry.json --summarize
```

OpenRouter gives access to models from OpenAI, Anthropic, Mistral, and
others through a single key — useful for community testing without
committing to a specific provider.

If `OPENROUTER_API_KEY` is absent or the call fails, Sherlock logs a
warning to stderr and continues without summarization — it is never a
hard failure.

## Running tests

```bash
pytest tests/
```

## Future work

Pluggable detectors, telemetry adapters (Prometheus, OTEL), notification adapters (Slack, PagerDuty), and tracker adapters (GitHub Issues, Jira).

## License

Apache 2.0
