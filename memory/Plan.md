# Plan

## Active investigations

(none — add entries here when tracking specific anomalies)

## Detection cycle

Each `sherlock run` invocation:

1. Parse telemetry input (file or stdin): single JSON object, array, or JSONL.
2. For each record: compute severity (value/threshold ratio). Drop records at or below threshold.
3. For each finding: compute dedup signature (`service=<s>|metric=<m>`).
4. Load all open cases from `memory/cases/`.
5. Match each finding to an open case by signature, or create a new case.
6. For open cases with no matching finding this cycle: resolve them.
7. Compute transitions: new_case / severity_changed / resolved / steady_state.
8. Update case file: append evidence (newest first), update mutable YAML fields, save.
9. Print one stdout line per meaningful transition. Steady state = silent.
