from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


_SEVERITY_THRESHOLDS = [
    (2.0, "critical"),
    (1.5, "high"),
    (1.0, "medium"),
]


def compute_severity(value: float, threshold: float) -> str | None:
    if threshold <= 0:
        raise ValueError(f"threshold must be > 0, got {threshold}")
    ratio = value / threshold
    if ratio <= 1.0:
        return None
    for cutoff, label in _SEVERITY_THRESHOLDS:
        if ratio > cutoff:
            return label
    return "medium"


def compute_dedup_signature(record: dict[str, Any]) -> str:
    return f"service={record['service']}|metric={record['metric']}"


def _parse_records(raw: str) -> list[dict[str, Any]]:
    raw = raw.strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return [parsed]
    except json.JSONDecodeError:
        pass
    records = []
    for line in raw.splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def parse_telemetry(source: str | Path | None) -> list[dict[str, Any]]:
    if source is None:
        raw = sys.stdin.read()
    else:
        raw = Path(source).read_text(encoding="utf-8")
    return _parse_records(raw)


def detect(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings = []
    for rec in records:
        severity = compute_severity(rec["value"], rec["threshold"])
        if severity is None:
            continue
        findings.append({
            "service": rec["service"],
            "metric": rec["metric"],
            "value": rec["value"],
            "threshold": rec["threshold"],
            "timestamp": rec["timestamp"],
            "severity": severity,
            "dedup_signature": compute_dedup_signature(rec),
        })
    return findings
