from __future__ import annotations

from typing import Any


def compute_transitions(
    case: dict[str, Any],
    finding: dict[str, Any] | None,
    is_new: bool,
) -> list[dict[str, Any]]:
    if is_new:
        return [{"type": "new_case", "case_id": case["case_id"],
                 "slug": case["slug"], "severity": case["severity"]}]

    if finding is None:
        if case.get("status") == "open":
            return [{"type": "resolved", "case_id": case["case_id"], "slug": case["slug"]}]
        return []

    if case.get("severity") != finding["severity"]:
        return [{"type": "severity_changed", "case_id": case["case_id"],
                 "slug": case["slug"], "old_severity": case["severity"],
                 "new_severity": finding["severity"]}]

    return [{"type": "steady_state", "case_id": case["case_id"]}]


def _prepend_after_heading(body: str, heading: str, line: str) -> str:
    marker = f"{heading}\n"
    idx = body.find(marker)
    if idx == -1:
        return body + f"\n{heading}\n\n{line}"
    insert_at = idx + len(marker)
    # Skip one blank line after heading if present
    if body[insert_at:insert_at + 1] == "\n":
        insert_at += 1
    return body[:insert_at] + line + body[insert_at:]


def update_case(
    case: dict[str, Any],
    finding: dict[str, Any] | None,
    is_new: bool,
    timestamp: str,
    recovery_record: dict[str, Any] | None = None,
) -> None:
    if finding is not None:
        if not is_new:
            old_severity = case["severity"]
            case["last_seen"] = timestamp
            if finding["severity"] != old_severity:
                case["severity"] = finding["severity"]
                case["last_severity_change"] = timestamp
        evidence_line = (
            f"- {timestamp} — {finding['metric']} {finding['value']}, "
            f"threshold {finding['threshold']}.\n"
        )
        case["_body"] = _prepend_after_heading(case["_body"], "## Evidence log", evidence_line)
    else:
        # Append recovery observation to evidence log if the raw record is available
        if recovery_record is not None:
            rec_line = (
                f"- {timestamp} — {recovery_record['metric']} {recovery_record['value']}, "
                f"threshold {recovery_record['threshold']} (recovered).\n"
            )
            case["_body"] = _prepend_after_heading(case["_body"], "## Evidence log", rec_line)
        case["status"] = "resolved"
        case["resolved_at"] = timestamp
        case["resolution_reason"] = "metric recovered below threshold"
        decision_line = f"- {timestamp} — case resolved: metric recovered below threshold.\n"
        case["_body"] = _prepend_after_heading(case["_body"], "## Decision log", decision_line)
