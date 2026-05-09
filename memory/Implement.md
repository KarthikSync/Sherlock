# Implementation Notes

## Module map

- `detector.py` — pure functions: `parse_telemetry`, `compute_severity`, `compute_dedup_signature`, `detect`
- `memory.py` — I/O: `load_cases`, `save_case`, `allocate_case_id`
- `case_matcher.py` — `match_or_create`: indexes open cases by `dedup_signature`
- `transitions.py` — `compute_transitions`, `update_case` (mutates in place)
- `renderer.py` — `format_transition` → stdout line or None
- `cli.py` — Click commands; orchestrates the cycle via `_run_cycle`

## Key invariants

- Dedup signature: `service=<service>|metric=<metric>` (no window field in MVP)
- Case IDs allocated by scanning existing files + in-batch offset counter
- Evidence log: newest entry at top, under `## Evidence log` heading
- `_body` and `_path` are private dict keys, filtered before YAML serialization
- `sherlock run` stdout: ONLY transition lines; all diagnostics → stderr

## YAML frontmatter key order

case_id, slug, status, severity, first_seen, last_seen, last_severity_change,
resolved_at, resolution_reason, dedup_signature, hypothesis
